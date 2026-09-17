"""
Database layer for CarbonLoop using SQLite with multi-tenant data isolation.
Enforces audit logs and traceable relation records.
"""

import sqlite3
from typing import Generator
from app.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Organizations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS organizations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        industry TEXT NOT NULL,
        country TEXT NOT NULL,
        state TEXT NOT NULL,
        employee_count INTEGER NOT NULL DEFAULT 1,
        facility_sqft REAL NOT NULL DEFAULT 1000.0,
        baseline_year INTEGER NOT NULL DEFAULT 2023,
        is_synthetic INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'analyst',
        org_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE
    )
    """)

    # 3. Activities
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id TEXT PRIMARY KEY,
        org_id TEXT NOT NULL,
        user_id TEXT,
        activity_date TEXT NOT NULL,
        scope TEXT NOT NULL,
        category TEXT NOT NULL,
        activity_type TEXT NOT NULL,
        activity_value REAL,
        activity_unit TEXT NOT NULL,
        data_quality TEXT NOT NULL DEFAULT 'USER_ENTERED',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE
    )
    """)

    # 4. Calculations (Immutable 1-to-1 deterministic result of an activity)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calculations (
        id TEXT PRIMARY KEY,
        activity_id TEXT UNIQUE NOT NULL,
        org_id TEXT NOT NULL,
        factor_id TEXT NOT NULL,
        factor_value REAL NOT NULL,
        co2e_kg REAL NOT NULL,
        co2e_tonnes REAL NOT NULL,
        formula TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'CALCULATED',
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE,
        FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE
    )
    """)

    # 5. Reduction Scenarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scenarios (
        id TEXT PRIMARY KEY,
        org_id TEXT NOT NULL,
        name TEXT NOT NULL,
        solar_share_pct REAL NOT NULL DEFAULT 0.0,
        hvac_temp_offset_c REAL NOT NULL DEFAULT 0.0,
        transit_shift_pct REAL NOT NULL DEFAULT 0.0,
        flight_reduction_pct REAL NOT NULL DEFAULT 0.0,
        waste_composting_pct REAL NOT NULL DEFAULT 0.0,
        projected_annual_reduction_kg REAL NOT NULL DEFAULT 0.0,
        projected_residual_co2e_kg REAL NOT NULL DEFAULT 0.0,
        classification TEXT NOT NULL DEFAULT 'SIMULATION/PROJECTION',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE
    )
    """)

    # 6. Targets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS targets (
        id TEXT PRIMARY KEY,
        org_id TEXT NOT NULL,
        target_name TEXT NOT NULL,
        baseline_year INTEGER NOT NULL,
        target_year INTEGER NOT NULL,
        target_reduction_pct REAL NOT NULL,
        target_co2e_kg REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE
    )
    """)

    # 7. Audit History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        org_id TEXT NOT NULL,
        user_id TEXT,
        action TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (org_id) REFERENCES organizations (id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
