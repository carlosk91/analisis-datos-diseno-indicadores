"""
Generate a reproducible synthetic financial-performance dataset for classroom use.

Run from the course module root:
    python scripts/generate_financial_performance.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)

MODULE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = MODULE_ROOT / "data"
DOCS_DIR = MODULE_ROOT / "docs"

MONTHS = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
BUSINESS_UNITS = ["Consumer", "SMB"]
REGIONS = ["Mexico", "United States", "Colombia"]
CHANNELS = ["Online", "Retail", "Partner"]
REGION_CURRENCY = {
    "Mexico": "MXN",
    "United States": "USD",
    "Colombia": "COP",
}

INCOMPLETE_MONTH = "2025-12"
INCOMPLETE_FACTOR = 18 / 31

# Segment structural multipliers (persistent tendencies, not constants)
BU_DEMAND = {"Consumer": 1.65, "SMB": 0.55}
BU_AOV = {"Consumer": 0.42, "SMB": 2.85}
BU_COGS_ADJ = {"Consumer": 1.04, "SMB": 0.92}
BU_MARKETING_INTENSITY = {"Consumer": 1.18, "SMB": 0.82}

REGION_DEMAND = {"Mexico": 1.45, "United States": 1.05, "Colombia": 0.62}
REGION_GROWTH = {"Mexico": 0.010, "United States": 0.012, "Colombia": 0.022}
REGION_AOV = {"Mexico": 0.78, "United States": 1.35, "Colombia": 0.88}
REGION_PAYROLL_RENT = {"Mexico": 0.82, "United States": 1.28, "Colombia": 0.90}
REGION_TAX_RATE = {"Mexico": 0.28, "United States": 0.24, "Colombia": 0.31}

CHANNEL_DEMAND = {"Online": 1.15, "Retail": 1.00, "Partner": 0.78}
CHANNEL_RENT = {"Online": 0.35, "Retail": 1.55, "Partner": 0.70}
CHANNEL_TECH = {"Online": 1.45, "Retail": 0.75, "Partner": 0.95}
CHANNEL_MARKETING = {"Online": 1.20, "Retail": 0.95, "Partner": 0.62}
CHANNEL_LOGISTICS = {"Online": 0.90, "Retail": 1.05, "Partner": 1.22}

# Deterministic anomaly targets (record_id assigned after skeleton build)
ANOMALY_SPEC = {
    "missing_marketing_expense": [12, 187],
    "missing_cac": [45, 301],
    "large_marketing_expense_record": 98,
    "large_gross_revenue_record": 256,
    "opex_reconciliation_record": 334,
    "impossible_units_sold_record": 412,
    "thousands_reporting_unit_records": [67, 198, 389],
}

TOL = 1e-2


def build_dimensions() -> pd.DataFrame:
    """Create the 432-row segment skeleton with unique composite keys."""
    rows = []
    record_id = 1
    for month in MONTHS:
        for bu in BUSINESS_UNITS:
            for region in REGIONS:
                for channel in CHANNELS:
                    rows.append(
                        {
                            "record_id": record_id,
                            "month": month.strftime("%Y-%m"),
                            "business_unit": bu,
                            "region": region,
                            "channel": channel,
                        }
                    )
                    record_id += 1
    df = pd.DataFrame(rows)
    assert len(df) == 432
    assert df["record_id"].is_unique
    assert df.duplicated(["month", "business_unit", "region", "channel"]).sum() == 0
    return df


def add_period_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Attach calendar boundaries and completeness flags."""
    month_ts = pd.to_datetime(df["month"] + "-01")
    is_incomplete = df["month"] == INCOMPLETE_MONTH

    period_end = month_ts + pd.offsets.MonthEnd(0)
    period_end = period_end.where(~is_incomplete, pd.Timestamp("2025-12-18"))

    df = df.copy()
    df["period_start"] = month_ts.dt.strftime("%Y-%m-%d")
    df["period_end"] = period_end.dt.strftime("%Y-%m-%d")
    df["is_complete_period"] = ~is_incomplete
    return df


def month_index(month_str: str) -> int:
    return (pd.Timestamp(month_str + "-01") - pd.Timestamp("2024-01-01")).days // 30


def seasonality_factor(month_str: str) -> float:
    month = int(month_str.split("-")[1])
    seasonal = {
        1: 0.88,
        2: 0.92,
        3: 0.96,
        4: 1.00,
        5: 1.02,
        6: 1.00,
        7: 0.98,
        8: 1.00,
        9: 1.03,
        10: 1.06,
        11: 1.12,
        12: 1.18,
    }
    return seasonal[month]


