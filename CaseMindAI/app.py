"""
app.py
======
CaseMind AI - Main Application Entry Point
Tagline: Analyze • Investigate • Find the Truth
A Class 12 School Computer Science Project.

Built with:
- Python
- Streamlit
- SQLite
- Google Gemini API
- News API
- Pillow
"""

import streamlit as st
from database import init_db
from styles import apply_custom_styles
from login import show_login_screen
from register import show_register_screen
from dashboard import show_dashboard
from case_analysis import show_case_analysis
from results import show_results_screen
from case_database import show_case_database
from news_search import show_news_search
from settings import show_settings

# 1. Page Configuration
st.set_page_config(
    page_title="CaseMind AI - Analyze • Investigate • Find the Truth",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize Database & Styles
init_db()
apply_custom_styles()

# 3. Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Login"

# 4. Authentication Check & Sidebar Navigation
if not st.session_state["logged_in"]:
    # Unauthenticated flow: Login or Register
    if st.session_state["current_page"] == "Register":
        show_register_screen()
    else:
        show_login_screen()
else:
    # Authenticated flow: Sidebar Navigation
    user = st.session_state.get("user", {})
    user_name = user.get("full_name", "Investigator")
    user_role = user.get("role", "Student")

    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 10px 0 20px 0; border-bottom: 1px solid #1e293b; margin-bottom: 20px;">
            <div style="font-size: 20px; font-weight: 800; color: #60a5fa;">🔍 CaseMind AI</div>
            <div style="font-size: 11px; color: #94a3b8; font-weight: 500;">Analyze • Investigate • Find the Truth</div>
            <div style="margin-top: 10px; font-size: 12px; color: #cbd5e1;">
                👤 <strong>{user_name}</strong> ({user_role})
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 700;'>Navigation</p>", unsafe_allow_html=True)

        pages = [
            ("📊 Dashboard", "Dashboard"),
            ("🔎 New Case Analysis", "New Case Analysis"),
            ("🗄️ Case Database", "Case Database"),
            ("📰 News Search", "News Search"),
            ("⚙️ Settings", "Settings")
        ]

        # Add AI Analysis Results if an active case exists
        if "pending_case_data" in st.session_state:
            pages.insert(2, ("⚡ AI Analysis Results", "AI Analysis Results"))

        for label, page_key in pages:
            if st.button(label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state["current_page"] = page_key
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", key="sidebar_logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["user"] = None
            st.session_state["current_page"] = "Login"
            st.rerun()

    # Route to the selected page
    current = st.session_state.get("current_page", "Dashboard")
    if current == "Dashboard":
        show_dashboard()
    elif current == "New Case Analysis":
        show_case_analysis()
    elif current == "AI Analysis Results":
        show_results_screen()
    elif current == "Case Database":
        show_case_database()
    elif current == "News Search":
        show_news_search()
    elif current == "Settings":
        show_settings()
    else:
        show_dashboard()
