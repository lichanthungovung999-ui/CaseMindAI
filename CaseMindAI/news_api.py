"""
news_api.py
===========
News API Client for CaseMind AI:
- Fetches real-world investigative, crime, cybercrime, court, and missing persons news
- Reads NEWS_API_KEY securely from `.streamlit/secrets.toml` or environment
- Never hard-codes credentials
- Default geographic context is India ('India')
- Handles missing keys, invalid keys, rate limits, network timeouts, and malformed articles
- Strictly separates news intelligence from forensic case evidence
"""

import os
from typing import Dict, Any, List
import requests
import streamlit as st

CATEGORY_QUERY_MAP = {
    "Crime": "crime OR criminal incident India",
    "Cybercrime": "cybercrime OR \"cyber crime\" OR \"data breach\" India",
    "Investigation": "police investigation OR CBI OR forensic India",
    "Legal cases": "\"high court\" OR \"supreme court\" OR judicial trial India",
    "Forensics": "\"forensic science\" OR \"forensic evidence\" OR ballistics India",
    "Missing persons": "\"missing person\" OR \"missing child\" India",
    "Other": "investigation India"
}

def get_news_api_key() -> str:
    """
    Retrieve News API key securely without hardcoding:
    1. Streamlit secrets (`st.secrets["NEWS_API_KEY"]`)
    2. Direct read of `.streamlit/secrets.toml` (for offline/CLI tests)
    3. Session state (`st.session_state["news_api_key"]`)
    4. Environment variable (`NEWS_API_KEY`)
    """
    # 1. Try Streamlit secrets
    try:
        if hasattr(st, "secrets") and "NEWS_API_KEY" in st.secrets:
            key = st.secrets["NEWS_API_KEY"]
            if key and key.strip() != "your_news_api_key_here":
                return key.strip()
    except Exception:
        pass

    # 2. Try session state
    try:
        if hasattr(st, "session_state") and "news_api_key" in st.session_state:
            key = st.session_state["news_api_key"]
            if key and key.strip() != "your_news_api_key_here":
                return key.strip()
    except Exception:
        pass

    # 3. Direct read of .streamlit/secrets.toml
    try:
        base_dir = os.path.dirname(__file__)
        secrets_file = os.path.join(base_dir, ".streamlit", "secrets.toml")
        if os.path.exists(secrets_file):
            with open(secrets_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("NEWS_API_KEY"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            val = parts[1].strip().strip('"').strip("'")
                            if val and val != "your_news_api_key_here":
                                return val
    except Exception:
        pass

    # 4. Environment variable fallback
    env_key = os.environ.get("NEWS_API_KEY", "")
    if env_key and env_key.strip() != "your_news_api_key_here":
        return env_key.strip()

    return ""


def get_offline_reference_articles(category: str = "Crime") -> List[Dict[str, Any]]:
    """Curated real-format educational reference news articles for demonstration when API key is unconfigured."""
    return [
        {
            "title": "National Crime Records & Supreme Court publish digital forensics evidence directives",
            "description": "The apex court issued directions standardizing the custody chain, hash verification, and electronic forensics protocols for crime investigation nationwide.",
            "source": {"name": "Legal News India"},
            "publishedAt": "2026-09-28T10:30:00Z",
            "url": "https://sci.gov.in",
            "urlToImage": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=600&auto=format&fit=crop&q=80"
        },
        {
            "title": "State Cybercrime Police Cell recovers cloned credential drives in interstate banking fraud trail",
            "description": "Forensic cyber investigators analyzed IP routing trails and recovered unauthorized access equipment in financial cybercrime probe.",
            "source": {"name": "Cyber Forensic Chronicle"},
            "publishedAt": "2026-09-25T14:15:00Z",
            "url": "https://cybercrime.gov.in",
            "urlToImage": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=600&auto=format&fit=crop&q=80"
        },
        {
            "title": "Central Forensic Science Laboratory introduces automated ballistics striation database",
            "description": "New ballistic automated matching system links recovered crime scene shell casings with central criminal trial records.",
            "source": {"name": "National Police Journal"},
            "publishedAt": "2026-09-20T08:45:00Z",
            "url": "https://mha.gov.in",
            "urlToImage": None
        },
        {
            "title": "Interstate Missing Persons task force expands biometric identification verification",
            "description": "Police tracking unit deployed synchronized database checks across transport hubs to assist ongoing missing persons investigations.",
            "source": {"name": "National Investigation Gazette"},
            "publishedAt": "2026-09-18T11:00:00Z",
            "url": "https://mha.gov.in",
            "urlToImage": None
        }
    ]


def sanitize_articles(raw_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Validate and sanitize article records, discarding invalid or deleted entries."""
    valid_articles = []
    for item in raw_articles:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        if not title or title.strip() == "" or title.strip() == "[Removed]":
            continue

        desc = item.get("description") or "No detailed description provided by publisher."
        source_obj = item.get("source")
        source_name = source_obj.get("name") if isinstance(source_obj, dict) else "News Outlet"

        valid_articles.append({
            "title": title.strip(),
            "description": desc.strip(),
            "source": {"name": source_name or "Verified News"},
            "publishedAt": item.get("publishedAt", ""),
            "url": item.get("url") or "#",
            "urlToImage": item.get("urlToImage")
        })
    return valid_articles


def fetch_investigation_news(query: str = "", category: str = "Crime") -> Dict[str, Any]:
    """
    Fetch news from NewsAPI.org based on keywords and forensic category.
    Returns:
        {
            "status": "ok" | "no_key" | "invalid_key" | "rate_limited" | "error",
            "articles": List[Dict],
            "total_results": int,
            "message": str
        }
    """
    api_key = get_news_api_key()

    # Case 1: Missing API Key
    if not api_key:
        ref_articles = get_offline_reference_articles(category)
        filtered = ref_articles
        if query and query.strip():
            q_lower = query.strip().lower()
            matched = [
                a for a in ref_articles
                if q_lower in a["title"].lower() or q_lower in a["description"].lower()
            ]
            # If query matched specific items, use them; otherwise provide educational reference list
            filtered = matched if matched else ref_articles
        return {
            "status": "no_key",
            "articles": filtered,
            "total_results": len(filtered),
            "message": "NEWS_API_KEY is not configured in .streamlit/secrets.toml. Displaying educational reference reports."
        }

    # Case 2: Live Query with Real API Key
    try:
        url = "https://newsapi.org/v2/everything"
        category_term = CATEGORY_QUERY_MAP.get(category, "crime OR investigation India")

        if query and query.strip():
            full_query = f"({query.strip()}) AND ({category_term})"
        else:
            full_query = category_term

        params = {
            "q": full_query,
            "sortBy": "publishedAt",
            "pageSize": 12,
            "language": "en",
            "apiKey": api_key
        }

        resp = requests.get(url, params=params, timeout=10)

        # HTTP Status Handling
        if resp.status_code == 200:
            data = resp.json()
            raw_articles = data.get("articles", [])
            clean_articles = sanitize_articles(raw_articles)
            return {
                "status": "ok",
                "articles": clean_articles,
                "total_results": len(clean_articles),
                "message": f"Successfully retrieved {len(clean_articles)} verified articles."
            }

        elif resp.status_code == 401:
            return {
                "status": "invalid_key",
                "articles": [],
                "total_results": 0,
                "message": "Invalid NewsAPI key. Please check your credentials in .streamlit/secrets.toml."
            }

        elif resp.status_code == 429:
            return {
                "status": "rate_limited",
                "articles": [],
                "total_results": 0,
                "message": "NewsAPI rate limit reached (free tier allows 100 requests per 24 hours)."
            }

        else:
            err_msg = resp.json().get("message", f"HTTP {resp.status_code}") if resp.text else f"HTTP {resp.status_code}"
            return {
                "status": "error",
                "articles": [],
                "total_results": 0,
                "message": f"News API error: {err_msg}"
            }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "articles": [],
            "total_results": 0,
            "message": "Connection to News API timed out. Please check your internet connection."
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "articles": [],
            "total_results": 0,
            "message": f"Network error querying News API: {str(e)}"
        }

    except Exception as e:
        return {
            "status": "error",
            "articles": [],
            "total_results": 0,
            "message": f"Unexpected error: {str(e)}"
        }
