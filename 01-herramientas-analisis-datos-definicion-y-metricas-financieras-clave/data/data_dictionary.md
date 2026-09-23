# Financial Performance Data Dictionary

## Grain
One row = **month × business_unit × region × channel**.
Composite key: (`month`, `business_unit`, `region`, `channel`).

## Currency and unit normalization
Monetary values are stored in the row's `currency` and `reporting_unit`.
To express a monetary value in MXN:

```
value_mxn = value_local × unit_multiplier × fx_rate_to_mxn

unit_multiplier = 1       if reporting_unit == 'units'
unit_multiplier = 1_000   if reporting_unit == 'thousands'
```

Do **not** sum monetary values across regions before applying FX conversion.
Do **not** compute company margins as simple averages of segment margins.
Instead, normalize, aggregate numerators and denominators, then divide.

## Balance sheet allocation
Balance-sheet fields are segment-level allocations that sum to company totals.
They are legitimate to aggregate by summation after unit/FX normalization.

## Operating expenses scope
`operating_expenses` includes marketing, payroll, rent, technology, logistics, and other operating expense.
It **excludes** COGS, depreciation & amortization, interest, and taxes.

## Columns

| Column | Type | Definition | Unit | Field kind | Notes |
| --- | --- | --- | --- | --- | --- |
| record_id | integer | Unique row identifier. | ID | dimension | Primary key. |
| month | string (YYYY-MM) | Calendar month of the observation. | month | dimension | Part of composite grain key. |
| period_start | date | First day of the reporting period. | date | dimension | Use with period_end for partial periods. |
| period_end | date | Last day included in the reporting period. | date | dimension | May be before month-end for incomplete periods. |
| is_complete_period | boolean | Whether the row covers a full calendar month. | flag | dimension | False for partial December 2025. |
| business_unit | string | Customer segment: Consumer or SMB. | category | dimension | Persistent segment differences exist. |
| region | string | Geographic market. | category | dimension | Determines local currency. |
| channel | string | Go-to-market channel. | category | dimension | Affects cost structure. |
| currency | string | Local reporting currency for monetary fields. | currency code | dimension | MXN, USD, or COP. |
| fx_rate_to_mxn | float | MXN per one unit of local currency. | MXN / local unit | dimension | Multiply monetary values by this after unit normalization to compare in MXN. |
| reporting_unit | string | Scale of monetary amounts: units or thousands. | category | dimension | If thousands, multiply monetary values by 1,000 before FX conversion. |
| gross_revenue | float | Total billed sales before discounts and refunds. | local currency | flow | Normalize before cross-region aggregation. |
| discounts | float | Promotional and pricing discounts. | local currency | flow | Reduces gross revenue. |
| refunds | float | Customer refunds and returns. | local currency | flow | Reduces gross revenue. |
| net_revenue | float | Revenue after discounts and refunds. | local currency | derived | gross_revenue - discounts - refunds. |
| cogs | float | Cost of goods sold. | local currency | flow | Direct product/service delivery cost. |
| marketing_expense | float | Advertising, campaigns, and acquisition spend. | local currency | flow | Part of operating expenses. |
| payroll_expense | float | Employee compensation and benefits. | local currency | flow | Part of operating expenses. |
| rent_expense | float | Facilities and store rent. | local currency | flow | Part of operating expenses. |
| technology_expense | float | Software, infrastructure, and IT operations. | local currency | flow | Part of operating expenses. |
| logistics_expense | float | Fulfillment, shipping, and delivery costs. | local currency | flow | Part of operating expenses. |
| other_operating_expense | float | Remaining operating costs not elsewhere classified. | local currency | flow | Part of operating expenses. |
| operating_expenses | float | Total operating expense excl. COGS, D&A, interest, and tax. | local currency | derived | Sum of six OPEX components only. |
| gross_profit | float | Net revenue minus COGS. | local currency | derived | net_revenue - cogs. |
| ebitda | float | Earnings before interest, taxes, depreciation, and amortization. | local currency | derived | gross_profit - operating_expenses. |
| operating_income | float | EBITDA minus depreciation and amortization. | local currency | derived | ebitda - depreciation_amortization. |
| net_income | float | Bottom-line profit after interest and taxes. | local currency | derived | operating_income - interest_expense - tax_expense. |
| capital_expenditure | float | Cash invested in long-lived assets. | local currency | flow | Drives future depreciation. |
| depreciation_amortization | float | Non-cash allocation of prior capital investment. | local currency | flow | Excluded from operating_expenses. |
| cash | float | Allocated cash balance for the segment. | local currency | stock | End-of-period; summable across segments. |
| debt | float | Allocated interest-bearing debt. | local currency | stock | Drives interest expense. |
| other_liabilities | float | Allocated non-debt liabilities. | local currency | stock | Summable across segments. |
| total_liabilities | float | Debt plus other liabilities. | local currency | derived | debt + other_liabilities. |
| equity | float | Allocated shareholders' equity. | local currency | stock | Used for ROE at consolidated level. |
| total_assets | float | Liabilities plus equity. | local currency | derived | total_liabilities + equity. |
| invested_capital | float | Debt plus equity minus cash. | local currency | derived | Useful for ROI-style metrics. |
| interest_expense | float | Cost of debt financing. | local currency | flow | Function of allocated debt. |
| tax_expense | float | Income taxes on positive pre-tax income. | local currency | flow | Regional effective rates differ. |
| active_customers | float | Customers active at period end. | count | stock | Not scaled for partial periods. |
| new_customers | float | Customers acquired during the period. | count | flow | Scaled for partial periods. |
| churned_customers | float | Customers lost during the period. | count | flow | Scaled for partial periods. |
| transactions | float | Number of orders/transactions. | count | flow | Relates to revenue volume. |
| units_sold | float | Physical or logical units sold. | count | flow | Relates to logistics costs. |
| average_order_value | float | Revenue per transaction. | local currency | derived | net_revenue / transactions. |
| customer_acquisition_cost | float | Marketing spend per new customer. | local currency | derived | marketing_expense / new_customers. |
| headcount | float | Allocated employees for the segment. | count | stock | Relates to payroll expense. |