def generate_fx_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Attach local currency and gradually drifting MXN conversion rates."""
    df = df.copy()
    df["currency"] = df["region"].map(REGION_CURRENCY)
    t = df["month"].map(month_index).to_numpy()

    fx = np.zeros(len(df))
    for i, row in df.iterrows():
        ti = month_index(row["month"])
        drift = 1.0 + 0.0012 * ti + RNG.normal(0, 0.0008)
        if row["region"] == "Mexico":
            fx[i] = 1.0
        elif row["region"] == "United States":
            fx[i] = 17.0 + 0.055 * ti + RNG.normal(0, 0.08)
        else:
            fx[i] = 0.00415 + 0.000028 * ti + RNG.normal(0, 0.00004)

    df["fx_rate_to_mxn"] = np.maximum(fx, 1e-6)
    df["reporting_unit"] = "units"
    return df


def segment_multiplier(row: pd.Series) -> float:
    return (
        BU_DEMAND[row["business_unit"]]
        * REGION_DEMAND[row["region"]]
        * CHANNEL_DEMAND[row["channel"]]
        * seasonality_factor(row["month"])
    )


def growth_multiplier(row: pd.Series) -> float:
    t = month_index(row["month"])
    base = 1.0 + REGION_GROWTH[row["region"]] * t
    nonlinear = 1.0 + 0.00035 * t**1.35
    return base * nonlinear


def generate_operating_drivers(df: pd.DataFrame) -> pd.DataFrame:
    """Generate customer, transaction, and headcount drivers."""
    df = df.copy()
    active_customers = []
    new_customers = []
    churned_customers = []
    transactions = []
    headcount = []

    for _, row in df.iterrows():
        t = month_index(row["month"])
        base_customers = 420 * segment_multiplier(row) * growth_multiplier(row)
        noise = RNG.normal(1.0, 0.04)
        active = max(base_customers * noise, 25.0)

        churn_rate = 0.038 + 0.0004 * RNG.random()
        churned = max(active * churn_rate * RNG.normal(1.0, 0.08), 1.0)
        new = max(churned * (1.05 + 0.08 * BU_MARKETING_INTENSITY[row["business_unit"]]) * RNG.normal(1.0, 0.07), 1.0)

        txn_per_active = 1.55 + 0.018 * t + RNG.normal(0, 0.06)
        txn = max(active * txn_per_active * RNG.normal(1.0, 0.05), 5.0)

        hc_base = 2.8 * (active / 350.0) ** 0.55
        hc = max(hc_base * REGION_PAYROLL_RENT[row["region"]] * RNG.normal(1.0, 0.05), 0.5)

        active_customers.append(active)
        new_customers.append(new)
        churned_customers.append(churned)
        transactions.append(txn)
        headcount.append(hc)

    df["active_customers"] = active_customers
    df["new_customers"] = new_customers
    df["churned_customers"] = churned_customers
    df["transactions"] = transactions
    df["headcount"] = headcount
    return df


def generate_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Generate revenue stack with accounting identity."""
    df = df.copy()
    gross_revenue = []
    discounts = []
    refunds = []

    for _, row in df.iterrows():
        t = month_index(row["month"])
        aov_local = (
            920
            * BU_AOV[row["business_unit"]]
            * REGION_AOV[row["region"]]
            * (1.0 + 0.004 * t)
            * RNG.normal(1.0, 0.03)
        )
        net_rev = max(row["transactions"] * aov_local, 1.0)

        discount_rate = 0.045 + 0.0015 * CHANNEL_MARKETING[row["channel"]] + RNG.normal(0, 0.003)
        refund_rate = 0.012 + RNG.normal(0, 0.002)
        discount_rate = np.clip(discount_rate, 0.02, 0.09)
        refund_rate = np.clip(refund_rate, 0.005, 0.025)

        discounts_amt = net_rev * discount_rate / (1.0 - discount_rate - refund_rate)
        refunds_amt = net_rev * refund_rate / (1.0 - discount_rate - refund_rate)
        gross = net_rev + discounts_amt + refunds_amt

        gross_revenue.append(gross)
        discounts.append(discounts_amt)
        refunds.append(refunds_amt)

    df["gross_revenue"] = gross_revenue
    df["discounts"] = discounts
    df["refunds"] = refunds
    df["net_revenue"] = df["gross_revenue"] - df["discounts"] - df["refunds"]
    return df


def cogs_ratio(row: pd.Series) -> float:
    """Declining COGS ratio over time -> improving gross margin."""
    t = month_index(row["month"]) / 23.0
    base = 0.545 - 0.065 * t
    adj = BU_COGS_ADJ[row["business_unit"]]
    channel_adj = 1.0 + 0.02 * (CHANNEL_LOGISTICS[row["channel"]] - 1.0)
    ratio = base * adj * channel_adj + RNG.normal(0, 0.008)
    return float(np.clip(ratio, 0.38, 0.62))


def generate_costs(df: pd.DataFrame) -> pd.DataFrame:
    """Generate COGS and operating expense components."""
    df = df.copy()

    cogs = []
    marketing = []
    payroll = []
    rent = []
    technology = []
    logistics = []
    other_opex = []

    for _, row in df.iterrows():
        t = month_index(row["month"])
        ratio = cogs_ratio(row)
        cogs.append(max(row["net_revenue"] * ratio, 0.0))

        mkt_rate = (
            0.086
            + 0.0030 * t
            + 0.012 * (BU_MARKETING_INTENSITY[row["business_unit"]] - 1.0)
            + 0.008 * (CHANNEL_MARKETING[row["channel"]] - 1.0)
        )
        marketing.append(max(row["net_revenue"] * mkt_rate * RNG.normal(1.0, 0.05), 0.0))

        payroll_per_hc = 18500 * REGION_PAYROLL_RENT[row["region"]] * (1.0 + 0.0035 * t)
        payroll.append(max(row["headcount"] * payroll_per_hc * RNG.normal(1.0, 0.04), 0.0))

        rent_base = 4200 * REGION_PAYROLL_RENT[row["region"]] * CHANNEL_RENT[row["channel"]]
        rent.append(max(rent_base * (1.0 + 0.001 * t) * RNG.normal(1.0, 0.03), 0.0))

        tech_rate = 0.0285 + 0.0018 * t
        tech_mult = CHANNEL_TECH[row["channel"]]
        technology.append(max(row["net_revenue"] * tech_rate * tech_mult * RNG.normal(1.0, 0.05), 0.0))

        units = row["transactions"] * RNG.normal(1.15, 0.06)
        logistics_unit_cost = 42 * CHANNEL_LOGISTICS[row["channel"]] * (1.0 + 0.002 * t)
        logistics.append(max(units * logistics_unit_cost * RNG.normal(1.0, 0.05), 0.0))

        other_rate = 0.022 + RNG.normal(0, 0.002)
        other_opex.append(max(row["net_revenue"] * other_rate, 0.0))

    df["cogs"] = cogs
    df["marketing_expense"] = marketing
    df["payroll_expense"] = payroll
    df["rent_expense"] = rent
    df["technology_expense"] = technology
    df["logistics_expense"] = logistics
    df["other_operating_expense"] = other_opex
    df["operating_expenses"] = (
        df["marketing_expense"]
        + df["payroll_expense"]
        + df["rent_expense"]
        + df["technology_expense"]
        + df["logistics_expense"]
        + df["other_operating_expense"]
    )
    return df


