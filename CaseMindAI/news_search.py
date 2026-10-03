"""
news_search.py
==============
News Search Screen for CaseMind AI:
- Queries real-time legal, crime, forensics, and investigation news (Context: India)
- Reads credentials securely from `.streamlit/secrets.toml`
- Displays Article Title, Source, Publication Date, Description, Image, and Read More Link
- Provides clean handling for Missing Key, Invalid Key, Rate Limits, and Empty States
- Strictly maintains separation: News reports are research intelligence, NEVER automatic case evidence
"""

import streamlit as st
from news_api import fetch_investigation_news, get_news_api_key
from utils import format_timestamp

def show_news_search():
    """Render the News Intelligence Search screen matching Google Stitch UI."""
    # Screen Header
    st.markdown("""
    <div class="brand-header">
        <div>
            <div style="font-size: 20px; font-weight: 700; color: #f8fafc;">
                📰 Legal & Forensic News Intelligence
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
                Live crime, cyber forensics, and judicial developments (Context: India).
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mandatory Independence Notice
    st.markdown("""
    <div class="cm-notice">
        <strong>⚖️ Intelligence Advisory:</strong> External news articles are provided solely for background research and context.
        They are strictly separated from CaseMind AI case dossiers and are <strong>never automatically admitted as verified evidence</strong> in any case analysis.
    </div>
    """, unsafe_allow_html=True)

    # API Key Configuration Check & Guidance
    api_key = get_news_api_key()
    if not api_key:
        st.info(
            "ℹ️ **NEWS_API_KEY is not configured.**\n\n"
            "To enable live worldwide news queries, create a free API key at [newsapi.org](https://newsapi.org) "
            "and add it to `CaseMindAI/.streamlit/secrets.toml` as:\n\n"
            "```toml\nNEWS_API_KEY = \"your_news_api_key_here\"\n```\n"
            "*(Currently displaying verified offline reference forensic reports for testing and evaluation.)*"
        )

    # Search Bar & Filter Options
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "Search Keyword or Topic",
            placeholder="e.g. cyber theft, forensic laboratory, CBI chargesheet, high court...",
            key="news_query_input"
        )
    with col2:
        category = st.selectbox(
            "Forensic Category",
            ["Crime", "Cybercrime", "Investigation", "Legal cases", "Forensics", "Missing persons", "Other"],
            index=0,
            key="news_category_select"
        )

    search_clicked = st.button("🔍 Search Intelligence Feeds", use_container_width=True)

    # Always fetch on button click or default initial load
    if search_clicked or "last_news_result" not in st.session_state:
        with st.spinner("Fetching verified legal and crime intelligence..."):
            result = fetch_investigation_news(query=query, category=category)
            st.session_state["last_news_result"] = result
            st.session_state["last_news_query"] = query
            st.session_state["last_news_category"] = category
    else:
        result = st.session_state.get("last_news_result", {})

    status = result.get("status", "ok")
    articles = result.get("articles", [])
    message = result.get("message", "")

    # Status-Specific UI Handling
    if status == "invalid_key":
        st.error(f"❌ Authentication Failed: {message}")
        return

    if status == "rate_limited":
        st.warning(f"⚠️ Usage Notice: {message}")
        return

    if status == "error":
        st.error(f"⚠️ Network / Service Error: {message}")
        return

    # Results Display
    if not articles:
        st.markdown(f"""
        <div class="cm-card" style="text-align: center; padding: 30px;">
            <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
            <div style="font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 4px;">
                No News Articles Found
            </div>
            <div style="font-size: 13px; color: #94a3b8;">
                No verified articles matched your query '<strong>{query}</strong>' under '<strong>{category}</strong>'.
                Try using broader keywords or selecting a different category.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.write(f"Displaying **{len(articles)}** verified report(s) (Region Context: **India**):")

    for idx, item in enumerate(articles):
        title = item.get("title", "Untitled")
        desc = item.get("description", "No description provided.")
        source = item.get("source", {}).get("name", "Verified News")
        pub_date = format_timestamp(item.get("publishedAt", ""))
        url = item.get("url", "#")
        img_url = item.get("urlToImage")

        with st.container():
            st.markdown(f"""
            <div class="cm-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <span class="cm-badge cm-badge-blue" style="background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.4); color: #93c5fd; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;">
                        {source}
                    </span>
                    <span style="font-size: 11px; color: #94a3b8;">{pub_date}</span>
                </div>
                <div style="font-size: 16px; font-weight: 700; color: #f8fafc; margin-bottom: 8px; line-height: 1.4;">
                    {title}
                </div>
                <div style="font-size: 13px; color: #cbd5e1; line-height: 1.5; margin-bottom: 12px;">
                    {desc}
                </div>
            """, unsafe_allow_html=True)

            # Display Image if available
            if img_url:
                try:
                    st.image(img_url, caption=f"Photo Source: {source}", use_container_width=True)
                except Exception:
                    pass

            st.markdown(f"""
                <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid #1e293b;">
                    <a href="{url}" target="_blank" style="text-decoration: none; color: #60a5fa; font-weight: 600; font-size: 13px;">
                        Read Full Article on Publisher Website ↗
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
