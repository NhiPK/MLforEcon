"""
generate_data_report.py

Generates a self-contained Markdown report with descriptive statistics for the
German firm-level panel (A_FirmData.csv). Intended to be run as a repeatable
step in the ML-for-Economists term paper pipeline, and to be checked into
GitHub so co-authors / graders can see the state of the data without opening
a notebook.

Usage
-----
    python generate_data_report.py \
        --input data/A_FirmData.csv \
        --outdir reports/

Outputs
-------
    reports/firmdata_report.md      <- the report itself
    reports/figures/*.png           <- plots referenced from the report

Notes
-----
- Designed to run on the FULL csv (~1.7M rows). Uses explicit dtypes so it
  doesn't need to guess column types, which is both faster and safer.
- No look-ahead / leakage risk here: this script only *describes* the data,
  it does not build model features.
"""

import argparse
import os
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # no display needed, just save PNGs
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# 0. Variable dictionary (from A_FirmData_description.txt)
#    Keeping this here means the report is self-documenting even if a reader
#    never opens the .txt file.
# --------------------------------------------------------------------------
VAR_DESC = {
    "idnr": "BvD unique firm identifier",
    "name": "Company name",
    "type": "Legal form / company type (raw from BvD)",
    "dateinc": "Date of incorporation",
    "naics_core_code": "NAICS industry code (primary activity)",
    "closdate_year": "Fiscal year",
    "empl": "Number of employees",
    "ncliGrowthNextYear": "One-year-ahead growth in non-current liabilities (outcome)",
    "fias": "Fixed assets (total)",
    "ifas": "Intangible fixed assets",
    "tfas": "Tangible fixed assets",
    "ofas": "Other fixed assets",
    "cuas": "Current assets (total)",
    "stok": "Stocks / inventories",
    "debt": "Debtors / accounts receivable",
    "ocas": "Other current assets",
    "cash": "Cash and cash equivalents",
    "toas": "Total assets",
    "shfd": "Shareholders' funds (total equity)",
    "capi": "Capital (subscribed / paid-in)",
    "osfd": "Other shareholders' funds",
    "ncli": "Non-current liabilities (total)",
    "ltdb": "Long-term debt (within non-current liabilities)",
    "oncl": "Other non-current liabilities",
    "prov": "Provisions",
    "culi": "Current liabilities (total)",
    "loan": "Loans (short-term, within current liabilities)",
    "cred": "Creditors / accounts payable",
    "ocli": "Other current liabilities",
    "tshf": "Total shareholders' funds and liabilities",
    "wkca": "Working capital",
}

# Columns expected to be in thousands of EUR (per description.txt note 3)
MONETARY_COLS = [
    "fias", "ifas", "tfas", "ofas", "cuas", "stok", "debt", "ocas", "cash",
    "toas", "shfd", "capi", "osfd", "ncli", "ltdb", "oncl", "prov", "culi",
    "loan", "cred", "ocli", "tshf", "wkca",
]

DTYPES = {
    "idnr": "string",
    "name": "string",
    "type": "string",
    "naics_core_code": "Int64",
    "closdate_year": "Int64",
    "empl": "float64",
    "ncliGrowthNextYear": "float64",
    **{c: "float64" for c in MONETARY_COLS},
}


# --------------------------------------------------------------------------
# 1. Loading
# --------------------------------------------------------------------------
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        dtype=DTYPES,
        parse_dates=["dateinc"],
        low_memory=False,
    )
    return df


# --------------------------------------------------------------------------
# 2. Section builders — each returns a markdown string
# --------------------------------------------------------------------------
def section_overview(df: pd.DataFrame, source_path: str) -> str:
    n_rows, n_cols = df.shape
    n_firms = df["idnr"].nunique()
    year_min, year_max = int(df["closdate_year"].min()), int(df["closdate_year"].max())
    mem_mb = df.memory_usage(deep=True).sum() / 1e6
    dup_rows = df.duplicated(subset=["idnr", "closdate_year"]).sum()

    lines = [
        "## 1. Overview",
        "",
        f"- **Source file:** `{os.path.basename(source_path)}`",
        f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- **Rows (firm-years):** {n_rows:,}",
        f"- **Columns:** {n_cols}",
        f"- **Unique firms (idnr):** {n_firms:,}",
        f"- **Fiscal years covered:** {year_min}–{year_max}",
        f"- **Duplicate (idnr, closdate_year) pairs:** {dup_rows:,} "
        f"{'⚠️ investigate' if dup_rows else '✅ none'}",
        f"- **In-memory size:** {mem_mb:,.1f} MB",
        "",
        "Unit of observation: one row per firm per fiscal year. All monetary "
        "variables are in **thousands of EUR**. Sample already restricted to "
        "German (DE), EUR-reporting, unconsolidated, December fiscal-year-end "
        "firms; see `A_FirmData_description.txt` for the full construction.",
        "",
    ]
    return "\n".join(lines)


