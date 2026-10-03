"""
styles.py
=========
Contains custom CSS styling for CaseMind AI to reproduce the Google Stitch UI design.
"""

import streamlit as st

def apply_custom_styles():
    """Injects custom CSS to style the Streamlit interface matching Google Stitch UI."""
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {
        background: linear-gradient(180deg, #090e17 0%, #0d1527 100%);
        color: #f1f5f9;
        font-family: 'Inter', sans-serif;
    }

    .brand-header {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.2);
        padding: 16px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .cm-card {
        background: #111a2e;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .cm-notice {
        background: rgba(30, 41, 59, 0.6);
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        font-size: 13px;
        color: #cbd5e1;
        margin: 14px 0;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
    }

    section[data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #1e293b;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
