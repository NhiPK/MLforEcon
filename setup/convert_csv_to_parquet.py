"""Convert a large CSV file to Parquet without loading it into pandas."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a large CSV file to compressed Parquet."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--memory-limit",
        default="8GB",
        help="DuckDB memory limit, for example 4GB or 8GB.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=2,
        help="Number of DuckDB threads.",
    )
    parser.add_argument(
        "--temp-dir",
        type=Path,
        default=Path(".duckdb_temp"),
        help="Directory used for temporary files.",
    )
    return parser.parse_args()


def sql_path(path: Path) -> str:
    """Return an absolute path escaped for inclusion in DuckDB SQL."""
    return str(path.resolve()).replace("'", "''")


def main() -> None:
    args = parse_arguments()

    input_path = args.input.resolve()
    output_path = args.output.resolve()
    temp_path = args.temp_dir.resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path == output_path:
        raise ValueError("Input and output paths must be different.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        raise FileExistsError(
            f"Output already exists: {output_path}\n"
            "Delete or rename it before running the conversion again."
        )

    connection = duckdb.connect()

    # Keep DuckDB below the Codespace's total RAM.
    connection.execute(f"SET memory_limit = '{args.memory_limit}'")
    connection.execute(f"SET threads = {args.threads}")

    # Reduces memory requirements when writing a large file.
    connection.execute("SET preserve_insertion_order = false")

    connection.execute(
        f"SET temp_directory = '{sql_path(temp_path)}'"
    )

    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Memory limit: {args.memory_limit}")
    print(f"Threads: {args.threads}")
    print("Starting conversion...")

    connection.execute(
        f"""
        COPY (
            SELECT *
            FROM read_csv(
                '{sql_path(input_path)}',
                header = true,
                sample_size = -1
            )
        )
        TO '{sql_path(output_path)}'
        (
            FORMAT PARQUET,
            COMPRESSION ZSTD,
            ROW_GROUP_SIZE 100000
        )
        """
    )

    connection.close()

    csv_size = input_path.stat().st_size / 1024**3
    parquet_size = output_path.stat().st_size / 1024**3

    print("\nConversion completed.")
    print(f"CSV size:     {csv_size:.2f} GB")
    print(f"Parquet size: {parquet_size:.2f} GB")


if __name__ == "__main__":
    main()