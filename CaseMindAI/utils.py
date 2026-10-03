"""
utils.py
========
Helper and utility functions for CaseMind AI:
- Date formatting and validation
- File extension checks for uploaded evidence (JPG, JPEG, PNG)
- Image saving to uploads directory
"""

import os
from datetime import datetime
from PIL import Image

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")

def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded evidence has an allowed image extension."""
    if "." in filename:
        ext = filename.rsplit(".", 1)[1].lower()
        return ext in ALLOWED_EXTENSIONS
    return False

def validate_and_open_image(image_path: str):
    """Validate and open an evidence image using PIL. Returns Image object or None."""
    if not image_path or not os.path.exists(image_path):
        return None
    if not is_allowed_file(image_path):
        return None
    try:
        img = Image.open(image_path)
        img.verify()  # Verify that it is, in fact, an image
        # Re-open after verify() because verify() can leave the file descriptor in an unusable state
        img = Image.open(image_path)
        return img.convert("RGB")
    except Exception:
        return None

def get_current_date() -> str:
    """Return the current date formatted as YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")

def format_timestamp(ts_str: str) -> str:
    """Format an ISO timestamp to human-readable date and time."""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return ts_str or "N/A"
