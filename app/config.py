"""
Application configuration for CarbonLoop.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("CARBONLOOP_DB_PATH", str(BASE_DIR / "carbonloop.db"))

SECRET_KEY = os.environ.get("CARBONLOOP_SECRET_KEY", "carbonloop_super_secret_audit_key_2026_sebi")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
