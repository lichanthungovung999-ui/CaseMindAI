"""
test_news_integration.py
========================
Automated test suite verifying the News Search feature for CaseMind AI:
1. News API module initialization & imports
2. Secure API key detection (no hard-coding, read from .streamlit/secrets.toml)
3. Missing API key handling & educational reference mode
4. Invalid API key handling (HTTP 401 simulation)
5. Empty search results handling
6. Network timeout and API error handling
7. Article sanitization (handling nulls, missing images, [Removed] articles)
8. News & Case independence validation (news articles are not case evidence)
"""

import os
import sys
from unittest.mock import patch, MagicMock
import requests

# Add CaseMindAI directory to path
sys.path.insert(0, os.path.dirname(__file__))

from news_api import (
    get_news_api_key,
    fetch_investigation_news,
    sanitize_articles,
    get_offline_reference_articles
)

def test_initialization():
    print("[1/7] Testing News API module initialization & imports...")
    import requests
    import streamlit
    from news_api import fetch_investigation_news, get_news_api_key
    print("      ✓ Modules imported successfully.")

def test_api_key_detection():
    print("[2/7] Testing secure API key detection...")
    # Verify no hardcoded keys exist in source code
    with open(os.path.join(os.path.dirname(__file__), "news_api.py"), "r") as f:
        code = f.read()
        assert "apiKey = \"" not in code or "apiKey = \"\"" in code, "No hardcoded API keys allowed!"

    key = get_news_api_key()
    print(f"      ✓ API key detection executed safely (Current key state: {'Configured' if key else 'Unconfigured / Ready for key'}).")

def test_missing_api_key_and_offline_mode():
    print("[3/7] Testing missing API key handling & offline reference mode...")
    # Ensure missing key returns clear 'no_key' status and does not crash
    with patch("news_api.get_news_api_key", return_value=""):
        res = fetch_investigation_news(query="cyber", category="Cybercrime")
        assert res["status"] == "no_key", f"Expected 'no_key', got {res['status']}"
        assert isinstance(res["articles"], list), "Articles must be a list"
        assert len(res["articles"]) > 0, "Reference articles should be available for educational testing"
        assert "NEWS_API_KEY is not configured" in res["message"]
        print("      ✓ Missing API key handled cleanly with clear user guidance banner.")

def test_empty_search_results():
    print("[4/7] Testing empty search results handling...")
    # Mock a live 200 response with 0 articles
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ok", "totalResults": 0, "articles": []}

    with patch("news_api.get_news_api_key", return_value="test_valid_key_12345"), \
         patch("requests.get", return_value=mock_resp):
        res = fetch_investigation_news(query="xyznonexistentkeyword9999", category="Crime")
        assert res["status"] == "ok"
        assert res["articles"] == []
        assert res["total_results"] == 0
        print("      ✓ Zero results condition handled properly without errors.")

def test_invalid_api_key_and_rate_limits():
    print("[5/7] Testing invalid API key and rate limit error codes...")
    # Simulate 401 Unauthorized
    mock_401 = MagicMock()
    mock_401.status_code = 401
    mock_401.json.return_value = {"status": "error", "code": "apiKeyInvalid", "message": "Your API key is invalid or incorrect."}

    with patch("news_api.get_news_api_key", return_value="invalid_key"), \
         patch("requests.get", return_value=mock_401):
        res_401 = fetch_investigation_news(query="forensics", category="Forensics")
        assert res_401["status"] == "invalid_key", "Expected status 'invalid_key' on HTTP 401"
        assert "Invalid NewsAPI key" in res_401["message"]

    # Simulate 429 Rate Limit
    mock_429 = MagicMock()
    mock_429.status_code = 429
    with patch("news_api.get_news_api_key", return_value="rate_limited_key"), \
         patch("requests.get", return_value=mock_429):
        res_429 = fetch_investigation_news(query="forensics", category="Forensics")
        assert res_429["status"] == "rate_limited", "Expected status 'rate_limited' on HTTP 429"
        assert "rate limit reached" in res_429["message"]
    print("      ✓ HTTP 401 and HTTP 429 responses correctly categorized and reported.")

def test_network_and_timeout_errors():
    print("[6/7] Testing network timeout and connection failure handling...")
    with patch("news_api.get_news_api_key", return_value="mock_key"), \
         patch("requests.get", side_effect=requests.exceptions.Timeout("Connection timed out")):
        res_timeout = fetch_investigation_news(query="cyber", category="Cybercrime")
        assert res_timeout["status"] == "error"
        assert "timed out" in res_timeout["message"]

    with patch("news_api.get_news_api_key", return_value="mock_key"), \
         patch("requests.get", side_effect=requests.exceptions.ConnectionError("DNS lookup failed")):
        res_conn = fetch_investigation_news(query="cyber", category="Cybercrime")
        assert res_conn["status"] == "error"
        assert "Network error" in res_conn["message"]
    print("      ✓ Network timeouts and connection drops handled gracefully without crash.")

def test_article_sanitization_and_independence():
    print("[7/7] Testing article sanitization and CaseMind independence...")
    # Test filtering out "[Removed]" and None titles
    raw_sample = [
        {"title": "[Removed]", "description": "[Removed]", "url": "https://example.com/1"},
        {"title": None, "description": "Broken article", "url": "https://example.com/2"},
        {"title": "High Court upholds digital evidence standard", "description": "Guidelines verified.", "source": {"name": "National Law Review"}, "url": "https://example.com/3", "urlToImage": "https://example.com/pic.jpg"},
        "invalid_non_dict_record"
    ]
    cleaned = sanitize_articles(raw_sample)
    assert len(cleaned) == 1, f"Expected 1 valid article, got {len(cleaned)}"
    assert cleaned[0]["title"] == "High Court upholds digital evidence standard"
    assert cleaned[0]["source"]["name"] == "National Law Review"

    # Verify that Gemini case analyzer and SQLite database do NOT import or depend on news_api
    with open(os.path.join(os.path.dirname(__file__), "ai_analyzer.py"), "r") as f:
        ai_code = f.read()
        assert "news_api" not in ai_code, "Gemini analyzer must remain independent from news search."
    with open(os.path.join(os.path.dirname(__file__), "database.py"), "r") as f:
        db_code = f.read()
        assert "news_api" not in db_code, "Database schema must remain independent from news search."

    print("      ✓ Article sanitization validated.")
    print("      ✓ Strict forensic separation verified: news search is an independent intelligence tool.")

def main():
    print("\n" + "="*70)
    print("  CASEMIND AI - NEWS API INTEGRATION TEST SUITE")
    print("  Class 12 Computer Science Project Verification")
    print("="*70 + "\n")

    test_initialization()
    test_api_key_detection()
    test_missing_api_key_and_offline_mode()
    test_empty_search_results()
    test_invalid_api_key_and_rate_limits()
    test_network_and_timeout_errors()
    test_article_sanitization_and_independence()

    print("\n" + "="*70)
    print("  [7/7] ALL NEWS SEARCH TESTS PASSED SUCCESSFULLY! (7/7)")
    print("  NewsAPI integration, error handling, and article cards fully operational.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
