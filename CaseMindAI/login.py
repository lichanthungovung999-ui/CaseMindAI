"""
login.py
========
Login Screen for CaseMind AI.
Reproduces Google Stitch design:
- Header with shield & logo
- Tagline: "Analyze • Investigate • Find the Truth"
- Clean credentials input card
- Action to switch to Register
"""

import streamlit as st
from auth import login_user

def show_login_screen():
    """Render the Login screen matching Google Stitch UI."""
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="brand-header" style="text-align: center;">
            <div style="font-size: 26px; font-weight: 800; color: #60a5fa; margin-bottom: 6px;">
                🔍 CaseMind AI
            </div>
            <div style="font-size: 13px; color: #94a3b8; font-weight: 500; letter-spacing: 0.5px;">
                Analyze • Investigate • Find the Truth
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="cm-card">
            <div style="font-size: 18px; font-weight: 700; color: #f8fafc; margin-bottom: 12px;">
                Sign In to Investigation Portal
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-bottom: 18px;">
                Access confidential case records, AI analysis, and forensic timelines.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email Address", placeholder="investigator@casemind.ai")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit_btn = st.form_submit_button("Sign In")

            if submit_btn:
                success, user, message = login_user(email, password)
                if success and user:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = user
                    st.session_state["current_page"] = "Dashboard"
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("<div style='text-align: center; margin-top: 16px; font-size: 13px; color: #94a3b8;'>Don't have an account yet?</div>", unsafe_allow_html=True)
        if st.button("Create New Account"):
            st.session_state["current_page"] = "Register"
            st.rerun()
