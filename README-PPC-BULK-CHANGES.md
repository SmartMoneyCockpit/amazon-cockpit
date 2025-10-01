# Next Step: PPC Bulk Changes CSV + Changes Log

This pack adds a conversion layer that turns your **Optimizer** suggestions into
human‑readable CSVs for **Campaign Budgets**, **Keyword Bids/Pauses**, and **Negatives**,
plus a flat **Changes Log** you can archive or upload to Sheets later.

## Files
- `utils/ppc_changes.py` → split actions into campaigns/keywords/negatives + CSV bytes + changes log builder
- `modules_ppc_manager_snippet.py` → a small function you paste into your `ppc_manager.py` and call after `actions_df`

## How to apply
1) Copy `utils/ppc_changes.py` into your project.
2) Open `modules/ppc_manager.py` and:
   - Paste the `_render_bulk_changes_and_log(actions_df)` function from `modules_ppc_manager_snippet.py` (top or bottom of file).
   - After your suggestions table is shown (where `actions_df` exists), call:
     ```python
     _render_bulk_changes_and_log(actions_df)
     ```
3) Redeploy. You’ll see two new expanders:
   - **Export Bulk Files** → three CSVs (campaigns, keywords, negatives)
   - **Export Changes Log** → a flat log CSV with timestamps and reasons

## Notes
- This is a neutral CSV format, not an official Amazon Bulk schema. It’s designed for quick review and easy mapping.
- If you want direct **Ads API write** later, we can add an execution layer with dry‑run + confirmation prompts.
- For a Google Sheets log, we’ll add **write** scopes and a small `gsheets_write.py` helper in a future step.
