"""
quick_check.py — compact descriptive stats for the final engineered dataset.

Run this and paste the printed output back into chat so we can sanity-check
the data together before moving to modeling.

Usage:
    python quick_check.py --input data/processed/analysis_panel.parquet
    # or, if it's a CSV:
    # python quick_check.py --input data/processed/analysis_panel.csv
"""


import argparse
import pandas as pd

pd.set_option("display.max_columns", 50)
pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 100)


def load(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path, low_memory=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--outcome", default="ncliGrowthNextYear",
                         help="Name of the outcome column, for the correlation check")
    args = parser.parse_args()

    df = load(args.input)

    print("=" * 70)
    print("1. SHAPE & IDENTIFIERS")
    print("=" * 70)
    print(f"Rows: {len(df):,}   Columns: {df.shape[1]}")
    if "idnr" in df.columns:
        print(f"Unique firms: {df['idnr'].nunique():,}")
    if "closdate_year" in df.columns:
        print(f"Fiscal years: {df['closdate_year'].min()}–{df['closdate_year'].max()}")
    if {"idnr", "closdate_year"}.issubset(df.columns):
        dup = df.duplicated(subset=["idnr", "closdate_year"]).sum()
        print(f"Duplicate (idnr, closdate_year) rows: {dup:,}")

    print()
    print("=" * 70)
    print("2. DTYPES")
    print("=" * 70)
    print(df.dtypes)

    print()
    print("=" * 70)
    print("3. MISSINGNESS (sorted, worst first)")
    print("=" * 70)
    miss = df.isna().sum().sort_values(ascending=False)
    miss_pct = (100 * miss / len(df)).round(2)
    miss_tbl = pd.DataFrame({"missing_n": miss, "missing_pct": miss_pct})
    print(miss_tbl[miss_tbl["missing_n"] > 0])

    print()
    print("=" * 70)
    print("4. NUMERIC SUMMARY (all numeric columns)")
    print("=" * 70)
    num_cols = df.select_dtypes(include="number").columns.tolist()
    print(df[num_cols].describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99]).T.round(3))

    print()
    print("=" * 70)
    print("5. INFINITE VALUES CHECK (common after building ratios)")
    print("=" * 70)
    import numpy as np
    inf_counts = {c: int(np.isinf(df[c]).sum()) for c in num_cols if df[c].dtype.kind == "f"}
    inf_counts = {k: v for k, v in inf_counts.items() if v > 0}
    if inf_counts:
        for k, v in inf_counts.items():
            print(f"  ⚠️ {k}: {v} infinite values")
    else:
        print("  ✅ none found")

    print()
    print("=" * 70)
    print("6. CATEGORICAL / LOW-CARDINALITY COLUMNS")
    print("=" * 70)
    cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
    for c in cat_cols:
        n_unique = df[c].nunique(dropna=True)
        print(f"\n--- {c} ({n_unique} unique) ---")
        if n_unique <= 20:
            print(df[c].value_counts(dropna=False).head(20))
        else:
            print(f"  (too many categories to print — showing top 10)")
            print(df[c].value_counts(dropna=False).head(10))

    print()
    print("=" * 70)
    print(f"7. CORRELATION WITH OUTCOME ({args.outcome})")
    print("=" * 70)
    if args.outcome in df.columns:
        corr = (
            df[num_cols].corr()[args.outcome]
            .drop(args.outcome, errors="ignore")
            .sort_values(key=lambda s: s.abs(), ascending=False)
        )
        print(corr.round(3).head(20))
    else:
        print(f"  Column '{args.outcome}' not found — skipping.")

    print()
    print("=" * 70)
    print("8. ZERO / NEGATIVE DENOMINATORS (relevant for any ratio features)")
    print("=" * 70)
    denom_candidates = [c for c in ["toas", "shfd", "culi"] if c in df.columns]
    for c in denom_candidates:
        n_zero_or_neg = (df[c] <= 0).sum()
        print(f"  {c} <= 0: {n_zero_or_neg:,} rows")

    print()
    print("Done. Copy everything above and paste it back into chat.")


if __name__ == "__main__":
    main()
