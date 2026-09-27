"""
FlowMind AI — Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Gemini ───────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    try:
        import streamlit as st
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        pass
GEMINI_MODEL = "gemini-2.5-flash"

# ─── Database ─────────────────────────────────────────────────────────────────
DB_PATH = os.path.join("data", "flowmind.db")

# ─── App ──────────────────────────────────────────────────────────────────────
APP_NAME = "FlowMind AI"
APP_TAGLINE = "Turn messy business messages into organized work."
APP_VERSION = "1.0.0"

# ─── Task Config ──────────────────────────────────────────────────────────────
PRIORITY_VALUES = ["LOW", "MEDIUM", "HIGH", "URGENT"]
STATUS_VALUES = ["TODO", "IN_PROGRESS", "COMPLETED"]

PRIORITY_COLORS = {
    "LOW": "#6c757d",
    "MEDIUM": "#0d6efd",
    "HIGH": "#fd7e14",
    "URGENT": "#dc3545",
}

STATUS_COLORS = {
    "TODO": "#6c757d",
    "IN_PROGRESS": "#0d6efd",
    "COMPLETED": "#198754",
}

# ─── Demo Employees ───────────────────────────────────────────────────────────
DEMO_EMPLOYEES = [
    {"name": "Rahul", "role": "Sales Manager"},
    {"name": "Neha", "role": "Inventory Lead"},
    {"name": "Amit", "role": "Accounts Executive"},
    {"name": "Priya", "role": "Operations Head"},
]
