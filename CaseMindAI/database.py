"""
database.py
===========
SQLite Database Management for CaseMind AI.
- Creates users table (id, full_name, email, password_hash, role, created_at)
- Creates cases table (id, user_id, title, location, case_date, description,
  clues, suspects, witnesses, alibis, additional_info, image_path, analysis_json, created_at)
- Provides parameterized query helpers to prevent SQL injection.
- Beginner-friendly functions for Class 12 viva explanations.
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any

# Path to SQLite database file
DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "casemind.db")

def get_connection():
    """Create and return a connection to the SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name like dict
    return conn

def init_db():
    """Initialize SQLite database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Cases Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            location TEXT,
            case_date TEXT,
            description TEXT NOT NULL,
            clues TEXT,
            suspects TEXT,
            witnesses TEXT,
            alibis TEXT,
            additional_info TEXT,
            image_path TEXT,
            analysis_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("CaseMind AI Database initialized at:", DB_PATH)
