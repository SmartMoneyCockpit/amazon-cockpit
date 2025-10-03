
#!/usr/bin/env python3
"""
Apply Sidebar Plan (viewer+strict)
- Renames pages to canonical numeric order.
- Disables admin-only pages and any extras not in canonical list.
"""

import os, re, sys

CANONICAL = [
    "00_Home_Global_Overview.py",
    "01_Data_Seed.py",
    "10_Product_Tracker.py",
    "14_PPC_Manager_Safe.py",
    "15_PPC_Import_Wizard.py",
    "21_Aplus_SEO_Panel.py",
    "22_Compliance_Vault_App.py",
    "24_Product_Research_Scoring.py",
    "25_Data_Sync.py",
    "26_Finance_Monthly_Export.py",
    "27_Finance_Dashboard_v2.py",
    "33_Finance_Heatmap.py",
    "36_COGS_Manager.py",
    "37_Revenue_Protection.py",
    "38_Reorder_Forecast.py",
    "39_Margin_Scenario.py",
    "34_Daily_Digest.py",
    "35_Drive_Upload_Test.py",
    "40_Digest_Distribution.py",
    "41_Alerts_Notifications.py",
    "42_PPC_Live.py",
    "43_Weekly_Digest.py",
]

ADMIN_ONLY = {
    "25_Data_Sync.py",
    "35_Drive_Upload_Test.py",
    "40_Digest_Distribution.py",
    "41_Alerts_Notifications.py",
    "42_PPC_Live.py",
}

def strip_num(name:str)->str:
    return re.sub(r'^[0-9]+_', '', name)

def apply_plan(pages_dir):
    files = [f for f in os.listdir(pages_dir) if f.endswith(".py")]
    changes = []

    # Map canonical bases
    canon_bases = {strip_num(c): c for c in CANONICAL}

    # Rename to canonical
    for f in files:
        base = strip_num(f)
        if base in canon_bases:
            target = canon_bases[base]
            if f != target:
                changes.append(("rename", f, target))

    # Disable admin-only + extras
    for f in files:
        if f in ADMIN_ONLY:
            changes.append(("disable", f, "_" + f + ".disabled"))
        else:
            base = strip_num(f)
            if base not in canon_bases:
                changes.append(("disable", f, "_" + f + ".disabled"))

    # Apply changes
    for op, src, dst in changes:
        src_path = os.path.join(pages_dir, src)
        dst_path = os.path.join(pages_dir, dst)
        if not os.path.exists(src_path):
            continue
        if op == "rename":
            os.rename(src_path, dst_path)
            print(f"RENAMED: {src} -> {dst}")
        elif op == "disable":
            os.rename(src_path, dst_path)
            print(f"DISABLED: {src} -> {dst}")
    if not changes:
        print("No changes needed. Already clean.")

def main():
    root = os.getcwd()
    pages_dir = os.path.join(root, "pages")
    if not os.path.isdir(pages_dir):
        print("No 'pages' directory found.")
        sys.exit(1)
    apply_plan(pages_dir)

if __name__ == "__main__":
    main()
