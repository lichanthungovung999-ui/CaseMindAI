"""
case_database.py
================
Case Database Screen for CaseMind AI:
- Query saved cases from SQLite using parameterized queries
- Search cases by title, location, or description
- Expand case details and view stored AI analysis
- Delete cases safely with confirmation
"""

import json
import streamlit as st
from database import get_connection

def show_case_database():
    """Render Case Database viewer with search, detail modal, and delete."""
    st.markdown("""
    <div class="brand-header">
        <div>
            <div style="font-size: 20px; font-weight: 700; color: #f8fafc;">
                🗄️ Case Investigation Database
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
                Secure local SQLite repository of analyzed investigations.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.get("user", {})
    user_id = user.get("id", 1)

    # Search Bar
    search_query = st.text_input("Search Cases by Title, Location, or Keyword", placeholder="Type to filter...")

    conn = get_connection()
    cursor = conn.cursor()

    if search_query.strip():
        term = f"%{search_query.strip()}%"
        cursor.execute("""
            SELECT id, title, location, case_date, description, clues, suspects,
                   witnesses, alibis, additional_info, analysis_json, created_at
            FROM cases
            WHERE user_id = ? AND (title LIKE ? OR location LIKE ? OR description LIKE ?)
            ORDER BY id DESC;
        """, (user_id, term, term, term))
    else:
        cursor.execute("""
            SELECT id, title, location, case_date, description, clues, suspects,
                   witnesses, alibis, additional_info, analysis_json, created_at
            FROM cases
            WHERE user_id = ?
            ORDER BY id DESC;
        """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        st.info("No saved cases found in your database. Start a new investigation via 'New Case Analysis'.")
        return

    st.write(f"Found **{len(rows)}** case record(s):")

    for row in rows:
        with st.expander(f"📁 #{row['id']} - {row['title']} ({row['location'] or 'Unknown Location'})"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Date:** {row['case_date']} | **Logged:** {row['created_at']}")
                st.markdown(f"**Description:** {row['description']}")
                if row['clues']:
                    st.markdown(f"**Clues:** {row['clues']}")
                if row['suspects']:
                    st.markdown(f"**Suspects:** {row['suspects']}")
            with c2:
                # Delete button with safe confirmation
                confirm_key = f"confirm_del_{row['id']}"
                if st.session_state.get(confirm_key):
                    st.warning("⚠️ Confirm delete?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("Yes", key=f"yes_{row['id']}", type="primary"):
                            del_conn = get_connection()
                            del_cur = del_conn.cursor()
                            del_cur.execute("DELETE FROM cases WHERE id = ? AND user_id = ?", (row['id'], user_id))
                            del_conn.commit()
                            del_conn.close()
                            st.session_state[confirm_key] = False
                            st.success(f"Case #{row['id']} deleted.")
                            st.rerun()
                    with col_no:
                        if st.button("Cancel", key=f"no_{row['id']}"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                else:
                    if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                        st.session_state[confirm_key] = True
                        st.rerun()

            # Display AI analysis if stored
            if row['analysis_json']:
                try:
                    analysis = json.loads(row['analysis_json'])
                    st.markdown("---")
                    st.markdown("**AI Executive Summary:**")
                    st.write(analysis.get("case_summary", "N/A"))
                    with st.expander("Show Detailed AI Findings"):
                        st.json(analysis)
                except Exception:
                    st.write("Stored analysis data is unavailable.")
