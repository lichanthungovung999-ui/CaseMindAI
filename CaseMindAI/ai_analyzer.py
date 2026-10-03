"""
ai_analyzer.py
==============
Gemini AI Analysis Engine for CaseMind AI:
- Uses the official Google Gemini Python SDK (`google-genai`)
- Reads GEMINI_API_KEY from `.streamlit/secrets.toml` or environment
- Supports both Text-Only Case Analysis and Multimodal Evidence Image Analysis
- Adheres strictly to forensic principles:
  1. Distinguishes User-Provided Facts, Direct Observations (including Image Observations),
     Possible Connections, Alternative Hypotheses, and Missing Information
  2. NEVER declares a person definitely guilty or innocent
  3. Never fabricates evidence, witnesses, or claims not grounded in provided data
  4. Never makes legal verdicts
- Returns structured JSON guaranteed to save cleanly into SQLite
"""

import json
import os
from typing import Dict, Any, Optional
import streamlit as st
from utils import validate_and_open_image

def get_gemini_api_key() -> str:
    """
    Retrieve Gemini API key from:
    1. Streamlit secrets (`st.secrets["GEMINI_API_KEY"]`)
    2. Direct read from `.streamlit/secrets.toml` (for offline/CLI usage)
    3. Streamlit session state (`st.session_state["gemini_api_key"]`)
    4. Environment variable (`GEMINI_API_KEY`)
    """
    # 1. Try Streamlit secrets
    try:
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            key = st.secrets["GEMINI_API_KEY"]
            if key and key != "your_gemini_api_key_here":
                return key.strip()
    except Exception:
        pass

    # 2. Try session state
    try:
        if hasattr(st, "session_state") and "gemini_api_key" in st.session_state:
            key = st.session_state["gemini_api_key"]
            if key and key != "your_gemini_api_key_here":
                return key.strip()
    except Exception:
        pass

    # 3. Direct read of .streamlit/secrets.toml
    try:
        base_dir = os.path.dirname(__file__)
        secrets_file = os.path.join(base_dir, ".streamlit", "secrets.toml")
        if os.path.exists(secrets_file):
            with open(secrets_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("GEMINI_API_KEY"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            val = parts[1].strip().strip('"').strip("'")
                            if val and val != "your_gemini_api_key_here":
                                return val
    except Exception:
        pass

    # 4. Environment variable fallback
    env_key = os.environ.get("GEMINI_API_KEY", "")
    if env_key and env_key != "your_gemini_api_key_here":
        return env_key.strip()

    return ""


def build_analysis_prompt(case_data: Dict[str, Any], has_image: bool = False) -> str:
    """Build the strict forensic system prompt for Gemini."""
    image_instruction = ""
    if has_image:
        image_instruction = """
IMAGE FORENSIC GUIDELINE:
An evidence image is attached to this request.
- Examine the visual details carefully (markings, visible objects, lighting, environment, text, damage, timestamps).
- Populate the "image_observations" field with purely factual, objective visual observations.
- DO NOT make unsupported claims about identity, guilt, or facts that cannot be directly proven from the visual pixels.
"""

    prompt = f"""
You are CaseMind AI, an objective, impartial forensic and investigative analysis engine designed for an educational Class 12 Computer Science project.

CRITICAL FORENSIC RULES:
1. Base your analysis STRICTLY on the user-provided facts and attached evidence image.
2. NEVER state or declare that any person is definitely guilty or innocent.
3. NEVER make legal conclusions, verdicts, or accusations.
4. Clearly distinguish between:
   - Facts provided by the user
   - Direct observations (including physical/digital evidence and visual image observations)
   - Possible connections and logical links
   - Hypotheses and alternative explanations
   - Missing information and critical investigative gaps
5. Do NOT invent evidence, suspects, witnesses, or unprovided events.
{image_instruction}

CASE INFORMATION PROVIDED BY USER:
- Title: {case_data.get('title', 'Untitled')}
- Location: {case_data.get('location', 'Unspecified')}
- Date: {case_data.get('case_date', 'Unspecified')}
- Description: {case_data.get('description', '')}
- Known Clues: {case_data.get('clues', 'None reported')}
- Suspect Information: {case_data.get('suspects', 'None reported')}
- Witness Statements: {case_data.get('witnesses', 'None reported')}
- Reported Alibis: {case_data.get('alibis', 'None reported')}
- Additional Notes: {case_data.get('additional_info', 'None reported')}

JSON OUTPUT FORMAT REQUIREMENT:
Respond STRICTLY with a valid JSON object matching this schema exactly:
{{
  "case_summary": "Concise 2-3 paragraph objective summary of known circumstances.",
  "user_facts": ["List of distinct, verified facts explicitly stated by the user."],
  "image_observations": ["Objective visual details observed directly in the evidence photo (or state 'No image attached')."],
  "key_evidence": ["Identified physical or digital evidence items."],
  "important_clues": ["Noteworthy clues and their potential investigative significance."],
  "possible_timeline": [
    {{"time": "Approximate or stated time", "event": "Specific occurrence", "source": "User statement / clue / witness"}}
  ],
  "entities_mentioned": [
    {{"name": "Entity or person name", "type": "Suspect / Witness / Institution / Victim", "detail": "Neutral description"}}
  ],
  "possible_connections": ["Logical correlations between clues, locations, and entities."],
  "missing_information": ["Key investigative gaps, unverified claims, or missing documentation."],
  "alternative_explanations": ["Alternative non-criminal, accidental, or third-party hypotheses."],
  "investigation_questions": ["Key prioritized questions investigators should pursue next."],
  "limitations": "Explicit note that this analysis is an investigative aid bounded strictly by the provided inputs.",
  "legal_notice": "LEGAL NOTICE: CaseMind AI analysis is an investigative aid and does NOT constitute proof of guilt, identity, or any legal determination."
}}
"""
    return prompt.strip()


def analyze_case_with_gemini(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform case analysis using Google Gemini Python SDK (`google-genai`).
    Supports:
    - Text-only case analysis
    - Multimodal evidence image analysis (JPG, JPEG, PNG)
    - Fallback handling for missing API keys or network errors
    """
    api_key = get_gemini_api_key()

    # 1. Check for attached evidence image and validate
    image_path = case_data.get("image_path")
    pil_image = None
    has_image = False
    if image_path:
        pil_image = validate_and_open_image(image_path)
        if pil_image is not None:
            has_image = True

    # 2. Build the strict forensic prompt
    prompt_text = build_analysis_prompt(case_data, has_image=has_image)

    # 3. If API Key is missing, provide structured guidance
    if not api_key:
        return {
            "case_summary": f"Case record for '{case_data.get('title')}'. Location: {case_data.get('location', 'N/A')}. Incident details: {case_data.get('description', '')[:200]}...",
            "user_facts": [
                f"Location recorded: {case_data.get('location', 'Unspecified')}.",
                f"Incident date: {case_data.get('case_date', 'Unspecified')}.",
                f"Description provided: {case_data.get('description', 'N/A')[:150]}"
            ],
            "image_observations": [
                f"Evidence image '{os.path.basename(image_path)}' logged in evidence registry."
            ] if has_image else ["No evidence image attached to this case file."],
            "key_evidence": [
                case_data.get("clues", "Physical evidence logged in case file.")
            ],
            "important_clues": [
                "Reconcile timeline discrepancies between witness reports and reported alibis.",
                "Verify digital logs or physical records corresponding to the reported scene."
            ],
            "possible_timeline": [
                {"time": "Incident Window", "event": "Reported incident occurrence", "source": "User Description"},
                {"time": "Subsequent", "event": "Evidence logged & witness statements collected", "source": "Case Log"}
            ],
            "entities_mentioned": [
                {"name": "Suspects listed", "type": "Person of Interest", "detail": case_data.get("suspects", "None")},
                {"name": "Witnesses listed", "type": "Witness", "detail": case_data.get("witnesses", "None")}
            ],
            "possible_connections": [
                "Correlation between known suspects' proximity and time of incident.",
                "Review of stated alibis against physical or digital timestamps."
            ],
            "missing_information": [
                "Digital forensics or CCTV footage verification.",
                "Independent witness corroboration for the reported alibi window."
            ],
            "alternative_explanations": [
                "Incident may have involved unobserved third-party interference.",
                "Misinterpretation of initial witness sequence or timing."
            ],
            "investigation_questions": [
                "Can the suspect's whereabouts during the incident window be independently corroborated?",
                "Are there additional physical clues at the scene that require forensic lab processing?"
            ],
            "limitations": "Analysis is strictly bounded by the details input by the user. No independent verification was performed.",
            "legal_notice": "LEGAL NOTICE: CaseMind AI analysis is an investigative aid and does not constitute proof of guilt, identity, or any legal determination.",
            "api_notice": "Note: To activate real-time Gemini AI analysis, configure GEMINI_API_KEY in .streamlit/secrets.toml."
        }

    # 4. Live Gemini API Call using official google-genai SDK
    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        # Prepare multimodal contents array
        if has_image and pil_image is not None:
            contents = [prompt_text, pil_image]
        else:
            contents = [prompt_text]

        # Try modern high-speed models in order of resilience
        models_to_try = ["gemini-3.1-flash-lite", "gemini-flash-latest", "gemini-3.8-flash"]
        last_error = None
        response = None

        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config={"response_mime_type": "application/json"}
                )
                if response and response.text:
                    break
            except Exception as model_err:
                last_error = model_err
                continue

        if not response or not response.text:
            raise last_error or RuntimeError("Gemini models failed to return content.")

        response_text = response.text.strip()
        parsed = json.loads(response_text)

        # Ensure all required keys exist in the parsed output
        required_keys = [
            "case_summary", "user_facts", "key_evidence", "important_clues",
            "possible_timeline", "entities_mentioned", "possible_connections",
            "missing_information", "alternative_explanations",
            "investigation_questions", "limitations", "legal_notice"
        ]
        for k in required_keys:
            if k not in parsed:
                parsed[k] = [] if "s" in k or k.endswith("evidence") or k.endswith("information") else "Not provided"

        if "image_observations" not in parsed:
            parsed["image_observations"] = [
                "Image processed by Gemini Vision."
            ] if has_image else ["No evidence image attached."]

        return parsed

    except Exception as e:
        # Graceful error handling: return structured object with error logged
        return {
            "case_summary": f"Investigation summary for '{case_data.get('title')}'. Processing encountered an API error: {str(e)}",
            "user_facts": [
                f"Incident location: {case_data.get('location', 'Unspecified')}.",
                f"Reported occurrence: {case_data.get('case_date', 'Unspecified')}."
            ],
            "image_observations": [
                f"Evidence image attached ({os.path.basename(image_path) if image_path else 'None'})."
            ] if has_image else ["No evidence image attached."],
            "key_evidence": [case_data.get("clues", "Evidence noted in case details.")],
            "important_clues": ["Review physical evidence and timeline consistency."],
            "possible_timeline": [
                {"time": "Incident Date", "event": "Occurrence logged", "source": "User Description"}
            ],
            "entities_mentioned": [
                {"name": "Persons of Interest", "type": "Entities", "detail": case_data.get("suspects", "None")}
            ],
            "possible_connections": ["Analyze correlations between clues and witness accounts."],
            "missing_information": ["Detailed forensic reports and corroborating witnesses."],
            "alternative_explanations": ["Examine all reasonable alternative scenarios."],
            "investigation_questions": ["What additional physical evidence can be gathered?"],
            "limitations": f"Automated analysis paused due to API exception: {str(e)}.",
            "legal_notice": "LEGAL NOTICE: CaseMind AI analysis is an investigative aid and does not constitute proof of guilt, identity, or any legal determination.",
            "api_error": str(e)
        }
