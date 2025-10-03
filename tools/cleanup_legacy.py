
#!/usr/bin/env python3
import os

TARGETS = [
    "pages/20_PPC_Manager.py",
    "pages/30_Aplus_SEO.py",
    "pages/50_Finance_Dashboard.py",
    "pages/09_Dashboard_Overview.py",
]

def disable(path):
    if os.path.exists(path):
        new = path.replace("pages/", "pages/_") + ".disabled"
        os.rename(path, new)
        return f"disabled -> {new}"
    return "not found"

def main():
    base = os.getcwd()
    results = {}
    for p in TARGETS:
        full = os.path.join(base, p)
        try:
            results[p] = disable(full)
        except Exception as e:
            results[p] = f"error: {e}"
    for k, v in results.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    main()
