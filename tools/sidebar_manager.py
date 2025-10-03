#!/usr/bin/env python3
"""
Sidebar & Roles Manager
- Applies a canonical sidebar order by renaming files in /pages with numeric prefixes.
- Can switch between ADMIN and VIEWER modes by disabling admin-only pages with a leading "_" and ".disabled".
- Dry-run by default; pass --apply to perform changes.

Usage:
  python tools/sidebar_manager.py --apply --mode admin
  python tools/sidebar_manager.py --apply --mode viewer
  python tools/sidebar_manager.py              # dry run (no changes)

Notes:
- Matching ignores the current numeric prefix. It compares by "base name" (after removing leading digits + underscore).
- Unknown/extra pages are left untouched unless --strict is provided, in which case they are disabled.
"""
import argparse, os, re, sys, shutil

# Canonical order (number -> base filename)
ORDER = [
    ("00", "Home_Global_Overview.py"),
    ("01", "Data_Seed.py"),                       # optional utility
    ("10", "Product_Tracker.py"),
    ("14", "PPC_Manager_Safe.py"),
    ("15", "PPC_Import_Wizard.py"),
    ("21", "Aplus_SEO_Panel.py"),
    ("22", "Compliance_Vault_App.py"),
    ("24", "Product_Research_Scoring.py"),
    ("25", "Data_Sync.py"),                       # admin-only
    ("26", "Finance_Monthly_Export.py"),
    ("27", "Finance_Dashboard_v2.py"),
    ("33", "Finance_Heatmap.py"),
    ("36", "COGS_Manager.py"),
    ("37", "Revenue_Protection.py"),
    ("38", "Reorder_Forecast.py"),
    ("39", "Margin_Scenario.py"),
    ("34", "Daily_Digest.py"),
    ("35", "Drive_Upload_Test.py"),               # admin-only
    ("40", "Digest_Distribution.py"),             # admin-only
    ("41", "Alerts_Notifications.py"),            # admin-only
    ("42", "PPC_Live.py"),                        # admin-only
]

ADMIN_ONLY = {
    "Data_Sync.py",
    "Drive_Upload_Test.py",
    "Digest_Distribution.py",
    "Alerts_Notifications.py",
    "PPC_Live.py",
}

def strip_num(name:str)->str:
    return re.sub(r'^[0-9]+_', '', name)

def target_name(num:str, base:str)->str:
    return f"{num}_{base}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="apply changes (default dry-run)")
    ap.add_argument("--mode", choices=["admin","viewer"], default="admin", help="role mode (admin keeps all, viewer disables admin-only)")
    ap.add_argument("--strict", action="store_true", help="disable unknown extra pages in viewer mode")
    args = ap.parse_args()

    pages_dir = os.path.join(os.getcwd(), "pages")
    if not os.path.isdir(pages_dir):
        print("No 'pages' directory found.")
        sys.exit(1)

    # Build mapping from base->current full path
    files = [f for f in os.listdir(pages_dir) if f.endswith(".py") and not f.startswith("_")]
    base_to_current = {}
    for f in files:
        base = strip_num(f)
        base_to_current[base] = f

    changes = []

    # Enforce order
    for num, base in ORDER:
        tgt = target_name(num, base)
        if base in base_to_current:
            cur = base_to_current[base]
            if cur != tgt:
                src = os.path.join(pages_dir, cur)
                dst = os.path.join(pages_dir, tgt)
                changes.append(("rename", src, dst))

    # Viewer mode: disable admin-only
    if args.mode == "viewer":
        for num, base in ORDER:
            if base in ADMIN_ONLY:
                fname = target_name(num, base)
                full = os.path.join(pages_dir, fname)
                if os.path.exists(full):
                    dst = os.path.join(pages_dir, "_" + fname + ".disabled")
                    changes.append(("disable", full, dst))
        if args.strict:
            # disable unknown pages not in ORDER
            ordered_set = {target_name(num, base) for num, base in ORDER}
            for f in files:
                if f not in ordered_set:
                    src = os.path.join(pages_dir, f)
                    dst = os.path.join(pages_dir, "_" + f + ".disabled")
                    changes.append(("disable", src, dst))

    # Print plan
    if not changes:
        print("No changes needed.")
        return

    print("Planned changes:")
    for op, src, dst in changes:
        print(f" - {op.upper()}: {os.path.basename(src)} -> {os.path.basename(dst)}")

    if not args.apply:
        print("\n(Dry run) Use --apply to perform changes.")
        return

    # Apply
    for op, src, dst in changes:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if op == "rename":
            os.rename(src, dst)
        elif op == "disable":
            os.rename(src, dst)

    print("\nDone.")

if __name__ == "__main__":
    main()
