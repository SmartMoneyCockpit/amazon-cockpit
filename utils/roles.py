import streamlit as st
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class RoleConfig:
    label: str
    tabs: List[str]          # Tabs the role can see
    default_tab: str         # Tab to open first for this role

# Define role → tabs mapping
ROLE_MAP: Dict[str, RoleConfig] = {
    "Admin": RoleConfig(
        label="👑 Admin",
        tabs=["Home","Product Tracker","PPC Manager","A+ & SEO","Compliance Vault","Finance Dashboard","Alerts Hub"],
        default_tab="Home"
    ),
    "ROI Renegades (PPC)": RoleConfig(
        label="📈 ROI Renegades (PPC)",
        tabs=["Home","PPC Manager","Finance Dashboard","Alerts Hub"],
        default_tab="PPC Manager"
    ),
    "Joanne (Compliance)": RoleConfig(
        label="🧾 Joanne (Compliance)",
        tabs=["Home","Compliance Vault","Product Tracker","Alerts Hub"],
        default_tab="Compliance Vault"
    ),
    "Faith (A+ / Creative)": RoleConfig(
        label="🧩 Faith (A+ / Creative)",
        tabs=["Home","A+ & SEO","Product Tracker","Alerts Hub"],
        default_tab="A+ & SEO"
    ),
}

def get_roles_list() -> list:
    # Allow override via secrets: roles_default (string)
    return list(ROLE_MAP.keys())

def get_role_config(name: str) -> RoleConfig:
    return ROLE_MAP.get(name, ROLE_MAP["Admin"])