def section_schema(df: pd.DataFrame) -> str:
    rows = []
    n = len(df)
    for col in df.columns:
        miss = df[col].isna().sum()
        rows.append({
            "Variable": col,
            "Description": VAR_DESC.get(col, ""),
            "Dtype": str(df[col].dtype),
            "Missing (n)": miss,
            "Missing (%)": round(100 * miss / n, 2),
            "Unique": df[col].nunique(dropna=True),
        })
    schema_df = pd.DataFrame(rows).sort_values("Missing (%)", ascending=False)

    lines = [
        "## 2. Schema & missingness",
        "",
        schema_df.to_markdown(index=False),
        "",
    ]
    return "\n".join(lines)


def section_panel_structure(df: pd.DataFrame, fig_dir: str) -> str:
    per_year = df.groupby("closdate_year")["idnr"].nunique().rename("n_firms")
    obs_per_firm = df.groupby("idnr").size()

    fig, ax = plt.subplots(figsize=(7, 4))
    per_year.plot(kind="bar", ax=ax, color="#4C72B0")
    ax.set_xlabel("Fiscal year")
    ax.set_ylabel("Number of firms")
    ax.set_title("Panel coverage: firms per year")
    fig.tight_layout()
    fig_path = os.path.join(fig_dir, "firms_per_year.png")
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)

    lines = [
        "## 3. Panel structure",
        "",
        f"- **Firm-years per firm:** mean {obs_per_firm.mean():.2f}, "
        f"median {obs_per_firm.median():.0f}, max {obs_per_firm.max():.0f}",
        "",
        "![Firms per year](figures/firms_per_year.png)",
        "",
        "**Firms observed per fiscal year:**",
        "",
        per_year.reset_index().to_markdown(index=False),
        "",
    ]
    return "\n".join(lines)


def section_categoricals(df: pd.DataFrame) -> str:
    type_counts = df["type"].value_counts().rename_axis("type").reset_index(name="n_firm_years")
    top_naics = (
        df["naics_core_code"].value_counts().head(15)
        .rename_axis("naics_core_code").reset_index(name="n_firm_years")
    )

    lines = [
        "## 4. Firm characteristics",
        "",
        "**Legal form (`type`):**",
        "",
        type_counts.to_markdown(index=False),
        "",
        "**Top 15 industries (`naics_core_code`):**",
        "",
        top_naics.to_markdown(index=False),
        "",
        f"**Employees (`empl`):** available for "
        f"{df['empl'].notna().sum():,} / {len(df):,} firm-years "
        f"({100 * df['empl'].notna().mean():.1f}%). "
        f"Median {df['empl'].median():.0f}, mean {df['empl'].mean():.1f}, "
        f"max {df['empl'].max():.0f}.",
        "",
    ]
    return "\n".join(lines)


def section_numeric_summary(df: pd.DataFrame) -> str:
    num_cols = MONETARY_COLS
    desc = df[num_cols].describe(percentiles=[0.01, 0.25, 0.5, 0.75, 0.99]).T
    desc = desc.round(1)
    desc.insert(0, "variable", desc.index)

    # simple sanity flags: negative values in items that should be >= 0
    nonneg_expected = ["fias", "cuas", "toas", "tshf", "culi", "ncli"]
    neg_counts = {c: int((df[c] < 0).sum()) for c in nonneg_expected}
    neg_lines = [f"  - `{c}`: {n} negative values" for c, n in neg_counts.items() if n > 0]

    lines = [
        "## 5. Balance-sheet variables — descriptive statistics",
        "",
        "All figures in thousands of EUR.",
        "",
        desc.to_markdown(index=False),
        "",
    ]
    if neg_lines:
        lines += ["**⚠️ Negative values found in items normally expected ≥ 0:**", ""] + neg_lines + [""]
    else:
        lines += ["No negative values found in items normally expected ≥ 0. ✅", ""]
    return "\n".join(lines)


