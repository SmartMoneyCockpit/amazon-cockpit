
#!/usr/bin/env python3
import os, sys, io

ROOT = os.getcwd()

DIST_FILE = os.path.join(ROOT, "utils", "distribute.py")
WEEKLY_PAGE = os.path.join(ROOT, "pages", "43_Weekly_Digest.py")
SNAP_FILE = os.path.join(ROOT, "scripts", "snapshots.py")

DIST_FN = r"""
def distribute_weekly(week_tag: str, subject_prefix: str = "Weekly Digest") -> dict:
    """
    Intenta enviar weekly_digest_<YYYYWW>.pdf/.zip via SendGrid y/o Webhook.
    Requiere las funciones existentes: send_email_via_sendgrid, post_to_webhook.
    Usa DIGEST_OUT_DIR (default /tmp).
    """
    import os
    tag = week_tag
    outdir = os.getenv("DIGEST_OUT_DIR", "/tmp")
    pdf = os.path.join(outdir, f"weekly_digest_{tag}.pdf")
    zf  = os.path.join(outdir, f"weekly_digest_{tag}.zip")
    paths = {}
    if os.path.exists(pdf): paths["pdf"] = pdf
    if os.path.exists(zf):  paths["zip"] = zf

    results = {}
    # Email (si está configurado)
    if os.getenv("SENDGRID_API_KEY") and os.getenv("DIGEST_EMAIL_TO") and os.getenv("DIGEST_EMAIL_FROM"):
        html = f"<p>Weekly digest {tag} generated.</p>" + ''.join(
            f"<p>Attached: {os.path.basename(p)}</p>" for p in paths.values()
        )
        status, msg = send_email_via_sendgrid(f"{subject_prefix} — {tag}", html, attachments=paths)
        results["email"] = (status, msg)
    else:
        results["email"] = ("skipped", "email env not fully set")

    # Webhook (opcional)
    if os.getenv("WEBHOOK_URL"):
        payload = {"type": "weekly_digest", "week": tag, "paths": paths}
        status, msg = post_to_webhook(payload)
        results["webhook"] = (status, msg)
    else:
        results["webhook"] = ("skipped", "WEBHOOK_URL not set")

    return results
"""
SNAP_HOOK = r"""
# === Weekly digest on Sundays (America/Mazatlan) ===
try:
    import datetime as dt, pytz
    tz = pytz.timezone("America/Mazatlan")
    now = dt.datetime.now(tz)
    # Domingo (Monday=0 → Sunday=6)
    if now.weekday() == 6:
        from scripts import weekly_digest
        res = weekly_digest.generate()   # crea weekly_digest_<YYYYWW>.pdf/.zip
        try:
            from utils.distribute import distribute_weekly
            distribute_weekly(res.get("week"))
        except Exception:
            pass
except Exception:
    pass
"""
WEEKLY_BTN = r"""
# --- Weekly send button ---
st.markdown("—")
if col[1].button("Send Weekly Now"):
    try:
        from utils.distribute import distribute_weekly
        tag = st.session_state.get("_weekly_paths", {}).get("week")
        if not tag:
            import datetime as dt
            tag = dt.datetime.utcnow().strftime("%G%V")
        res = distribute_weekly(tag)
        st.json(res)
    except Exception as e:
        st.error(f"Send failed: {e}")
"""

def ensure_distribute_weekly():
    if not os.path.exists(DIST_FILE):
        print("utils/distribute.py not found. Please add Day-18 Distribution first.")
        return False
    with open(DIST_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    if "def distribute_weekly(" in content:
        print("distribute_weekly() already present.")
        return True
    with open(DIST_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n" + DIST_FN + "\n")
    print("Appended distribute_weekly() to utils/distribute.py")
    return True

def ensure_snapshots_hook():
    if not os.path.exists(SNAP_FILE):
        print("scripts/snapshots.py not found. Skipping snapshots hook.")
        return
    with open(SNAP_FILE, "r", encoding="utf-8") as f:
        txt = f.read()
    if "Weekly digest on Sundays" in txt:
        print("Weekly hook already present in scripts/snapshots.py")
        return
    with open(SNAP_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n" + SNAP_HOOK + "\n")
    print("Appended weekly hook to scripts/snapshots.py")

def ensure_weekly_button():
    if not os.path.exists(WEEKLY_PAGE):
        print("pages/43_Weekly_Digest.py not found. Skipping page button patch.")
        return
    with open(WEEKLY_PAGE, "r", encoding="utf-8") as f:
        page = f.read()
    if "Send Weekly Now" in page:
        print("Weekly send button already present in Weekly Digest page.")
        return
    # Insert button near downloads section or at end
    page += "\n\n" + WEEKLY_BTN + "\n"
    with open(WEEKLY_PAGE, "w", encoding="utf-8") as f:
        f.write(page)
    print("Added 'Send Weekly Now' button to pages/43_Weekly_Digest.py")

def main():
    ok = ensure_distribute_weekly()
    if ok:
        ensure_snapshots_hook()
        ensure_weekly_button()
    print("Done.")

if __name__ == "__main__":
    main()
