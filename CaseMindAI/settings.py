"""
settings.py
===========
Settings and User Profile Screen for CaseMind AI:
- View Profile (Name, Email, Role, Joined Date)
- Change Password
- Preferences & Data Management
- Logout functionality
"""

import streamlit as st
from auth import hash_password, verify_password
from database import get_connection

def show_settings():
    """Render Settings & Profile Management screen."""
    st.markdown("""
    <div class="brand-header">
        <div>
            <div style="font-size: 20px; font-weight: 700; color: #f8fafc;">
                ⚙️ User Profile & System Preferences
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
                Manage your credentials, database storage, and session settings.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.get("user", {})
    user_id = user.get("id", 1)

    t1, t2, t3 = st.tabs(["👤 Profile Information", "🔒 Security & Password", "💾 Data Management"])

    with t1:
        st.markdown(f"""
        <div class="cm-card">
            <div style="font-size: 16px; font-weight: 700; color: #60a5fa; margin-bottom: 12px;">
                Account Details
            </div>
            <p><strong>Full Name:</strong> {user.get('full_name', 'Investigator')}</p>
            <p><strong>Email Address:</strong> {user.get('email', 'N/A')}</p>
            <p><strong>System Role:</strong> <span class="cm-badge cm-badge-blue">{user.get('role', 'Student')}</span></p>
            <p><strong>Member Since:</strong> {user.get('created_at', '2026')}</p>
        </div>
        """, unsafe_allow_html=True)

    with t2:
        st.markdown("### Update Account Password")
        with st.form("pwd_form"):
            old_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_new = st.text_input("Confirm New Password", type="password")
            change_btn = st.form_submit_button("Update Password")

            if change_btn:
                if new_pwd != confirm_new:
                    st.error("New passwords do not match.")
                elif len(new_pwd) < 6:
                    st.error("New password must be at least 6 characters.")
                else:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
                    row = cursor.fetchone()
                    if row and verify_password(old_pwd, row["password_hash"]):
                        new_hash = hash_password(new_pwd)
                        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
                        conn.commit()
                        st.success("Password changed successfully!")
                    else:
                        st.error("Current password is incorrect.")
                    conn.close()

    with t3:
        st.markdown("### Database & Cache Management")
        st.write("Manage locally stored case records and evidence attachments.")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Purge My Saved Cases (SQLite)", type="primary"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cases WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
                st.warning("All case records for this account have been deleted.")

        with c2:
            st.markdown("""
            <div style="font-size: 13px; color: #94a3b8;">
                Cases are stored locally in <code>database/casemind.db</code>.
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    st.markdown("---")
    if st.button("🚪 Logout of CaseMind AI"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["current_page"] = "Login"
        st.rerun()