def section_outcome(df: pd.DataFrame, fig_dir: str) -> str:
    y = df["ncliGrowthNextYear"].dropna()
    stats = y.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(y, bins=60, color="#55A868")
    ax.set_xlabel("ncliGrowthNextYear")
    ax.set_ylabel("count")
    ax.set_title("Outcome distribution")
    fig.tight_layout()
    fig_path = os.path.join(fig_dir, "outcome_distribution.png")
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)

    lines = [
        "## 6. Outcome variable: `ncliGrowthNextYear`",
        "",
        f"- **Non-missing observations:** {y.shape[0]:,} / {len(df):,} "
        f"({100 * y.shape[0] / len(df):.1f}%)",
        f"- **Mean:** {stats['mean']:.4f}   **Std:** {stats['std']:.4f}   "
        f"**Median:** {stats['50%']:.4f}",
        f"- **1st/99th pct:** [{stats['1%']:.3f}, {stats['99%']:.3f}]  "
        f"(range is bounded in (-1, 1) by construction — see description.txt)",
        "",
        "![Outcome distribution](figures/outcome_distribution.png)",
        "",
    ]
    return "\n".join(lines)


def section_outcome_by_year(df: pd.DataFrame, fig_dir: str) -> str:
    sub = df[["closdate_year", "ncliGrowthNextYear"]].dropna()

    # Boxplot by year — shows median, IQR, and outliers per year at a glance
    years = sorted(sub["closdate_year"].unique())
    data_by_year = [sub.loc[sub["closdate_year"] == y, "ncliGrowthNextYear"].values for y in years]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    try:
        ax.boxplot(data_by_year, tick_labels=[str(y) for y in years], showfliers=True,
                   flierprops=dict(marker="o", markersize=2, alpha=0.3))
    except TypeError:  # matplotlib < 3.9 doesn't have tick_labels yet
        ax.boxplot(data_by_year, labels=[str(y) for y in years], showfliers=True,
                   flierprops=dict(marker="o", markersize=2, alpha=0.3))
    ax.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Fiscal year")
    ax.set_ylabel("ncliGrowthNextYear")
    ax.set_title("Outcome distribution by year")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig_path = os.path.join(fig_dir, "outcome_by_year_boxplot.png")
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)

    # Summary table: n, mean, median, std per year
    yearly = sub.groupby("closdate_year")["ncliGrowthNextYear"].agg(
        n="count", mean="mean", median="median", std="std"
    ).round(4).reset_index()

    lines = [
        "## 8. Outcome by year",
        "",
        "Same outcome as Section 6, split by fiscal year. Useful for spotting "
        "regime shifts (e.g. COVID-19) and checking whether the train "
        "(≤2019) and test (2020–2023) periods in an out-of-time split look "
        "meaningfully different.",
        "",
        "![Outcome by year](figures/outcome_by_year_boxplot.png)",
        "",
        yearly.to_markdown(index=False),
        "",
    ]
    return "\n".join(lines)


def section_correlations(df: pd.DataFrame, fig_dir: str) -> str:
    key_vars = ["toas", "ncli", "ltdb", "culi", "shfd", "cash", "ncliGrowthNextYear"]
    corr = df[key_vars].corr()

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(key_vars)))
    ax.set_xticklabels(key_vars, rotation=45, ha="right")
    ax.set_yticks(range(len(key_vars)))
    ax.set_yticklabels(key_vars)
    for i in range(len(key_vars)):
        for j in range(len(key_vars)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Correlation: key balance-sheet vars & outcome")
    fig.tight_layout()
    fig_path = os.path.join(fig_dir, "correlation_heatmap.png")
    fig.savefig(fig_path, dpi=150)
    plt.close(fig)

    lines = [
        "## 9. Correlations (selected variables)",
        "",
        "![Correlation heatmap](figures/correlation_heatmap.png)",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# 3. Main
# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to A_FirmData.csv")
    parser.add_argument("--outdir", default="reports", help="Output directory for the report")
    args = parser.parse_args()

    fig_dir = os.path.join(args.outdir, "figures")
    os.makedirs(fig_dir, exist_ok=True)

    print(f"Loading {args.input} ...")
    df = load_data(args.input)
    print(f"Loaded {len(df):,} rows, {df.shape[1]} columns.")

    parts = [
        "# Firm Data Report — A_FirmData.csv",
        "",
        "_Auto-generated by `generate_data_report.py`. Do not edit by hand — "
        "rerun the script instead._",
        "",
        section_overview(df, args.input),
        section_schema(df),
        section_panel_structure(df, fig_dir),
        section_categoricals(df),
        section_numeric_summary(df),
        section_outcome(df, fig_dir),
        section_outcome_by_year(df, fig_dir),
        section_correlations(df, fig_dir),
    ]

    report_path = os.path.join(args.outdir, "firmdata_report.md")
    with open(report_path, "w") as f:
        f.write("\n".join(parts))

    print(f"Report written to {report_path}")
    print(f"Figures written to {fig_dir}")


if __name__ == "__main__":
    main()