# Financial Performance Dataset — Generation Validation

## Dataset shape
- Rows: 432
- Columns: 46

## Dtypes
```
record_id                      int64
month                            str
business_unit                    str
region                           str
channel                          str
period_start                     str
period_end                       str
is_complete_period              bool
currency                         str
fx_rate_to_mxn               float64
reporting_unit                   str
active_customers             float64
new_customers                float64
churned_customers            float64
transactions                 float64
headcount                    float64
gross_revenue                float64
discounts                    float64
refunds                      float64
net_revenue                  float64
cogs                         float64
marketing_expense            float64
payroll_expense              float64
rent_expense                 float64
technology_expense           float64
logistics_expense            float64
other_operating_expense      float64
operating_expenses           float64
gross_profit                 float64
ebitda                       float64
capital_expenditure          float64
depreciation_amortization    float64
operating_income             float64
debt                         float64
interest_expense             float64
tax_expense                  float64
net_income                   float64
cash                         float64
other_liabilities            float64
equity                       float64
total_liabilities            float64
total_assets                 float64
invested_capital             float64
units_sold                   float64
average_order_value          float64
customer_acquisition_cost    float64
```

## Category values
- business_unit: ['Consumer', 'SMB']
- region: ['Colombia', 'Mexico', 'United States']
- channel: ['Online', 'Partner', 'Retail']
- currency: ['COP', 'MXN', 'USD']
- reporting_unit: ['thousands', 'units']

## Key uniqueness
- Unique record_id: 432
- Unique composite keys: 432
- Exact duplicate rows: 0

## Missing values
```
marketing_expense            2
customer_acquisition_cost    2
```

## Accounting reconciliation (clean rows only)
- net_revenue = gross_revenue - discounts - refunds
- gross_profit = net_revenue - cogs
- ebitda = gross_profit - operating_expenses
- operating_income = ebitda - depreciation_amortization
- total_liabilities = debt + other_liabilities
- total_assets = total_liabilities + equity
- invested_capital = debt + equity - cash

All checks passed via `validate_dataset()` assertions.

## Currency distribution
```
region
Colombia         COP
Mexico           MXN
United States    USD
```

## Reporting-unit distribution
```
reporting_unit
units        429
thousands      3
```

## Incomplete periods
- Rows with is_complete_period=False: 18
- All correspond to month=2025-12

## Intentional anomalies
- record_id=12, column=marketing_expense: Marketing expense intentionally set to null.
- record_id=187, column=marketing_expense: Marketing expense intentionally set to null.
- record_id=45, column=customer_acquisition_cost: CAC intentionally set to null (marketing/new_customers still present).
- record_id=301, column=customer_acquisition_cost: CAC intentionally set to null (marketing/new_customers still present).
- record_id=98, column=marketing_expense: Marketing expense multiplied by 4.2; still technically possible.
- record_id=256, column=gross_revenue: Gross revenue multiplied by 3.6; downstream profit fields not fully reconciled.
- record_id=334, column=operating_expenses: Operating expenses no longer equal the sum of OPEX components.
- record_id=412, column=units_sold: Units sold set to a negative value.
- record_id=67, column=reporting_unit: Monetary values divided by 1,000; reporting_unit='thousands'.
- record_id=198, column=reporting_unit: Monetary values divided by 1,000; reporting_unit='thousands'.
- record_id=389, column=reporting_unit: Monetary values divided by 1,000; reporting_unit='thousands'.

## Company-level monthly KPI summary (MXN-normalized)

Formulas (complete months aggregated by summing MXN amounts first):
- gross_margin = sum(gross_profit_mxn) / sum(net_revenue_mxn)
- ebitda_margin = sum(ebitda_mxn) / sum(net_revenue_mxn)
- operating_margin = sum(operating_income_mxn) / sum(net_revenue_mxn)
- net_margin = sum(net_income_mxn) / sum(net_revenue_mxn)
- ROA = sum(net_income_mxn) / sum(total_assets_mxn)
- ROE = sum(net_income_mxn) / sum(equity_mxn)
- ROI = sum(net_income_mxn) / sum(invested_capital_mxn)

```
  month  gross_margin  ebitda_margin  operating_margin  net_margin    roa    roe    roi
2024-01        0.4840         0.1915            0.1665      0.0931 0.0085 0.0163 0.0100
2024-02        0.4806         0.1938            0.1680      0.0969 0.0095 0.0184 0.0112
2024-03        0.4807         0.1909            0.1633      0.0948 0.0103 0.0201 0.0121
2024-04        0.4854         0.1906            0.1594      0.0927 0.0105 0.0206 0.0123
2024-05        0.4911         0.1876            0.1510      0.0820 0.0094 0.0187 0.0110
2024-06        0.4906         0.1932            0.1566      0.0884 0.0107 0.0215 0.0125
2024-07        0.4911         0.1905            0.1493      0.0821 0.0096 0.0196 0.0113
2024-08        0.4965         0.1913            0.1491      0.0831 0.0102 0.0210 0.0120
2024-09        0.5054         0.1948            0.1542      0.0839 0.0111 0.0231 0.0130
2024-10        0.4977         0.1752            0.1301      0.0666 0.0090 0.0190 0.0106
2024-11        0.5058         0.1903            0.1488      0.0846 0.0127 0.0271 0.0149
2024-12        0.5132         0.2000            0.1606      0.0958 0.0159 0.0344 0.0187
2025-01        0.5138         0.1813            0.1273      0.0598 0.0076 0.0167 0.0089
2025-02        0.5128         0.1871            0.1323      0.0640 0.0088 0.0195 0.0103
2025-03        0.3861         0.1388            0.0992      0.0521 0.0103 0.0232 0.0121
2025-04        0.5196         0.1919            0.1378      0.0719 0.0113 0.0257 0.0132
2025-05        0.5232         0.1917            0.1344      0.0690 0.0112 0.0259 0.0131
2025-06        0.5199         0.1808            0.1186      0.0550 0.0087 0.0205 0.0102
2025-07        0.5217         0.1813            0.1109      0.0482 0.0077 0.0185 0.0090
2025-08        0.5304         0.1849            0.1183      0.0548 0.0092 0.0224 0.0107
2025-09        0.5354         0.1766            0.0997      0.0382 0.0066 0.0163 0.0077
2025-10        0.5391         0.1913            0.1196      0.0565 0.0108 0.0273 0.0126
2025-11        0.5437         0.1930            0.1231      0.0603 0.0124 0.0317 0.0143
```

## Trend summary (H1 2024 vs H2 2025, complete months)
- Revenue (MXN, mean monthly): 105776792.6413 -> 189811326.5343
- Gross margin: 0.4854 -> 0.5341
- EBITDA margin: 0.1913 -> 0.1854
- Operating margin: 0.1608 -> 0.1143
- Net margin: 0.0913 -> 0.0516
- ROA: 0.0098 -> 0.0094
- ROE: 0.0193 -> 0.0232
- ROI: 0.0115 -> 0.0109

### Interpretation
Revenue rises while gross margin improves, but operating and net margins deteriorate more clearly.
EBITDA margin is flatter than operating margin because depreciation rises with later CapEx.
Absolute net income can remain stable or grow modestly while net margin falls because revenue scales faster.
ROE can improve even as net margin falls when distributions and buybacks reduce equity faster than earnings decline.
Students who average segment margins or sum unconverted currencies will reach misleading conclusions.