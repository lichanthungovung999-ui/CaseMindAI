"""
register.py
===========
User Registration Screen for CaseMind AI.
Fields:
- Full Name
- Email
- Password & Confirm Password
- Role: Student, Researcher, Investigator, Other
"""

import streamlit as st
from auth import register_user

def show_register_screen():
    """Render the Registration screen matching Google Stitch UI."""
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
            <div style="font-size: 18px; font-weight: 700; color: #f8fafc; margin-bottom: 8px;">
                Create CaseMind Account
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-bottom: 16px;">
                Register to investigate cases, track forensic evidence, and query legal news.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            full_name = st.text_input("Full Name", placeholder="e.g. John Doe")
            email = st.text_input("Email Address", placeholder="name@example.com")
            role = st.selectbox("Role", ["Student", "Researcher", "Investigator", "Other"])
            password = st.text_input("Password", type="password", placeholder="At least 6 characters")
            confirm_pwd = st.text_input("Confirm Password", type="password", placeholder="Repeat your password")

            submit_btn = st.form_submit_button("Register Account")

            if submit_btn:
                if password != confirm_pwd:
                    st.error("Passwords do not match. Please verify and retype.")
                else:
                    success, message = register_user(full_name, email, password, role)
                    if success:
                        st.success(message)
                        st.info("You can now log in with your credentials.")
                    else:
                        st.error(message)

        st.markdown("<div style='text-align: center; margin-top: 14px; font-size: 13px; color: #94a3b8;'>Already registered?</div>", unsafe_allow_html=True)
        if st.button("Return to Login"):
            st.session_state["current_page"] = "Login"
            st.rerun()
