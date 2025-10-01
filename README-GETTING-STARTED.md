# Next Step: "Getting Started" Checklist (Home)

Adds a guided setup panel on the Home screen so you (and teammates) can see at a glance what’s configured and what’s left.

## Files
- `utils/onboarding.py` → builds checklist rows from your secrets
- `modules/home_onboarding_snippet.py` → function `render_getting_started()` to paste into `modules/home.py`

## How to apply
1) Copy both files into your project.
2) In `modules/home.py`, import and call it inside `dashboard_home_view()` (anywhere below the KPIs), e.g.:
   ```python
   from modules.home_onboarding_snippet import render_getting_started
   ...
   render_getting_started()
   ```
3) (Optional) Use the **Secrets Template** downloader on the Home page to scaffold your `.streamlit/secrets.toml`.

That’s it — the checklist reads current secrets and marks items ✅/⚠️/ℹ️/• accordingly.