def generate_capex_and_depreciation(df: pd.DataFrame) -> pd.DataFrame:
    """CapEx ramps in later months; D&A follows accumulated investment with lag."""
    df = df.copy()
    capex = []
    depreciation = []

    company_capex_by_month: dict[str, float] = {}
    for month in df["month"].unique():
        t = month_index(month)
        ramp = 1.0 + max(0.0, (t - 10) / 12.0) ** 1.6 * 1.55
        company_capex_by_month[month] = 2_350_000 * ramp * RNG.normal(1.0, 0.06)

    accumulated = 0.0
    monthly_dep_base: dict[str, float] = {}
    for month in sorted(company_capex_by_month):
        capex_amt = company_capex_by_month[month]
        accumulated = accumulated * 0.985 + capex_amt
        monthly_dep_base[month] = accumulated * 0.028 + capex_amt * 0.12

    for _, row in df.iterrows():
        month = row["month"]
        share = segment_multiplier(row) * growth_multiplier(row)
        total_share = df.loc[df["month"] == month].apply(
            lambda r: segment_multiplier(r) * growth_multiplier(r), axis=1
        ).sum()
        weight = share / total_share

        seg_capex = company_capex_by_month[month] * weight * RNG.normal(1.0, 0.04)
        seg_dep = monthly_dep_base[month] * weight * RNG.normal(1.0, 0.03)
        capex.append(max(seg_capex, 0.0))
        depreciation.append(max(seg_dep, 0.0))

    df["capital_expenditure"] = capex
    df["depreciation_amortization"] = depreciation
    return df


def calculate_gross_and_ebitda(df: pd.DataFrame) -> pd.DataFrame:
    """Compute gross profit and EBITDA."""
    df = df.copy()
    df["gross_profit"] = df["net_revenue"] - df["cogs"]
    df["ebitda"] = df["gross_profit"] - df["operating_expenses"]
    return df


def calculate_operating_income(df: pd.DataFrame) -> pd.DataFrame:
    """Compute operating income after depreciation."""
    df = df.copy()
    df["operating_income"] = df["ebitda"] - df["depreciation_amortization"]
    return df


def revenue_weights(df: pd.DataFrame, month: str) -> pd.Series:
    """Return within-month revenue allocation weights indexed by dataframe index."""
    month_df = df[df["month"] == month]
    return month_df["net_revenue"] / month_df["net_revenue"].sum()


def generate_balance_sheet_and_financing(df: pd.DataFrame) -> pd.DataFrame:
    """Evolve company balance sheet monthly and allocate stocks to segments."""
    df = df.copy()
    months_sorted = sorted(df["month"].unique())

    debt = 48_000_000.0
    equity = 62_000_000.0
    cash = 9_500_000.0
    other_liabilities = 7_800_000.0

    month_state: dict[str, dict[str, float]] = {}

    for month in months_sorted:
        t = month_index(month)
        month_mask = df["month"] == month
        month_df = df.loc[month_mask]
        weights = revenue_weights(df, month)

        debt = debt * (1.0 + 0.0040 + 0.00028 * t) + month_df["capital_expenditure"].sum() * 0.15
        other_liabilities = other_liabilities * (1.0 + 0.0015) + month_df["net_revenue"].sum() * 0.002
        cash = cash + month_df["ebitda"].sum() * 0.06 - month_df["capital_expenditure"].sum() * 0.08
        cash = max(cash, 4_000_000.0)

        total_liabilities = debt + other_liabilities
        total_assets = total_liabilities + equity
        invested_capital = debt + equity - cash

        month_state[month] = {
            "debt": debt,
            "equity": equity,
            "cash": cash,
            "other_liabilities": other_liabilities,
            "total_liabilities": total_liabilities,
            "total_assets": total_assets,
            "invested_capital": invested_capital,
            "weights": weights,
        }

        # Interest, tax, and net income for this month (segment level)
        annual_rate = 0.083 + 0.0012 * t
        monthly_rate = annual_rate / 12.0
        region_premium = df.loc[month_mask, "region"].map({"Colombia": 0.004, "Mexico": 0.0, "United States": 0.0})
        seg_debt = debt * weights
        seg_interest = seg_debt * (monthly_rate + region_premium / 12.0)
        df.loc[month_mask, "debt"] = seg_debt.values
        df.loc[month_mask, "interest_expense"] = np.maximum(seg_interest.values, 0.0)

        pretax = df.loc[month_mask, "operating_income"] - df.loc[month_mask, "interest_expense"]
        tax_rates = df.loc[month_mask, "region"].map(REGION_TAX_RATE).to_numpy() + RNG.normal(0, 0.008, month_mask.sum())
        tax_rates = np.clip(tax_rates, 0.18, 0.35)
        df.loc[month_mask, "tax_expense"] = np.maximum(pretax.to_numpy(), 0.0) * tax_rates
        df.loc[month_mask, "net_income"] = (
            df.loc[month_mask, "operating_income"]
            - df.loc[month_mask, "interest_expense"]
            - df.loc[month_mask, "tax_expense"]
        )

        month_net_income = df.loc[month_mask, "net_income"].sum()
        retained = max(month_net_income, 0.0) * 0.26
        distributions = max(month_net_income, 0.0) * 0.68
        buybacks = max(month_net_income, 0.0) * 0.12 + month_df["capital_expenditure"].sum() * 0.04
        equity = max(equity + retained - distributions - buybacks, 28_000_000.0)

    for month in months_sorted:
        month_mask = df["month"] == month
        st = month_state[month]
        weights = st["weights"]
        df.loc[month_mask, "cash"] = (st["cash"] * weights).values
        df.loc[month_mask, "other_liabilities"] = (st["other_liabilities"] * weights).values
        df.loc[month_mask, "equity"] = (st["equity"] * weights).values
        df.loc[month_mask, "total_liabilities"] = df.loc[month_mask, "debt"] + df.loc[month_mask, "other_liabilities"]
        df.loc[month_mask, "total_assets"] = df.loc[month_mask, "total_liabilities"] + df.loc[month_mask, "equity"]
        df.loc[month_mask, "invested_capital"] = (
            df.loc[month_mask, "debt"] + df.loc[month_mask, "equity"] - df.loc[month_mask, "cash"]
        )

    return df


