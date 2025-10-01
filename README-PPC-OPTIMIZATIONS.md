# Next Step: PPC Optimizations (Guardrails, Bid Rules, Negatives)

### What this adds
- **Guardrails (Campaign)**: raise/cut budget based on ACoS and conversions.
- **Bid Rules (Keyword)**: raise/lower bids, pause unprofitable terms.
- **Negative Candidates**: low-CTR, high-impression, zero-order terms.
- **Export** suggestions (CSV/XLSX/PDF) and send alerts to the Alerts Hub.

### How to apply
1. Copy `utils/ppc_opt.py` into your project.
2. Replace the contents of `modules/ppc_manager.py` with `modules_ppc_manager.py` from this pack.
3. Redeploy. Tune settings in the **Optimizer** panel (ACoS target, min clicks/conv, CTR floor).

### Notes
- This runs on your current PPC tab data (sample or live). Once we wire Amazon Ads pulls, these rules will operate on real campaigns/keywords.
- In a later step we can export a “changes file” for bulk ops or call the Ads API to enact changes.
