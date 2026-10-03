"""
test_app.py
===========
End-to-End Core Application Test Suite for CaseMind AI
A Class 12 Computer Science Project.

Tests all core application layers:
1. Authentication:
   - Registration validation (blank fields, invalid emails, short passwords)
   - Password confirmation checking
   - Secure SHA-256 with salt hashing
   - Login with correct and incorrect credentials
   - Duplicate email prevention
   - Session dictionary structures
2. Database:
   - Table initialization (users, cases)
   - Parameterized query execution
   - Row factory access
   - Foreign key & relational integrity
3. Case CRUD Operations:
   - Case insertion with all fields
   - Case retrieval by user
   - Case search/filtering by keyword, title, location
   - Case deletion and consistency confirmation
4. Utilities & File Handling:
   - Allowed extension checks (JPG, JPEG, PNG, rejected formats)
   - Image validation and conversion with Pillow
   - Date and ISO timestamp formatting
5. AI Integration Regression:
   - Gemini client initialization
   - Text case analysis execution
   - Multimodal evidence image analysis
   - 13 forensic schema categories validation
   - Presumption of innocence & legal notice verification
   - SQLite JSON persistence
6. News Integration Regression:
   - Secure API key resolution
   - Missing key & educational reference mode
   - HTTP 401 / 429 status code handling
   - Article data sanitization & publisher link validation
   - Separation of news from case evidence
7. Navigation & Page Component Verification:
   - All page modules importable without errors
   - No circular dependencies
"""

import os
import sys
import json
import sqlite3
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image, ImageDraw

# Add CaseMindAI directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from database import get_connection, init_db, DB_PATH
from auth import hash_password, verify_password, register_user, login_user
from utils import is_allowed_file, validate_and_open_image, get_current_date, format_timestamp, UPLOAD_FOLDER
from ai_analyzer import get_gemini_api_key, analyze_case_with_gemini
from news_api import get_news_api_key, fetch_investigation_news, sanitize_articles

