"""
auth.py
=======
Authentication logic for CaseMind AI:
- Secure password hashing using Python hashlib (SHA-256 with salt)
- User registration with validation
- User login authentication against SQLite database
- Session state management for logged-in user
"""

import hashlib
import sqlite3
import streamlit as st
from typing import Optional, Dict, Any
from database import get_connection

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 for secure storage."""
    # Salt adds protection against pre-computed rainbow tables
    salt = "casemind_secure_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if a plain text password matches the stored hash."""
    return hash_password(plain_password) == hashed_password

def register_user(full_name: str, email: str, password: str, role: str) -> tuple[bool, str]:
    """Register a new user in SQLite with parameterized queries."""
    if not full_name.strip():
        return False, "Full Name is required."
    if not email.strip() or "@" not in email:
        return False, "Please enter a valid email address."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    pwd_hash = hash_password(password)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES (?, ?, ?, ?);
        """, (full_name.strip(), email.strip().lower(), pwd_hash, role))
        conn.commit()
        conn.close()
        return True, "Registration successful! You can now log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except Exception as e:
        return False, f"Registration error: {str(e)}"

def login_user(email: str, password: str) -> tuple[bool, Optional[Dict[str, Any]], str]:
    """Authenticate user credentials and return user dict if valid."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, full_name, email, password_hash, role, created_at
        FROM users
        WHERE email = ?;
    """, (email.strip().lower(),))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row:
        return False, None, "Invalid email or password."

    if verify_password(password, user_row["password_hash"]):
        user_dict = {
            "id": user_row["id"],
            "full_name": user_row["full_name"],
            "email": user_row["email"],
            "role": user_row["role"],
            "created_at": user_row["created_at"]
        }
        return True, user_dict, "Login successful!"
    return False, None, "Invalid email or password."
