# Next Step: Role‑Scoped Views

This pack adds **role‑based tab visibility** so each teammate sees only what they need.
Roles included out‑of‑the‑box:
- **Admin** (everything)
- **ROI Renegades (PPC)** → Home, PPC Manager, Finance Dashboard, Alerts Hub
- **Joanne (Compliance)** → Home, Compliance Vault, Product Tracker, Alerts Hub
- **Faith (A+ / Creative)** → Home, A+ & SEO, Product Tracker, Alerts Hub

## Files
- `utils/roles.py` → role definitions & helpers
- `app_roles.py` → drop‑in app that gates tabs by role

## How to use
1) Copy `utils/roles.py` into your project.
2) Add `app_roles.py` alongside your existing `app.py`.
3) On Render, you can either:
   - Change the start command to use `app_roles.py`:
     ```
     streamlit run app_roles.py --server.address 0.0.0.0 --server.port $PORT
     ```
   - Or keep `app.py` and manually copy the role selector pattern into it.

## Customize
Edit `ROLE_MAP` in `utils/roles.py` to change tab access per role or add new roles.
You can also drive the selected role via a secret or a query param later (e.g., `?role=Joanne (Compliance)`).
