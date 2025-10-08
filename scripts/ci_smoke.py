#!/usr/bin/env python3
import os, sys, ast, yaml

EXCLUDE_DIRS = {'.git', '.github', '.venv', 'venv', '__pycache__'}

def py_files(root='.'):
    for r, dnames, fnames in os.walk(root):
        dnames[:] = [d for d in dnames if d not in EXCLUDE_DIRS]
        for f in fnames:
            if f.endswith('.py'):
                yield os.path.join(r, f)

def yaml_files(root='tools'):
    if not os.path.isdir(root):
        return []
    out = []
    for f in os.listdir(root):
        if f.endswith('.yaml') or f.endswith('.yml'):
            out.append(os.path.join(root, f))
    return out

def main():
    errors = []
    # Syntax check
    for p in py_files('.'):
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fh:
                src = fh.read()
            ast.parse(src, filename=p)
        except Exception as e:
            errors.append(f"PY SYNTAX: {p}: {e}")
    # YAML sanity
    for y in yaml_files('tools'):
        try:
            with open(y, 'r', encoding='utf-8') as fh:
                data = yaml.safe_load(fh) or {}
        except Exception as e:
            errors.append(f"YAML READ: {y}: {e}")
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("CI SMOKE: OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
