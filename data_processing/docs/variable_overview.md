# Variable Overview: German Firm-Level Panel (`A_FirmData.csv`)

*A plain-language guide to every variable in the dataset — written for readers
with no finance background — plus a proposed set of new variables for model
building.*

---

## 0. The big picture: what is this data, and what is a "balance sheet"?

Each row in this dataset is one **firm in one fiscal year** (a "firm-year").
For each firm-year, we observe a snapshot of that company's **balance
sheet** — a financial statement that answers two questions on a single day
(here: the firm's December year-end):

1. **What does the company own or is owed to it?** → its **assets**
2. **Who has a claim on that value?** → **liabilities** (money owed to
   others: banks, suppliers, tax authorities) and **equity** (the owners'
   own stake)

The fundamental rule of accounting is that these always balance:

```
Assets  =  Liabilities  +  Equity
```

That's why some column names below look redundant (e.g. `toas` and `tshf`
are literally required to be equal) — it's not a data error, it's the
accounting identity holding.

There is **no information here about profit, revenue, or sales** — this
dataset only has balance-sheet (stock/snapshot) variables, not
income-statement (flow-over-a-year) variables. That's a deliberate
restriction (see Section 6 below) driven by what's actually available for
German firms in this data source.

All monetary variables are in **thousands of EUR** (so a value of `1,250`
means €1,250,000).

---

## 1. Identifiers & firm characteristics

| Variable | What it means, in plain terms |
|---|---|
| `idnr` | A unique ID number for the company. Use this to track the *same* firm across different years. |
| `name` | The company's name. |
| `type` | The company's legal form (e.g. GmbH, AG — Germany's equivalents of "Ltd" or "Inc"). Different legal forms have different reporting requirements and ownership structures. |
| `dateinc` | The date the company was legally founded/incorporated. Useful for calculating firm age. |
| `naics_core_code` | A standardized code for what industry the firm is in (e.g. construction, manufacturing, retail). Think of it like a postal code, but for industries instead of places. |
| `closdate_year` | The fiscal (financial reporting) year this row describes. Almost always the calendar year here, since the data is filtered to December year-ends only. |
| `empl` | Number of people employed by the firm. A basic proxy for firm size, alongside total assets. |

---

## 2. The outcome variable (what we're trying to predict)

| Variable | What it means |
|---|---|
| `ncliGrowthNextYear` | **This is the target variable for the whole project.** It measures how much a firm's long-term debts (see `ncli` below) grow from this year to *next* year, as a percentage. A value of `0.10` means non-current liabilities grew 10% next year; `-0.10` means they shrank 10%. |

**Why this variable, and why is it a proxy for "credit demand"?** We can't
directly observe whether a firm *wants* a new loan. But if a firm's
long-term liabilities grow a lot next year, that's a reasonable sign it
took on new long-term financing — which is the closest observable stand-in
for credit demand that this data allows.

It's been pre-processed for you already: it's calculated only when the firm
has two genuinely consecutive fiscal years of data (no gaps), and extreme
values (bigger than a ±100% swing, usually caused by a firm's liabilities
being close to zero the year before) have been removed to avoid distorting
model training.

---

## 3. Assets — "what the company owns"

Assets are grouped into two buckets: things that will stay in the business
long-term (**fixed assets**), and things expected to convert to cash within
a year (**current assets**).

### Fixed assets (long-term holdings)

| Variable | Plain-language meaning |
|---|---|
| `fias` | **Fixed assets, total.** Everything the firm owns for long-term use (not for resale). Equals `ifas + tfas + ofas`. |
| `ifas` | **Intangible fixed assets.** Things with no physical form but real value: patents, trademarks, brand value, goodwill from acquisitions, software licenses. |
| `tfas` | **Tangible fixed assets.** Physical, long-lived stuff: buildings, land, machinery, vehicles, equipment. |
| `ofas` | **Other fixed assets**, including long-term financial investments (e.g. shares the firm holds in *other* companies). |

### Current assets (short-term / liquid holdings)

