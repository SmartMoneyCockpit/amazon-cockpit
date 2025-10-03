#!/usr/bin/env python3
import os

TARGET = "pages/09_Dashboard_Overview.py"

def main():
    base = os.getcwd()
    full = os.path.join(base, TARGET)
    if os.path.exists(full):
        new = full.replace("pages/09_Dashboard_Overview.py", "pages/_09_Dashboard_Overview.py.disabled")
        os.rename(full, new)
        print(f"Disabled legacy dashboard overview: {new}")
    else:
        print("Target not found, nothing to disable.")

if __name__ == "__main__":
    main()
