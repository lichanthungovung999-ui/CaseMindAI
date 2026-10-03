"""
dashboard.py
============
Main Dashboard Screen for CaseMind AI.
Reproduces Google Stitch design:
- Top investigation status bar
- Metric overview cards
- Quick navigation shortcuts (New Case Analysis, Case Database, News Search, Settings)
- Recent cases summary
- Strict legal disclaimer banner
"""

import streamlit as st
from database import get_connection

def show_dashboard():
    """Render the Main Dashboard screen."""
    user = st.session_state.get("user", {})
    user_name = user.get("full_name", "Investigator")
    user_role = user.get("role", "Student")
    user_id = user.get("id", 1)

    # 1. Top Welcome & Brand Banner
    st.markdown(f"""
    <div class="brand-header">
        <div>
            <div style="font-size: 22px; font-weight: 800; color: #f8fafc;">
                Welcome back, <span style="color: #60a5fa;">{user_name}</span>
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
                Role: <span style="color: #cbd5e1; font-weight: 600;">{user_role}</span> • CaseMind AI Workspace
            </div>
        </div>
        <div style="text-align: right;">
            <span class="cm-badge cm-badge-green">● System Operational</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Disclaimer Notice
    st.markdown("""
    <div class="cm-notice">
        <strong>⚠️ Advisory Notice:</strong> CaseMind AI is an investigative aid designed for analysis, timeline structuring, and pattern discovery. It does not determine guilt or issue legal conclusions.
    </div>
    """, unsafe_allow_html=True)

    # 3. Quick Metrics from Database
    total_cases = 0
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM cases WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            total_cases = row["count"]
        conn.close()
    except Exception:
        total_cases = 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="cm-metric-box">
            <div class="cm-metric-val">{total_cases}</div>
            <div class="cm-metric-lbl">Total Cases</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="cm-metric-box">
            <div class="cm-metric-val">Gemini Flash</div>
            <div class="cm-metric-lbl">AI Engine</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="cm-metric-box">
            <div class="cm-metric-val">India</div>
            <div class="cm-metric-lbl">News Region</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="cm-metric-box">
            <div class="cm-metric-val">SQLite</div>
            <div class="cm-metric-lbl">Storage Mode</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 4. Navigation Action Cards
    st.markdown("<div style='font-size: 18px; font-weight: 700; color: #f1f5f9; margin-bottom: 12px;'>Investigative Modules</div>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="cm-card">
            <div style="font-size: 16px; font-weight: 700; color: #60a5fa; margin-bottom: 6px;">
                🔎 New Case Analysis
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-bottom: 14px;">
                Input clues, suspect dossiers, alibis, and run AI timeline synthesis.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Case Form", key="btn_dash_new_case"):
            st.session_state["current_page"] = "New Case Analysis"
            st.rerun()

    with col_b:
        st.markdown("""
        <div class="cm-card">
            <div style="font-size: 16px; font-weight: 700; color: #34d399; margin-bottom: 6px;">
                🗄️ Case Database
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-bottom: 14px;">
                Browse saved investigation files, evidence logs, and AI conclusions.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Database", key="btn_dash_db"):
            st.session_state["current_page"] = "Case Database"
            st.rerun()

    with col_c:
        st.markdown("""
        <div class="cm-card">
            <div style="font-size: 16px; font-weight: 700; color: #fbbf24; margin-bottom: 6px;">
                📰 Legal & Crime News
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-bottom: 14px;">
                Search real-time court, crime, cyber forensics, and missing persons feeds.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Search News", key="btn_dash_news"):
            st.session_state["current_page"] = "News Search"
            st.rerun()