| Variable | Plain-language meaning |
|---|---|
| `cuas` | **Current assets, total.** Everything expected to be used up or turned into cash within about a year. Equals `stok + debt + ocas + cash`. |
| `stok` | **Stocks / inventory.** Unsold goods sitting in a warehouse, raw materials, or work-in-progress. |
| `debt` | **Debtors / accounts receivable.** Money owed *to* the firm by its customers (they bought something on credit and haven't paid yet). Confusingly named — this is money the firm is owed, not money the firm owes. |
| `ocas` | **Other current assets** not captured above (e.g. prepaid expenses, short-term loans the firm made to others). |
| `cash` | **Cash and cash equivalents.** Actual cash in the bank, or things that convert to cash almost instantly (like money-market funds). |

### Total

| Variable | Plain-language meaning |
|---|---|
| `toas` | **Total assets.** Everything the firm owns: `fias + cuas`. The standard headline measure of firm size. |

---

## 4. Liabilities & Equity — "who has a claim on that value"

### Equity (the owners' stake)

| Variable | Plain-language meaning |
|---|---|
| `shfd` | **Shareholders' funds (equity), total.** The value left over for the owners after every debt is (hypothetically) paid off. Equals `capi + osfd`. |
| `capi` | **Capital.** Money the owners originally put into the company in exchange for their ownership stake. |
| `osfd` | **Other shareholders' funds**, mainly retained earnings — profit from past years that wasn't paid out to owners as dividends, and is instead kept in the business. |

### Non-current liabilities (long-term debts — this is what the outcome variable tracks)

| Variable | Plain-language meaning |
|---|---|
| `ncli` | **Non-current liabilities, total.** Everything the firm owes that is due more than one year from now. Equals `ltdb + oncl`. **This is the variable whose growth we're trying to predict.** |
| `ltdb` | **Long-term debt.** Bank loans, bonds, or other borrowing that doesn't need to be repaid for over a year — the closest thing to "did the firm take out a big loan." |
| `oncl` | **Other non-current liabilities**, including `prov` (see below) and other long-term obligations like pension liabilities. |
| `prov` | **Provisions.** Money set aside for expected future costs that aren't certain yet in amount or timing (e.g. an expected lawsuit payout, warranty repairs, pension commitments). |

### Current liabilities (short-term debts, due within a year)

| Variable | Plain-language meaning |
|---|---|
| `culi` | **Current liabilities, total.** Everything owed and due within about a year. Equals `loan + cred + ocli`. |
| `loan` | **Short-term loans.** Bank borrowing or credit lines due within a year — day-to-day working-capital financing, different in nature from the long-term borrowing in `ltdb`. |
| `cred` | **Creditors / accounts payable.** Money the firm owes to its suppliers for goods/services already received but not yet paid for. |
| `ocli` | **Other current liabilities** not captured above (e.g. taxes owed, short-term accrued expenses). |

### Totals & derived

| Variable | Plain-language meaning |
|---|---|
| `tshf` | **Total shareholders' funds and liabilities.** Equals `shfd + ncli + culi`. By accounting identity, this always equals `toas` — it's the same total pie, sliced by "who has a claim on it" instead of "what form it takes." |
| `wkca` | **Working capital.** Roughly `(stok + debt) - cred` — a measure of the short-term operating cushion a business has, separate from cash and loans. |

---

## 5. Quick mental model

Think of a firm's balance sheet like a household's finances at year-end:

- **Assets** = your house, your car, your savings account, money people owe you
- **Equity** = how much of your house you actually own outright (vs. mortgaged)
- **Non-current liabilities** = your mortgage (long-term debt)
- **Current liabilities** = this month's credit card bill (short-term debt)

The outcome variable, `ncliGrowthNextYear`, is asking: *"did this household's
mortgage balance grow a lot next year?"* — as a proxy for "did they just
take out new long-term borrowing."

---

## 6. Why is there no revenue, profit, or cash-flow data?

Per `A_FirmData_description.txt`, this sample keeps only variables with
**good data coverage** for German, EUR-reporting, unconsolidated firms.
Income-statement items (sales, profit, EBITDA — see the BvD ratios
reference doc for what these normally look like) have too many missing
values in this specific slice of the data to be usable, so they were
dropped. This is a real limitation worth naming explicitly in your report:
we're predicting credit demand using **only balance-sheet composition**,
with no direct view of profitability or sales growth.

---

## 7. Proposed new variables for model building

Raw levels like `toas` or `ncli` mostly reflect firm **size** — a bigger
firm has a bigger everything. The variables below are designed to strip
size out and capture the underlying financial *shape* of a firm, plus
add a time dimension the raw snapshot doesn't have.

### 7.1 Ratios (scale-free — comparable across firms of any size)

| Proposed variable | Formula | What it captures |
|---|---|---|
| `leverage` | `ncli / toas` | What share of the firm is financed by long-term debt, vs. equity or short-term debt. Core "how indebted is this firm" measure. |
| `gearing` | `(ncli + loan) / shfd` | Total borrowing relative to the owners' own stake. High values = firm relies heavily on debt vs. owner capital. |
| `solvency` | `shfd / toas` | The flip side of leverage: what share of the firm is owner-funded. Low solvency = financially fragile. |
| `current_ratio` | `cuas / culi` | Can the firm cover its short-term bills with its short-term assets? Below 1 is a liquidity warning sign. |
| `quick_ratio` | `(cuas - stok) / culi` | Like `current_ratio`, but excludes inventory (which isn't always quickly sellable) — a stricter liquidity check. |
| `cash_ratio` | `cash / toas` | How much of the firm is just sitting in cash — a buffer/flexibility measure. |
| `inventory_share` | `stok / toas` | How inventory-heavy the firm is (relevant for manufacturing/retail vs. services). |
| `receivables_share` | `debt / toas` | How much of the firm's assets are "money owed by customers" rather than tangible value. |
| `working_capital_ratio` | `wkca / toas` | Operating cushion, scaled by firm size. |

### 7.2 Size (log-transformed, to fix skew)

| Proposed variable | Formula | Why |
|---|---|---|
| `log_toas` | `log(toas)` | Total assets are heavily right-skewed (a few huge firms, many small ones); log makes the variable better-behaved for linear models. |
| `log_empl` | `log(empl + 1)` | Same logic for employee count (the `+1` avoids `log(0)` errors for firms with 0 reported). |

### 7.3 Momentum / history (needs firm-year panel structure — built via lags within `idnr`)

| Proposed variable | Formula | Why |
|---|---|---|
| `ncliGrowthThisYear` | This year's realized `ncliGrowthNextYear`, lagged one year | Already shown in the slides' example. Tests whether firms with rising debt keep rising (persistence). |
| `toas_growth` | `(toas(t) - toas(t-1)) / toas(t-1)` | Asset growth — a broader investment-activity signal, not just liabilities. |
| `cash_growth` | Same formula, for `cash` | Change in liquidity buffer year over year. |
| `growth_volatility` | Rolling std. dev. of a firm's own past `ncliGrowthNextYear` values | A simple firm-level "riskiness" proxy — some firms have stable financing needs, others swing wildly. |
| `firm_age` | `closdate_year - year(dateinc)` | Younger vs. mature firms likely have very different financing behavior. |
| `years_in_panel` | Count of prior observations for this `idnr` | A practical control for "new to the sample" firms, which sometimes behave differently (e.g. incomplete history). |

### 7.4 Industry & macro interactions

| Proposed variable | Formula | Why |
|---|---|---|
| `naics_2digit` | First 2 digits of `naics_core_code` | The full code has too many categories to use directly; collapsing to sector level (e.g. "construction," "manufacturing") makes it usable as a model feature. |
| `sector_year_growth` | Mean `ncliGrowthNextYear` by (`naics_2digit`, `closdate_year`), **excluding the firm itself** (leave-one-out, to avoid leakage) | Captures sector-wide credit cycles — is the whole industry borrowing more this year? |
| `sentiment_x_leverage` | `sentiment_index × leverage` | Tests your research question 2 directly: does macro sentiment matter *more* for already-leveraged firms? |
| `sentiment_x_size` | `sentiment_index × log_toas` | Same idea, testing whether sentiment sensitivity differs by firm size (a common SME-finance hypothesis). |

### 7.5 Data-quality features

| Proposed variable | Formula | Why |
|---|---|---|
| `is_na_empl` | 1 if `empl` is missing, else 0 | Missingness itself can be informative (e.g. correlates with firm size/type) rather than just something to drop. |

---

## 8. A caution on all ratio variables

Ratios can explode toward infinity when the denominator is close to zero
(e.g. a firm with `culi ≈ 0`). Rather than dropping those firm-years
entirely, winsorize (cap) each ratio at its 1st/99th percentile — this
keeps the observation in the dataset while preventing a few extreme values
from dominating model training.
