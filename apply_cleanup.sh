    #!/usr/bin/env bash
    set -euo pipefail

    echo "▶ Vega Cockpit automatic cleanup starting..."

    # 1) go to project root (Render source dir)
    cd /opt/render/project/src || { echo "Not running on Render (missing /opt/render/project/src)"; exit 1; }

    echo "• Working dir: $(pwd)"

    # 2) remove obsolete/duplicate pages
    echo "• Removing obsolete pages..."
    rm -f pages/44_Settings_Controls.py pages/45_Developer_Tools.py pages/Dev_Diagnostics.py || true
    # also remove stray patch file if present in root
    rm -f 44_Settings_Controls_patch.py || true

    # 3) inject System Tools block into Admin Console (45_Settings.py) if missing
    if ! grep -q "System Tools" pages/45_Settings.py 2>/dev/null; then
      echo "• Injecting 'System Tools' section into pages/45_Settings.py..."
      python3 - <<'PY'
import io, sys, os, re
p = "pages/45_Settings.py"
try:
    with open(p, "r", encoding="utf-8") as f:
        src = f.read()
except FileNotFoundError:
    print("ERROR: pages/45_Settings.py not found", file=sys.stderr)
    sys.exit(0)

block = '''
st.divider()
st.subheader("System Tools")
colA, colB, colC = st.columns(3)
with colA:
    st.page_link("pages/46_Backup_Manager.py", label="Backup Manager", icon="💾")
    st.page_link("pages/47_File_Inventory.py", label="File Inventory", icon="🗂️")
with colB:
    st.page_link("pages/48_Jobs_History.py", label="Jobs History", icon="📜")
    st.page_link("pages/49_Restore_Manager.py", label="Restore Manager", icon="🧩")
with colC:
    st.page_link("pages/900__Diagnostics.py", label="Diagnostics & Smoke Tests", icon="🩺")
    st.page_link("pages/35_Drive_Upload_Test.py", label="Drive Upload Test", icon="☁️")
    st.page_link("pages/42_PPC_Live.py", label="PPC Live — Amazon Ads API", icon="📈")
'''
# Try to append near the end; if a trailing caption is present, put it before it.
insertion_done = False

# Prefer to insert before the last closing line if there is a typical trailing caption.
anchor_patterns = [
    r"st\.caption\([^)]*\)\s*$",  # a trailing caption line
]
for pat in anchor_patterns:
    m = list(re.finditer(pat, src, flags=re.MULTILINE))
    if m:
        idx = m[-1].end()
        new = src[:idx] + "\n\n" + block + "\n" + src[idx:]
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        insertion_done = True
        break

if not insertion_done:
    # fallback: just append at the end
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n\n# Injected by cleanup\n" + block + "\n")
PY
    else
      echo "• 'System Tools' already present — skipping injection."
    fi

    # 4) clean sidebar: remove Settings Controls & Developer Tools links if present
    echo "• Cleaning sidebar links in app.py (if present)..."
    # Remove any line that links to the old Settings Controls page
    sed -i '/pages\/44_Settings_Controls.py/d' app.py || true
    # Remove any line that pulls in 45_Developer_Tools.py from the sidebar
    sed -i '/45_Developer_Tools.py/d' app.py || true
    # Also remove any explicit 'Developer Tools' label line
    sed -i '/Developer Tools/d' app.py || true

    # 5) restart app by touching app.py (Render detects and reloads)
    echo "• Touching app.py to trigger reload..."
    touch app.py

    echo "✅ Cleanup complete. Render will redeploy shortly."