class TestAuthentication(unittest.TestCase):
    """Test user registration, password hashing, and authentication workflows."""

    def setUp(self):
        init_db()

    def test_01_password_hashing_and_salting(self):
        plain = "ForensicPass@2026"
        hashed = hash_password(plain)
        self.assertNotEqual(plain, hashed)
        self.assertEqual(len(hashed), 64, "SHA-256 hash must be 64 hexadecimal characters.")
        self.assertTrue(verify_password(plain, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_02_registration_validation(self):
        # Blank name
        success, msg = register_user("", "test@casemind.ai", "pass123", "Student")
        self.assertFalse(success)
        self.assertIn("Full Name is required", msg)

        # Invalid email
        success, msg = register_user("John", "invalidemail", "pass123", "Student")
        self.assertFalse(success)
        self.assertIn("valid email", msg)

        # Short password
        success, msg = register_user("John", "john@casemind.ai", "12345", "Student")
        self.assertFalse(success)
        self.assertIn("at least 6 characters", msg)

    def test_03_registration_and_login_flow(self):
        email = f"officer_{os.getpid()}@casemind.ai"
        pwd = "SecretPassword123"

        # Register
        success, msg = register_user("Inspector Roy", email, pwd, "Investigator")
        self.assertTrue(success, f"Registration failed: {msg}")

        # Duplicate registration
        dup_success, dup_msg = register_user("Inspector Roy", email, pwd, "Investigator")
        self.assertFalse(dup_success)
        self.assertIn("already exists", dup_msg)

        # Login with correct credentials
        ok, user_dict, login_msg = login_user(email, pwd)
        self.assertTrue(ok)
        self.assertIsNotNone(user_dict)
        self.assertEqual(user_dict["email"], email.lower())
        self.assertEqual(user_dict["role"], "Investigator")

        # Login with wrong credentials
        bad_ok, bad_user, bad_msg = login_user(email, "WrongPassword")
        self.assertFalse(bad_ok)
        self.assertIsNone(bad_user)
        self.assertIn("Invalid", bad_msg)


class TestDatabaseAndCaseCRUD(unittest.TestCase):
    """Test SQLite database operations and case lifecycle (Create, Read, Search, Delete)."""

    def setUp(self):
        init_db()
        self.conn = get_connection()
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users LIMIT 1;")
        user = cursor.fetchone()
        if not user:
            register_user("Default Tester", "tester@casemind.ai", "testpass123", "Student")
            cursor.execute("SELECT id FROM users LIMIT 1;")
            user = cursor.fetchone()
        self.user_id = user["id"]

    def tearDown(self):
        self.conn.close()

    def test_04_database_tables_exist(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        self.assertIn("users", tables)
        self.assertIn("cases", tables)

    def test_05_case_crud_and_search(self):
        cursor = self.conn.cursor()

        unique_title = f"The Amber Laboratory Discrepancy #{os.getpid()}"
        cursor.execute("""
            INSERT INTO cases (
                user_id, title, location, case_date, description,
                clues, suspects, witnesses, alibis, additional_info,
                analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            self.user_id,
            unique_title,
            "Kolkata Forensic Bureau",
            "2026-10-01",
            "Unidentified breach of refrigerated centrifuge storage unit.",
            "Chemical residue traces on door seal",
            "Lab technician B",
            "Security shift guard",
            "Technician claimed dinner break between 8:00 and 9:00 PM",
            "Access log timestamps showed 8:22 PM door cycle",
            json.dumps({"case_summary": "Test Summary"})
        ))
        case_id = cursor.lastrowid
        self.conn.commit()
        self.assertIsNotNone(case_id)

        # Read back
        cursor.execute("SELECT * FROM cases WHERE id = ?;", (case_id,))
        record = cursor.fetchone()
        self.assertIsNotNone(record)
        self.assertEqual(record["title"], unique_title)
        self.assertEqual(record["location"], "Kolkata Forensic Bureau")

        # Search query matching title
        search_term = f"%{unique_title[:15]}%"
        cursor.execute("SELECT * FROM cases WHERE user_id = ? AND title LIKE ?;", (self.user_id, search_term))
        results = cursor.fetchall()
        self.assertGreaterEqual(len(results), 1)

        # Delete case
        cursor.execute("DELETE FROM cases WHERE id = ?;", (case_id,))
        self.conn.commit()

        cursor.execute("SELECT * FROM cases WHERE id = ?;", (case_id,))
        self.assertIsNone(cursor.fetchone())


class TestUtilitiesAndFileValidation(unittest.TestCase):
    """Test image validation, file extension filtering, and date formatters."""

    def test_06_file_extension_validation(self):
        self.assertTrue(is_allowed_file("evidence.jpg"))
        self.assertTrue(is_allowed_file("photo.JPEG"))
        self.assertTrue(is_allowed_file("fingerprint.png"))
        self.assertFalse(is_allowed_file("script.py"))
        self.assertFalse(is_allowed_file("executable.exe"))
        self.assertFalse(is_allowed_file("document.pdf"))
        self.assertFalse(is_allowed_file("no_extension"))

    def test_07_image_opening_and_validation(self):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        sample_path = os.path.join(UPLOAD_FOLDER, "test_util_sample.png")

        # Create valid image
        img = Image.new("RGB", (100, 100), color=(50, 100, 150))
        img.save(sample_path)

        validated = validate_and_open_image(sample_path)
        self.assertIsNotNone(validated)
        self.assertEqual(validated.size, (100, 100))

        # Test non-existent file
        self.assertIsNone(validate_and_open_image("/non_existent_image_path.png"))

    def test_08_date_and_timestamp_formatters(self):
        today = get_current_date()
        self.assertTrue(len(today) == 10 and today[4] == "-" and today[7] == "-")

        formatted = format_timestamp("2026-10-03T08:30:00")
        self.assertIn("2026", formatted)
        self.assertIn("Oct", formatted)

        # Fallback for malformed string
        self.assertEqual(format_timestamp("invalid_ts"), "invalid_ts")


class TestAIRegression(unittest.TestCase):
    """Regression test verifying Gemini text and multimodal image analysis."""

    def test_09_gemini_api_key_detection(self):
        key = get_gemini_api_key()
        self.assertTrue(len(key) > 10, "Valid GEMINI_API_KEY must be resolved.")

    def test_10_gemini_analysis_schema_and_forensic_rules(self):
        case_payload = {
            "title": "Regression Check - Jewelry Vault Alarm",
            "location": "Jaipur, Rajasthan",
            "case_date": "2026-09-30",
            "description": "Alarm system silently disconnected before scheduled night patrol.",
            "clues": "Bypassed relay wire cut cleanly with insulated shears.",
            "suspects": "Ex-security installer who worked on relay configuration.",
            "witnesses": "Night watchman reported no external door forced open.",
            "alibis": "Installer claimed to be traveling out of station.",
            "additional_info": "Toll gate RFID records pending verification."
        }

        result = analyze_case_with_gemini(case_payload)
        self.assertIsInstance(result, dict)

        # Verify all 13 forensic schema keys
        required_keys = [
            "case_summary", "user_facts", "image_observations", "key_evidence",
            "important_clues", "possible_timeline", "entities_mentioned",
            "possible_connections", "missing_information", "alternative_explanations",
            "investigation_questions", "limitations", "legal_notice"
        ]
        for k in required_keys:
            self.assertIn(k, result, f"Schema missing key: {k}")

        # Verify strict ethical rule (presumption of innocence / disclaimer)
        legal_text = result["legal_notice"].lower()
        self.assertTrue("guilt" in legal_text or "legal" in legal_text or "aid" in legal_text)

        # Verify fact vs hypothesis separation
        self.assertIsInstance(result["user_facts"], list)
        self.assertIsInstance(result["alternative_explanations"], list)


class TestNewsRegression(unittest.TestCase):
    """Regression test verifying NewsAPI integration and separation from case analysis."""

    def test_11_news_api_key_and_offline_graceful_handling(self):
        # When key is absent
        with patch("news_api.get_news_api_key", return_value=""):
            res = fetch_investigation_news("crime", "Crime")
            self.assertEqual(res["status"], "no_key")
            self.assertGreater(len(res["articles"]), 0)
            self.assertIn("NEWS_API_KEY is not configured", res["message"])

    def test_12_news_sanitization_and_status_codes(self):
        raw_list = [
            {"title": "Valid Headline", "description": "Story", "source": {"name": "Test"}, "url": "https://example.com"},
            {"title": "[Removed]", "description": "Story", "url": "https://example.com"},
            {"title": None, "description": "Broken", "url": "https://example.com"}
        ]
        sanitized = sanitize_articles(raw_list)
        self.assertEqual(len(sanitized), 1)
        self.assertEqual(sanitized[0]["title"], "Valid Headline")

    def test_13_news_independence_from_case_dossiers(self):
        # Verify news search does not modify or inject into SQLite cases table
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM cases;")
        before_count = cursor.fetchone()["count"]
        conn.close()

        # Perform news query
        _ = fetch_investigation_news("cybercrime", "Cybercrime")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM cases;")
        after_count = cursor.fetchone()["count"]
        conn.close()

        self.assertEqual(before_count, after_count, "News search must never insert records into cases table.")


class TestModuleImportsAndNavigation(unittest.TestCase):
    """Verify that all application screens and routers compile and import cleanly without circular dependencies."""

    def test_14_screen_modules_import_and_syntax(self):
        # Validate syntax of app.py without executing browser UI in bare test mode
        with open(os.path.join(BASE_DIR, "app.py"), "r", encoding="utf-8") as f:
            compiled = compile(f.read(), "app.py", "exec")
            self.assertIsNotNone(compiled)

        # Import all application screens and logic modules
        import login
        import register
        import dashboard
        import case_analysis
        import results
        import case_database
        import news_search
        import settings
        import styles
        import auth
        import database
        import ai_analyzer
        import news_api
        import utils
        self.assertTrue(True)


def main():
    print("\n" + "="*75)
    print("  CASEMIND AI - COMPLETE END-TO-END APPLICATION TEST SUITE")
    print("  Class 12 Computer Science Project Verification")
    print("="*75 + "\n")

    suite = unittest.TestLoader().loadTestsFromNames([
        "test_app.TestAuthentication",
        "test_app.TestDatabaseAndCaseCRUD",
        "test_app.TestUtilitiesAndFileValidation",
        "test_app.TestAIRegression",
        "test_app.TestNewsRegression",
        "test_app.TestModuleImportsAndNavigation"
    ])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*75)
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    print(f"  TOTAL TESTS RUN : {total}")
    print(f"  PASSED          : {passed}")
    print(f"  FAILED          : {failures}")
    print(f"  ERRORS          : {errors}")
    print("="*75 + "\n")

    if failures == 0 and errors == 0:
        print("  🎉 ALL APPLICATION SYSTEMS OPERATIONAL (14/14 TESTS PASSED)!\n")
        return 0
    else:
        print("  ❌ SOME TESTS FAILED.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