def calculate_operational_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Derive units sold, AOV, and CAC from financial/operational drivers."""
    df = df.copy()
    units_sold = []
    for _, row in df.iterrows():
        units_per_txn = 1.35 + 0.08 * (BU_DEMAND[row["business_unit"]] - 1.0)
        units_sold.append(max(row["transactions"] * units_per_txn * RNG.normal(1.0, 0.04), 1.0))
    df["units_sold"] = units_sold

    df["average_order_value"] = np.where(
        df["transactions"] > 0,
        df["net_revenue"] / df["transactions"],
        0.0,
    )
    df["customer_acquisition_cost"] = np.where(
        df["new_customers"] > 0,
        df["marketing_expense"] / df["new_customers"],
        0.0,
    )
    return df


def apply_incomplete_period_scaling(df: pd.DataFrame) -> pd.DataFrame:
    """Scale flow variables for the partial December 2025 period."""
    df = df.copy()
    flow_cols = [
        "gross_revenue",
        "discounts",
        "refunds",
        "net_revenue",
        "cogs",
        "marketing_expense",
        "payroll_expense",
        "rent_expense",
        "technology_expense",
        "logistics_expense",
        "other_operating_expense",
        "operating_expenses",
        "gross_profit",
        "ebitda",
        "capital_expenditure",
        "depreciation_amortization",
        "operating_income",
        "interest_expense",
        "tax_expense",
        "net_income",
        "new_customers",
        "churned_customers",
        "transactions",
        "units_sold",
    ]
    mask = df["month"] == INCOMPLETE_MONTH
    for col in flow_cols:
        df.loc[mask, col] = df.loc[mask, col] * INCOMPLETE_FACTOR

    # Reconcile identities after scaling
    df.loc[mask, "net_revenue"] = (
        df.loc[mask, "gross_revenue"] - df.loc[mask, "discounts"] - df.loc[mask, "refunds"]
    )
    df.loc[mask, "gross_profit"] = df.loc[mask, "net_revenue"] - df.loc[mask, "cogs"]
    df.loc[mask, "operating_expenses"] = (
        df.loc[mask, "marketing_expense"]
        + df.loc[mask, "payroll_expense"]
        + df.loc[mask, "rent_expense"]
        + df.loc[mask, "technology_expense"]
        + df.loc[mask, "logistics_expense"]
        + df.loc[mask, "other_operating_expense"]
    )
    df.loc[mask, "ebitda"] = df.loc[mask, "gross_profit"] - df.loc[mask, "operating_expenses"]
    df.loc[mask, "operating_income"] = (
        df.loc[mask, "ebitda"] - df.loc[mask, "depreciation_amortization"]
    )
    df.loc[mask, "net_income"] = (
        df.loc[mask, "operating_income"]
        - df.loc[mask, "interest_expense"]
        - df.loc[mask, "tax_expense"]
    )
    df.loc[mask, "average_order_value"] = np.where(
        df.loc[mask, "transactions"] > 0,
        df.loc[mask, "net_revenue"] / df.loc[mask, "transactions"],
        0.0,
    )
    df.loc[mask, "customer_acquisition_cost"] = np.where(
        df.loc[mask, "new_customers"] > 0,
        df.loc[mask, "marketing_expense"] / df.loc[mask, "new_customers"],
        0.0,
    )
    return df


MONETARY_COLS = [
    "gross_revenue",
    "discounts",
    "refunds",
    "net_revenue",
    "cogs",
    "marketing_expense",
    "payroll_expense",
    "rent_expense",
    "technology_expense",
    "logistics_expense",
    "other_operating_expense",
    "operating_expenses",
    "gross_profit",
    "ebitda",
    "capital_expenditure",
    "depreciation_amortization",
    "operating_income",
    "interest_expense",
    "tax_expense",
    "net_income",
    "cash",
    "debt",
    "other_liabilities",
    "total_liabilities",
    "equity",
    "total_assets",
    "invested_capital",
]


def apply_thousands_reporting_unit(df: pd.DataFrame, record_ids: list[int]) -> pd.DataFrame:
    """Mark selected rows as thousands and scale monetary values accordingly."""
    df = df.copy()
    mask = df["record_id"].isin(record_ids)
    df.loc[mask, "reporting_unit"] = "thousands"
    for col in MONETARY_COLS:
        df.loc[mask, col] = df.loc[mask, col] / 1_000.0
    return df


def inject_quality_issues(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Inject a small deterministic set of data-quality problems."""
    df = df.copy()
    issues: list[dict] = []

    for rid in ANOMALY_SPEC["missing_marketing_expense"]:
        idx = df.index[df["record_id"] == rid][0]
        df.loc[idx, "marketing_expense"] = np.nan
        issues.append(
            {
                "record_id": rid,
                "column": "marketing_expense",
                "issue_type": "missing_value",
                "description": "Marketing expense intentionally set to null.",
            }
        )

    for rid in ANOMALY_SPEC["missing_cac"]:
        idx = df.index[df["record_id"] == rid][0]
        df.loc[idx, "customer_acquisition_cost"] = np.nan
        issues.append(
            {
                "record_id": rid,
                "column": "customer_acquisition_cost",
                "issue_type": "missing_value",
                "description": "CAC intentionally set to null (marketing/new_customers still present).",
            }
        )

    rid = ANOMALY_SPEC["large_marketing_expense_record"]
    idx = df.index[df["record_id"] == rid][0]
    original = df.loc[idx, "marketing_expense"]
    df.loc[idx, "marketing_expense"] = original * 4.2
    df.loc[idx, "operating_expenses"] = (
        df.loc[idx, "marketing_expense"]
        + df.loc[idx, "payroll_expense"]
        + df.loc[idx, "rent_expense"]
        + df.loc[idx, "technology_expense"]
        + df.loc[idx, "logistics_expense"]
        + df.loc[idx, "other_operating_expense"]
    )
    df.loc[idx, "ebitda"] = df.loc[idx, "gross_profit"] - df.loc[idx, "operating_expenses"]
    df.loc[idx, "operating_income"] = df.loc[idx, "ebitda"] - df.loc[idx, "depreciation_amortization"]
    df.loc[idx, "tax_expense"] = max(
        (df.loc[idx, "operating_income"] - df.loc[idx, "interest_expense"]), 0.0
    ) * REGION_TAX_RATE[df.loc[idx, "region"]]
    df.loc[idx, "net_income"] = (
        df.loc[idx, "operating_income"] - df.loc[idx, "interest_expense"] - df.loc[idx, "tax_expense"]
    )
    issues.append(
        {
            "record_id": rid,
            "column": "marketing_expense",
            "issue_type": "extreme_value",
            "description": "Marketing expense multiplied by 4.2; still technically possible.",
        }
    )

    rid = ANOMALY_SPEC["large_gross_revenue_record"]
    idx = df.index[df["record_id"] == rid][0]
    original = df.loc[idx, "gross_revenue"]
    df.loc[idx, "gross_revenue"] = original * 3.6
    df.loc[idx, "net_revenue"] = df.loc[idx, "gross_revenue"] - df.loc[idx, "discounts"] - df.loc[idx, "refunds"]
    issues.append(
        {
            "record_id": rid,
            "column": "gross_revenue",
            "issue_type": "extreme_value",
            "description": "Gross revenue multiplied by 3.6; downstream profit fields not fully reconciled.",
        }
    )

    rid = ANOMALY_SPEC["opex_reconciliation_record"]
    idx = df.index[df["record_id"] == rid][0]
    df.loc[idx, "operating_expenses"] = df.loc[idx, "operating_expenses"] + df.loc[idx, "rent_expense"] * 0.35
    issues.append(
        {
            "record_id": rid,
            "column": "operating_expenses",
            "issue_type": "reconciliation_error",
            "description": "Operating expenses no longer equal the sum of OPEX components.",
        }
    )

    rid = ANOMALY_SPEC["impossible_units_sold_record"]
    idx = df.index[df["record_id"] == rid][0]
    df.loc[idx, "units_sold"] = -150.0
    issues.append(
        {
            "record_id": rid,
            "column": "units_sold",
            "issue_type": "impossible_value",
            "description": "Units sold set to a negative value.",
        }
    )

    for rid in ANOMALY_SPEC["thousands_reporting_unit_records"]:
        issues.append(
            {
                "record_id": rid,
                "column": "reporting_unit",
                "issue_type": "reporting_unit_thousands",
                "description": "Monetary values divided by 1,000; reporting_unit='thousands'.",
            }
        )

    return df, issues


