"""
results.py
==========
AI Analysis Results Display Screen.
Displays structured forensic outputs:
- Clearly separates:
  1. User-provided facts
  2. AI interpretation
  3. Uncertain information
- Timeline, clue connections, missing data gaps, alternative explanations
- Option to "Save Case to SQLite Database"
"""

import json
import os
import streamlit as st
from ai_analyzer import analyze_case_with_gemini
from database import get_connection

def show_results_screen():
    """Render the AI Analysis Results screen."""
    case_data = st.session_state.get("pending_case_data")
    if not case_data:
        st.warning("No active case analysis data found. Please start a new case.")
        if st.button("Go to New Case Form"):
            st.session_state["current_page"] = "New Case Analysis"
            st.rerun()
        return

    # Check if analysis is already computed or needs computation
    if "analysis_result" not in st.session_state:
        with st.spinner("CaseMind AI is structuring clues, timeline, and forensic connections..."):
            st.session_state["analysis_result"] = analyze_case_with_gemini(case_data)

    res = st.session_state["analysis_result"]

    # Header
    st.markdown(f"""
    <div class="brand-header">
        <div>
            <div style="font-size: 20px; font-weight: 700; color: #f8fafc;">
                ⚖️ AI Analysis Report: <span style="color: #60a5fa;">{case_data.get('title')}</span>
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
                Location: {case_data.get('location', 'N/A')} • Date: {case_data.get('case_date', 'N/A')}
            </div>
        </div>
        <div>
            <span class="cm-badge cm-badge-blue">Synthesis Complete</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mandatory Legal Disclaimer Notice
    st.markdown(f"""
    <div class="cm-notice">
        <strong>⚖️ Forensic Notice:</strong> {res.get('legal_notice', 'This AI analysis is an investigative aid and does not constitute proof of guilt, identity, or legal conclusion.')}
    </div>
    """, unsafe_allow_html=True)

    # Tabs for organized investigation breakdown
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📄 Case Summary",
        "🕒 Timeline & Evidence",
        "👥 Entities & Connections",
        "❓ Gaps & Questions",
        "🔀 Alternative Explanations",
        "💾 Save Case"
    ])

    with tab1:
        st.markdown("<div class='cm-card'>", unsafe_allow_html=True)
        st.markdown("### Executive Summary")
        st.write(res.get("case_summary", "No summary available."))
        st.markdown("#### User-Provided Facts (Unmodified)")
        for fact in res.get("user_facts", []):
            st.markdown(f"- 📌 {fact}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        if case_data.get("image_path") and os.path.exists(case_data.get("image_path")):
            st.markdown("### 📸 Uploaded Evidence Image")
            st.image(case_data.get("image_path"), caption="Evidence Photo Analyzed by Gemini Vision", use_container_width=True)

        img_obs = res.get("image_observations", [])
        if img_obs and img_obs != ["No evidence image attached."]:
            st.markdown("### 🔬 Gemini Vision Forensic Observations")
            for obs in img_obs:
                st.markdown(f"- 👁️ {obs}")

        st.markdown("### Reconstruction Timeline")
        timeline = res.get("possible_timeline", [])
        if timeline:
            for item in timeline:
                st.markdown(f"**{item.get('time')}**: {item.get('event')} *(Source: {item.get('source')})*")
        else:
            st.info("No timeline items identified.")

        st.markdown("### Key Physical & Digital Evidence")
        for ev in res.get("key_evidence", []):
            st.markdown(f"- 🔎 {ev}")

    with tab3:
        st.markdown("### Entities & Persons Mentioned")
        entities = res.get("entities_mentioned", [])
        for ent in entities:
            st.markdown(f"- **{ent.get('name')}** ({ent.get('type')}): {ent.get('detail')}")

        st.markdown("### Possible Logical Connections")
        for conn in res.get("possible_connections", []):
            st.markdown(f"- 🔗 {conn}")

    with tab4:
        st.markdown("### Missing Information & Critical Gaps")
        for gap in res.get("missing_information", []):
            st.markdown(f"- ⚠️ {gap}")

        st.markdown("### Recommended Investigation Questions")
        for q in res.get("investigation_questions", []):
            st.markdown(f"- ❓ {q}")

    with tab5:
        st.markdown("### Alternative Hypotheses & Explanations")
        for alt in res.get("alternative_explanations", []):
            st.markdown(f"- 💡 {alt}")

        st.markdown(f"**Limitations:** {res.get('limitations', 'Strictly bounded by user data.')}")

    with tab6:
        st.markdown("### Save to Case Database")
        st.write("Save this investigation dossier and its AI analysis report into your local SQLite database for future reference.")

        if st.button("💾 Confirm Save Case to Database"):
            user = st.session_state.get("user", {})
            user_id = user.get("id", 1)

            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cases (
                        user_id, title, location, case_date, description,
                        clues, suspects, witnesses, alibis, additional_info,
                        image_path, analysis_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    user_id,
                    case_data.get("title"),
                    case_data.get("location"),
                    case_data.get("case_date"),
                    case_data.get("description"),
                    case_data.get("clues"),
                    case_data.get("suspects"),
                    case_data.get("witnesses"),
                    case_data.get("alibis"),
                    case_data.get("additional_info"),
                    case_data.get("image_path"),
                    json.dumps(res)
                ))
                conn.commit()
                conn.close()
                st.success("Case successfully saved to SQLite database!")
                if st.button("Go to Case Database"):
                    st.session_state["current_page"] = "Case Database"
                    st.rerun()
            except Exception as e:
                st.error(f"Error saving case: {str(e)}")
