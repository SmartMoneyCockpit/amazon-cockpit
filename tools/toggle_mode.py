#!/usr/bin/env python3
import argparse, os, sys, subprocess

def run(cmd):
    print(">>", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(r.returncode)

def main():
    ap = argparse.ArgumentParser(description="Toggle cockpit mode: admin or viewer.")
    ap.add_argument("mode", choices=["admin","viewer"], help="Target mode")
    args = ap.parse_args()

    root = os.getcwd()
    tools = os.path.join(root, "tools")
    admin_script = os.path.join(tools, "apply_sidebar_plan_admin.py")
    viewer_script = os.path.join(tools, "apply_sidebar_plan.py")

    if args.mode == "admin":
        if not os.path.exists(admin_script):
            print("Missing tools/apply_sidebar_plan_admin.py (Day-21 admin).")
            sys.exit(1)
        run([sys.executable, admin_script])
    else:
        if not os.path.exists(viewer_script):
            print("Missing tools/apply_sidebar_plan.py (viewer+strict).")
            sys.exit(1)
        run([sys.executable, viewer_script])

    print("\nDone. Commit and redeploy to apply sidebar changes.")

if __name__ == "__main__":
    main()