def anomaly_record_ids() -> set[int]:
    ids = set(ANOMALY_SPEC["missing_marketing_expense"])
    ids.update(ANOMALY_SPEC["missing_cac"])
    ids.add(ANOMALY_SPEC["large_marketing_expense_record"])
    ids.add(ANOMALY_SPEC["large_gross_revenue_record"])
    ids.add(ANOMALY_SPEC["opex_reconciliation_record"])
    ids.add(ANOMALY_SPEC["impossible_units_sold_record"])
    return ids


def validate_dataset(df: pd.DataFrame, issues: list[dict]) -> None:
    """Fail loudly if core structural rules are violated."""
    bad_ids = anomaly_record_ids()

    assert len(df) == 432
    assert df["record_id"].is_unique
    assert df.duplicated(["month", "business_unit", "region", "channel"]).sum() == 0
    assert df.duplicated().sum() == 0

    assert set(df["business_unit"]) == set(BUSINESS_UNITS)
    assert set(df["region"]) == set(REGIONS)
    assert set(df["channel"]) == set(CHANNELS)
    assert set(df["reporting_unit"]) <= {"units", "thousands"}

    for region, currency in REGION_CURRENCY.items():
        assert (df.loc[df["region"] == region, "currency"] == currency).all()

    assert (df["fx_rate_to_mxn"] > 0).all()

    dec = df[df["month"] == INCOMPLETE_MONTH]
    assert (dec["period_start"] == "2025-12-01").all()
    assert (dec["period_end"] == "2025-12-18").all()
    assert (~dec["is_complete_period"]).all()
    complete = df[df["month"] != INCOMPLETE_MONTH]
    assert complete["is_complete_period"].all()

    clean = df[~df["record_id"].isin(bad_ids)]
    revenue_clean = clean[clean["record_id"] != ANOMALY_SPEC["large_gross_revenue_record"]]

    assert np.allclose(
        revenue_clean["net_revenue"],
        revenue_clean["gross_revenue"] - revenue_clean["discounts"] - revenue_clean["refunds"],
        atol=TOL,
        equal_nan=True,
    )
    assert np.allclose(revenue_clean["gross_profit"], revenue_clean["net_revenue"] - revenue_clean["cogs"], atol=TOL)
    assert np.allclose(clean["ebitda"], clean["gross_profit"] - clean["operating_expenses"], atol=TOL)
    assert np.allclose(
        clean["operating_income"],
        clean["ebitda"] - clean["depreciation_amortization"],
        atol=TOL,
    )

    opex_mask = ~clean["record_id"].isin({ANOMALY_SPEC["opex_reconciliation_record"]})
    opex_clean = clean[opex_mask]
    component_sum = (
        opex_clean["marketing_expense"]
        + opex_clean["payroll_expense"]
        + opex_clean["rent_expense"]
        + opex_clean["technology_expense"]
        + opex_clean["logistics_expense"]
        + opex_clean["other_operating_expense"]
    )
    assert np.allclose(opex_clean["operating_expenses"], component_sum, atol=TOL, equal_nan=True)

    assert np.allclose(clean["total_liabilities"], clean["debt"] + clean["other_liabilities"], atol=TOL)
    assert np.allclose(clean["total_assets"], clean["total_liabilities"] + clean["equity"], atol=TOL)
    assert np.allclose(clean["invested_capital"], clean["debt"] + clean["equity"] - clean["cash"], atol=TOL)

    planned_missing = {
        ("marketing_expense", rid) for rid in ANOMALY_SPEC["missing_marketing_expense"]
    } | {("customer_acquisition_cost", rid) for rid in ANOMALY_SPEC["missing_cac"]}
    for col in df.columns:
        missing = df[df[col].isna()]
        for _, row in missing.iterrows():
            assert (col, int(row["record_id"])) in planned_missing, (
                f"Unexpected missing value in {col} for record_id {row['record_id']}"
            )

    units_clean = clean[clean["record_id"] != ANOMALY_SPEC["impossible_units_sold_record"]]
    assert (units_clean["units_sold"] > 0).all()
    assert (clean[["cash", "debt", "other_liabilities", "equity", "total_assets", "invested_capital"]] >= 0).all().all()


