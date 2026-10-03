"""
case_analysis.py
================
New Case Analysis Input Screen.
Collects:
- Case Title, Location, Date, Description
- Known Clues, Suspect Information, Witness Information, Alibis, Additional Information
- Evidence Image Upload (JPG, JPEG, PNG)
- Modular Analysis Options (Evidence Summary, Timeline Analysis, Clue Connections,
  Missing Information, Alternative Explanations)
- Triggers AI Analysis with Gemini
"""

import streamlit as st
import os
from datetime import date
from utils import is_allowed_file, UPLOAD_FOLDER

def show_case_analysis():
    """Render New Case Analysis screen matching Stitch UI."""
    st.markdown("""
    <div class="brand-header">
        <div>
            <div style="font-size: 20px; font-weight: 700; color: #f8fafc;">
                🔍 New Case Investigation & Evidence Log
            </div>
            <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">
                Input case facts and evidence for impartial Gemini AI synthesis.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="cm-notice">
        <strong>Strict Forensic Rule:</strong> The AI will analyze ONLY facts you provide. It will never assume guilt or fabricate evidence.
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_case_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            title = st.text_input("Case Title *", placeholder="e.g. The Downtown Vault Disappearance")
            location = st.text_input("Location / City", placeholder="e.g. Mumbai, Maharashtra")
        with c2:
            case_date = st.date_input("Case Date", value=date.today())
            uploaded_file = st.file_uploader("Upload Evidence Photo (JPG, PNG)", type=["jpg", "jpeg", "png"])

        description = st.text_area("Case Description *", placeholder="Detailed summary of the incident, background, and initial findings...", height=120)

        c3, c4 = st.columns(2)
        with c3:
            clues = st.text_area("Known Clues & Physical Evidence", placeholder="List recovered items, footprints, digital logs, timestamps...", height=90)
            suspects = st.text_area("Suspect Information", placeholder="Persons of interest, motives, known whereabouts...", height=90)
        with c4:
            witnesses = st.text_area("Witness Testimonies", placeholder="Statements given by witnesses, observed timings...", height=90)
            alibis = st.text_area("Reported Alibis", placeholder="Claimed locations, verified vs unverified alibis...", height=90)

        additional_info = st.text_area("Additional Information / Notes", placeholder="Weather conditions, surveillance gaps, forensics lab remarks...", height=70)

        st.markdown("<div style='font-size: 15px; font-weight: 600; color: #93c5fd; margin-top: 10px; margin-bottom: 6px;'>Select AI Analysis Modules</div>", unsafe_allow_html=True)
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        with col_opt1:
            opt_evidence = st.checkbox("Evidence Summary", value=True)
            opt_timeline = st.checkbox("Timeline Analysis", value=True)
        with col_opt2:
            opt_connections = st.checkbox("Clue Connections", value=True)
            opt_missing = st.checkbox("Missing Information Gaps", value=True)
        with col_opt3:
            opt_alternatives = st.checkbox("Alternative Explanations", value=True)

        analyze_btn = st.form_submit_button("⚡ Analyze Case with AI")

        if analyze_btn:
            if not title.strip() or not description.strip():
                st.error("Please provide both a Case Title and a Case Description before running analysis.")
            else:
                saved_image_path = None
                if uploaded_file is not None:
                    if is_allowed_file(uploaded_file.name):
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        saved_image_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                        with open(saved_image_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    else:
                        st.error("Invalid image format. Only JPG, JPEG, and PNG evidence files are allowed.")
                        return

                case_input_data = {
                    "title": title.strip(),
                    "location": location.strip(),
                    "case_date": str(case_date),
                    "description": description.strip(),
                    "clues": clues.strip(),
                    "suspects": suspects.strip(),
                    "witnesses": witnesses.strip(),
                    "alibis": alibis.strip(),
                    "additional_info": additional_info.strip(),
                    "image_path": saved_image_path,
                    "options": {
                        "evidence_summary": opt_evidence,
                        "timeline": opt_timeline,
                        "clue_connections": opt_connections,
                        "missing_info": opt_missing,
                        "alternative_explanations": opt_alternatives
                    }
                }
                st.session_state["pending_case_data"] = case_input_data
                st.session_state["current_page"] = "AI Analysis Results"
                st.rerun()
