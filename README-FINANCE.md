# Next Step: Finance Dashboard — SKU-Level Profitability

### What this adds
- **Profitability math**: Revenue − (COGS + Fees) = Gross Profit; minus AdSpend → Net Profit.
- **Margins**: GrossMargin%, NetMargin%, ACoS%, per‑unit economics.
- **Trends**: monthly Revenue / GP / Net, AdSpend area.
- **SKU table** with export buttons.
- **Alerts**: NEGATIVE net margin (crit), Gross margin < 30% (warn).

### Google Sheets (optional)
Secrets supported:
- `gsheets_finance_sheet_id` → worksheet **finance**

Template: `sheets_templates/finance_template.csv`

### How to apply
1. Copy `utils/finance.py` into your project.
2. Replace the contents of `modules/finance_dashboard.py` with `modules_finance_dashboard.py` from this pack.
3. (Optional) Set the Sheet ID secret and share to your service account.
4. Redeploy.
