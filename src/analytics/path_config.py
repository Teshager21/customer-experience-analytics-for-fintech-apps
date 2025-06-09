"""
Common path configuration shared across scripts.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]  # Adjust if deeper
DATA_DIR = BASE_DIR / "data"
SCHEMA_FILE = BASE_DIR / "db" / "schema.sql"
DB_DIR = BASE_DIR / "db"
