# Quick mode toggles for the cockpit sidebar
# Usage:
#   make admin   # keep all pages visible (owner view)
#   make viewer  # viewer+strict: hide admin pages and extras (team view)

.PHONY: admin viewer

admin:
	python tools/apply_sidebar_plan_admin.py

viewer:
	python tools/apply_sidebar_plan.py
