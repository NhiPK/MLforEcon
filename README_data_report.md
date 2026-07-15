## 1. Suggested repo layout

```
your-repo/
├── data/
│   └── A_FirmData.csv              # raw data, gitignored (see below)
├── src/
│   └── generate_data_report.py     # the script
├── reports/
│   ├── firmdata_report.md          # <-- generated output, committed
│   └── figures/                    # <-- generated PNGs, committed
├── requirements.txt
└── .gitignore
```

## 2. `.gitignore`

The raw CSV is large (~1.7M rows) and is not something you want to check into
git. Add this to `.gitignore`:

```
data/*.csv
data/*.xlsx
__pycache__/
*.pyc
```

Commit the **generated** `reports/firmdata_report.md` and `reports/figures/`
though — that's the whole point, so teammates can see the data state on
GitHub without running anything.

## 3. `requirements.txt`

```
pandas>=2.0
numpy
matplotlib
tabulate      # needed for df.to_markdown()
```

## 4. Running it

```bash
python src/generate_data_report.py --input data/A_FirmData.csv --outdir reports/
```

This will:
- Load the CSV with explicit dtypes (faster + safer than letting pandas guess
  on a 1.7M-row file).
- Write `reports/firmdata_report.md` with:
  1. Overview (shape, firm count, year range, duplicate check, memory)
  2. Full variable schema with descriptions (pulled from
     `A_FirmData_description.txt`) and missingness
  3. Panel structure (firms per year, obs per firm) + a bar chart
  4. Firm characteristics (legal form, top industries, employee coverage)
  5. Descriptive statistics for all balance-sheet variables (with a basic
     negative-value sanity check on items that should be ≥ 0)
  6. Outcome variable (`ncliGrowthNextYear`) distribution + histogram
  7. A small correlation heatmap of key variables vs. the outcome
- Save all figures as PNGs under `reports/figures/`, referenced via relative
  markdown image links (renders natively on GitHub).

## 5. Re-running after data updates

Just re-run the same command — the script always overwrites
`firmdata_report.md` and the figures, so there's a single source of truth.
Consider adding it as a `make report` target or a pre-commit/CI step if you
want it to always stay in sync with the current data.

## 6. Extending it

A few things you'll likely want to add as your project moves into feature
engineering:
- A section on `ncliGrowthThisYear` (lagged outcome / momentum) once you
  build it, since the slides show it's not a strong predictor and it's worth
  tracking why.
- A join-coverage check once you merge in `B_MacroConfidenceData.csv` (i.e.
  what % of firm-years get a non-missing macro match).
- Winsorization / outlier flags on the balance-sheet levels before feeding
  them into linear models (tree-based models are robust to this, OLS is not).

## 7. Note on the sample file

I tested the script against `sample_firm_data.xlsx` (converted to CSV) and it
runs cleanly end-to-end — the column names, dtypes, and missingness patterns
in your sample match `A_FirmData_description.txt` exactly. On the real
1.7M-row file, expect the run to take a minute or two and the plots to look
like smooth distributions rather than the sparse bars you'll see in a 25-row
test.