def normalize_to_mxn(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with monetary columns converted to MXN at row level."""
    out = df.copy()
    unit_mult = np.where(out["reporting_unit"] == "thousands", 1_000.0, 1.0)
    for col in MONETARY_COLS:
        out[col + "_mxn"] = out[col] * unit_mult * out["fx_rate_to_mxn"]
    return out


def company_monthly_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute consolidated monthly KPIs after currency/unit normalization."""
    norm = normalize_to_mxn(df)
    months = sorted(norm["month"].unique())
    rows = []
    for month in months:
        m = norm[norm["month"] == month]
        rev = m["net_revenue_mxn"].sum()
        gp = m["gross_profit_mxn"].sum()
        ebitda = m["ebitda_mxn"].sum()
        op_inc = m["operating_income_mxn"].sum()
        ni = m["net_income_mxn"].sum()
        assets = m["total_assets_mxn"].sum()
        equity = m["equity_mxn"].sum()
        invested = m["invested_capital_mxn"].sum()
        rows.append(
            {
                "month": month,
                "net_revenue_mxn": rev,
                "gross_margin": gp / rev if rev else np.nan,
                "ebitda_margin": ebitda / rev if rev else np.nan,
                "operating_margin": op_inc / rev if rev else np.nan,
                "net_margin": ni / rev if rev else np.nan,
                "roa": ni / assets if assets else np.nan,
                "roe": ni / equity if equity else np.nan,
                "roi": ni / invested if invested else np.nan,
                "net_income_mxn": ni,
            }
        )
    return pd.DataFrame(rows)


def create_instructor_manifest(df: pd.DataFrame, issues: list[dict]) -> dict:
    """Build instructor ground-truth metadata."""
    kpis = company_monthly_kpis(df)
    complete_kpis = kpis[kpis["month"] != INCOMPLETE_MONTH]
    h1_2024 = complete_kpis[complete_kpis["month"] < "2024-07"]
    h2_2025 = complete_kpis[complete_kpis["month"] >= "2025-07"]

    def trend(col: str) -> str:
        a = h1_2024[col].mean()
        b = h2_2025[col].mean()
        delta = b - a
        rel = abs(delta / a) if a else abs(delta)
        if rel < 0.03:
            return "roughly flat"
        return "improving" if delta > 0 else "deteriorating"

    return {
        "random_seed": 42,
        "expected_rows": 432,
        "grain": "month x business_unit x region x channel",
        "categories": {
            "business_unit": BUSINESS_UNITS,
            "region": REGIONS,
            "channel": CHANNELS,
            "currency_by_region": REGION_CURRENCY,
            "reporting_units": ["units", "thousands"],
        },
        "intentional_quality_issues": issues,
        "accounting_identities": {
            "net_revenue": "gross_revenue - discounts - refunds",
            "gross_profit": "net_revenue - cogs",
            "operating_expenses": "sum of six OPEX components (excludes COGS, D&A, interest, tax)",
            "ebitda": "gross_profit - operating_expenses",
            "operating_income": "ebitda - depreciation_amortization",
            "pretax_income": "operating_income - interest_expense",
            "net_income": "operating_income - interest_expense - tax_expense",
            "total_liabilities": "debt + other_liabilities",
            "total_assets": "total_liabilities + equity",
            "invested_capital": "debt + equity - cash",
            "normalization": "value_mxn = value_local * unit_multiplier * fx_rate_to_mxn",
        },
        "expected_kpi_behavior": {
            "revenue_trend": trend("net_revenue_mxn"),
            "gross_margin_trend": trend("gross_margin"),
            "ebitda_margin_trend": trend("ebitda_margin"),
            "operating_margin_trend": trend("operating_margin"),
            "net_margin_trend": trend("net_margin"),
            "roa_trend": trend("roa"),
            "roe_trend": trend("roe"),
            "net_income_trend": trend("net_income_mxn"),
            "note": "Different profitability definitions should not all tell the same story.",
        },
        "incomplete_period": {
            "month": INCOMPLETE_MONTH,
            "period_end": "2025-12-18",
            "flow_scaling_factor": INCOMPLETE_FACTOR,
        },
        "thousands_reporting_unit_records": ANOMALY_SPEC["thousands_reporting_unit_records"],
    }


def create_validation_report(df: pd.DataFrame, issues: list[dict]) -> str:
    """Render an instructor validation markdown report."""
    norm = normalize_to_mxn(df)
    kpis = company_monthly_kpis(df)
    complete_kpis = kpis[kpis["month"] != INCOMPLETE_MONTH]

    lines = [
        "# Financial Performance Dataset — Generation Validation",
        "",
        "## Dataset shape",
        f"- Rows: {len(df)}",
        f"- Columns: {len(df.columns)}",
        "",
        "## Dtypes",
        "```",
        df.dtypes.to_string(),
        "```",
        "",
        "## Category values",
        f"- business_unit: {sorted(df['business_unit'].unique())}",
        f"- region: {sorted(df['region'].unique())}",
        f"- channel: {sorted(df['channel'].unique())}",
        f"- currency: {sorted(df['currency'].unique())}",
        f"- reporting_unit: {sorted(df['reporting_unit'].unique())}",
        "",
        "## Key uniqueness",
        f"- Unique record_id: {df['record_id'].nunique()}",
        f"- Unique composite keys: {df.drop_duplicates(['month','business_unit','region','channel']).shape[0]}",
        f"- Exact duplicate rows: {df.duplicated().sum()}",
        "",
        "## Missing values",
        "```",
        df.isna().sum()[df.isna().sum() > 0].to_string(),
        "```",
        "",
        "## Accounting reconciliation (clean rows only)",
        "- net_revenue = gross_revenue - discounts - refunds",
        "- gross_profit = net_revenue - cogs",
        "- ebitda = gross_profit - operating_expenses",
        "- operating_income = ebitda - depreciation_amortization",
        "- total_liabilities = debt + other_liabilities",
        "- total_assets = total_liabilities + equity",
        "- invested_capital = debt + equity - cash",
        "",
        "All checks passed via `validate_dataset()` assertions.",
        "",
        "## Currency distribution",
        "```",
        df.groupby('region')['currency'].agg(lambda x: x.unique()[0]).to_string(),
        "```",
        "",
        "## Reporting-unit distribution",
        "```",
        df['reporting_unit'].value_counts().to_string(),
        "```",
        "",
        "## Incomplete periods",
        f"- Rows with is_complete_period=False: {(~df['is_complete_period']).sum()}",
        f"- All correspond to month={INCOMPLETE_MONTH}",
        "",
        "## Intentional anomalies",
    ]

    for issue in issues:
        lines.append(
            f"- record_id={issue['record_id']}, column={issue['column']}: {issue['description']}"
        )

    lines.extend(
        [
            "",
            "## Company-level monthly KPI summary (MXN-normalized)",
            "",
            "Formulas (complete months aggregated by summing MXN amounts first):",
            "- gross_margin = sum(gross_profit_mxn) / sum(net_revenue_mxn)",
            "- ebitda_margin = sum(ebitda_mxn) / sum(net_revenue_mxn)",
            "- operating_margin = sum(operating_income_mxn) / sum(net_revenue_mxn)",
            "- net_margin = sum(net_income_mxn) / sum(net_revenue_mxn)",
            "- ROA = sum(net_income_mxn) / sum(total_assets_mxn)",
            "- ROE = sum(net_income_mxn) / sum(equity_mxn)",
            "- ROI = sum(net_income_mxn) / sum(invested_capital_mxn)",
            "",
            "```",
            complete_kpis[
                [
                    "month",
                    "gross_margin",
                    "ebitda_margin",
                    "operating_margin",
                    "net_margin",
                    "roa",
                    "roe",
                    "roi",
                ]
            ].round(4).to_string(index=False),
            "```",
            "",
            "## Trend summary (H1 2024 vs H2 2025, complete months)",
        ]
    )

    h1 = complete_kpis[complete_kpis["month"] < "2024-07"]
    h2 = complete_kpis[complete_kpis["month"] >= "2025-07"]

    def compare(label: str, col: str) -> str:
        return f"- {label}: {h1[col].mean():.4f} -> {h2[col].mean():.4f}"

    lines.extend(
        [
            compare("Revenue (MXN, mean monthly)", "net_revenue_mxn"),
            compare("Gross margin", "gross_margin"),
            compare("EBITDA margin", "ebitda_margin"),
            compare("Operating margin", "operating_margin"),
            compare("Net margin", "net_margin"),
            compare("ROA", "roa"),
            compare("ROE", "roe"),
            compare("ROI", "roi"),
            "",
            "### Interpretation",
            "Revenue rises while gross margin improves, but operating and net margins deteriorate more clearly.",
            "EBITDA margin is flatter than operating margin because depreciation rises with later CapEx.",
            "Absolute net income can remain stable or grow modestly while net margin falls because revenue scales faster.",
            "ROE can improve even as net margin falls when distributions and buybacks reduce equity faster than earnings decline.",
            "Students who average segment margins or sum unconverted currencies will reach misleading conclusions.",
        ]
    )

    return "\n".join(lines)


def export_student_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Select and order student-facing columns."""
    column_order = [
        "record_id",
        "month",
        "period_start",
        "period_end",
        "is_complete_period",
        "business_unit",
        "region",
        "channel",
        "currency",
        "fx_rate_to_mxn",
        "reporting_unit",
        "gross_revenue",
        "discounts",
        "refunds",
        "net_revenue",
        "cogs",
        "marketing_expense",
        "payroll_expense",
        "rent_expense",
        "technology_expense",
        "logistics_expense",
        "other_operating_expense",
        "operating_expenses",
        "gross_profit",
        "ebitda",
        "operating_income",
        "net_income",
        "capital_expenditure",
        "depreciation_amortization",
        "cash",
        "debt",
        "other_liabilities",
        "total_liabilities",
        "equity",
        "total_assets",
        "invested_capital",
        "interest_expense",
        "tax_expense",
        "active_customers",
        "new_customers",
        "churned_customers",
        "transactions",
        "units_sold",
        "average_order_value",
        "customer_acquisition_cost",
        "headcount",
    ]
    return df[column_order].copy()


def create_data_dictionary() -> str:
    """Return student-facing data dictionary markdown."""
    fields = [
        ("record_id", "integer", "Unique row identifier.", "ID", "dimension", "Primary key."),
        ("month", "string (YYYY-MM)", "Calendar month of the observation.", "month", "dimension", "Part of composite grain key."),
        ("period_start", "date", "First day of the reporting period.", "date", "dimension", "Use with period_end for partial periods."),
        ("period_end", "date", "Last day included in the reporting period.", "date", "dimension", "May be before month-end for incomplete periods."),
        ("is_complete_period", "boolean", "Whether the row covers a full calendar month.", "flag", "dimension", "False for partial December 2025."),
        ("business_unit", "string", "Customer segment: Consumer or SMB.", "category", "dimension", "Persistent segment differences exist."),
        ("region", "string", "Geographic market.", "category", "dimension", "Determines local currency."),
        ("channel", "string", "Go-to-market channel.", "category", "dimension", "Affects cost structure."),
        ("currency", "string", "Local reporting currency for monetary fields.", "currency code", "dimension", "MXN, USD, or COP."),
        ("fx_rate_to_mxn", "float", "MXN per one unit of local currency.", "MXN / local unit", "dimension", "Multiply monetary values by this after unit normalization to compare in MXN."),
        ("reporting_unit", "string", "Scale of monetary amounts: units or thousands.", "category", "dimension", "If thousands, multiply monetary values by 1,000 before FX conversion."),
        ("gross_revenue", "float", "Total billed sales before discounts and refunds.", "local currency", "flow", "Normalize before cross-region aggregation."),
        ("discounts", "float", "Promotional and pricing discounts.", "local currency", "flow", "Reduces gross revenue."),
        ("refunds", "float", "Customer refunds and returns.", "local currency", "flow", "Reduces gross revenue."),
        ("net_revenue", "float", "Revenue after discounts and refunds.", "local currency", "derived", "gross_revenue - discounts - refunds."),
        ("cogs", "float", "Cost of goods sold.", "local currency", "flow", "Direct product/service delivery cost."),
        ("marketing_expense", "float", "Advertising, campaigns, and acquisition spend.", "local currency", "flow", "Part of operating expenses."),
        ("payroll_expense", "float", "Employee compensation and benefits.", "local currency", "flow", "Part of operating expenses."),
        ("rent_expense", "float", "Facilities and store rent.", "local currency", "flow", "Part of operating expenses."),
        ("technology_expense", "float", "Software, infrastructure, and IT operations.", "local currency", "flow", "Part of operating expenses."),
        ("logistics_expense", "float", "Fulfillment, shipping, and delivery costs.", "local currency", "flow", "Part of operating expenses."),
        ("other_operating_expense", "float", "Remaining operating costs not elsewhere classified.", "local currency", "flow", "Part of operating expenses."),
        ("operating_expenses", "float", "Total operating expense excl. COGS, D&A, interest, and tax.", "local currency", "derived", "Sum of six OPEX components only."),
        ("gross_profit", "float", "Net revenue minus COGS.", "local currency", "derived", "net_revenue - cogs."),
        ("ebitda", "float", "Earnings before interest, taxes, depreciation, and amortization.", "local currency", "derived", "gross_profit - operating_expenses."),
        ("operating_income", "float", "EBITDA minus depreciation and amortization.", "local currency", "derived", "ebitda - depreciation_amortization."),
        ("net_income", "float", "Bottom-line profit after interest and taxes.", "local currency", "derived", "operating_income - interest_expense - tax_expense."),
        ("capital_expenditure", "float", "Cash invested in long-lived assets.", "local currency", "flow", "Drives future depreciation."),
        ("depreciation_amortization", "float", "Non-cash allocation of prior capital investment.", "local currency", "flow", "Excluded from operating_expenses."),
        ("cash", "float", "Allocated cash balance for the segment.", "local currency", "stock", "End-of-period; summable across segments."),
        ("debt", "float", "Allocated interest-bearing debt.", "local currency", "stock", "Drives interest expense."),
        ("other_liabilities", "float", "Allocated non-debt liabilities.", "local currency", "stock", "Summable across segments."),
        ("total_liabilities", "float", "Debt plus other liabilities.", "local currency", "derived", "debt + other_liabilities."),
        ("equity", "float", "Allocated shareholders' equity.", "local currency", "stock", "Used for ROE at consolidated level."),
        ("total_assets", "float", "Liabilities plus equity.", "local currency", "derived", "total_liabilities + equity."),
        ("invested_capital", "float", "Debt plus equity minus cash.", "local currency", "derived", "Useful for ROI-style metrics."),
        ("interest_expense", "float", "Cost of debt financing.", "local currency", "flow", "Function of allocated debt."),
        ("tax_expense", "float", "Income taxes on positive pre-tax income.", "local currency", "flow", "Regional effective rates differ."),
        ("active_customers", "float", "Customers active at period end.", "count", "stock", "Not scaled for partial periods."),
        ("new_customers", "float", "Customers acquired during the period.", "count", "flow", "Scaled for partial periods."),
        ("churned_customers", "float", "Customers lost during the period.", "count", "flow", "Scaled for partial periods."),
        ("transactions", "float", "Number of orders/transactions.", "count", "flow", "Relates to revenue volume."),
        ("units_sold", "float", "Physical or logical units sold.", "count", "flow", "Relates to logistics costs."),
        ("average_order_value", "float", "Revenue per transaction.", "local currency", "derived", "net_revenue / transactions."),
        ("customer_acquisition_cost", "float", "Marketing spend per new customer.", "local currency", "derived", "marketing_expense / new_customers."),
        ("headcount", "float", "Allocated employees for the segment.", "count", "stock", "Relates to payroll expense."),
    ]

    lines = [
        "# Financial Performance Data Dictionary",
        "",
        "## Grain",
        "One row = **month × business_unit × region × channel**.",
        "Composite key: (`month`, `business_unit`, `region`, `channel`).",
        "",
        "## Currency and unit normalization",
        "Monetary values are stored in the row's `currency` and `reporting_unit`.",
        "To express a monetary value in MXN:",
        "",
        "```",
        "value_mxn = value_local × unit_multiplier × fx_rate_to_mxn",
        "",
        "unit_multiplier = 1       if reporting_unit == 'units'",
        "unit_multiplier = 1_000   if reporting_unit == 'thousands'",
        "```",
        "",
        "Do **not** sum monetary values across regions before applying FX conversion.",
        "Do **not** compute company margins as simple averages of segment margins.",
        "Instead, normalize, aggregate numerators and denominators, then divide.",
        "",
        "## Balance sheet allocation",
        "Balance-sheet fields are segment-level allocations that sum to company totals.",
        "They are legitimate to aggregate by summation after unit/FX normalization.",
        "",
        "## Operating expenses scope",
        "`operating_expenses` includes marketing, payroll, rent, technology, logistics, and other operating expense.",
        "It **excludes** COGS, depreciation & amortization, interest, and taxes.",
        "",
        "## Columns",
        "",
        "| Column | Type | Definition | Unit | Field kind | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for name, typ, definition, unit, kind, notes in fields:
        lines.append(f"| {name} | {typ} | {definition} | {unit} | {kind} | {notes} |")

    return "\n".join(lines)


def generate_dataset() -> tuple[pd.DataFrame, list[dict]]:
    """Full generation pipeline."""
    df = build_dimensions()
    df = add_period_metadata(df)
    df = generate_fx_rates(df)
    df = generate_operating_drivers(df)
    df = generate_revenue(df)
    df = generate_costs(df)
    df = calculate_gross_and_ebitda(df)
    df = generate_capex_and_depreciation(df)
    df = calculate_operating_income(df)
    df = generate_balance_sheet_and_financing(df)
    df = calculate_operational_metrics(df)
    df = apply_incomplete_period_scaling(df)
    df = apply_thousands_reporting_unit(df, ANOMALY_SPEC["thousands_reporting_unit_records"])
    df, issues = inject_quality_issues(df)
    validate_dataset(df, issues)
    return df, issues


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    df, issues = generate_dataset()
    student_df = export_student_dataset(df)

    csv_path = DATA_DIR / "financial_performance.csv"
    student_df.to_csv(csv_path, index=False)

    dict_path = DATA_DIR / "data_dictionary.md"
    dict_path.write_text(create_data_dictionary(), encoding="utf-8")

    manifest = create_instructor_manifest(df, issues)
    manifest_path = DATA_DIR / "instructor_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    validation_path = DOCS_DIR / "generation_validation.md"
    validation_path.write_text(create_validation_report(df, issues), encoding="utf-8")

    print(f"Wrote {csv_path}")
    print(f"Wrote {dict_path}")
    print(f"Wrote {manifest_path}")
    print(f"Wrote {validation_path}")
    print(f"Rows: {len(student_df)}, Columns: {len(student_df.columns)}")


if __name__ == "__main__":
    main()
