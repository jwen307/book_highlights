#!/usr/bin/env python3
"""
Configuration file for Kindle Highlights Extractor
"""

import os
from pathlib import Path

# Default save location for highlights
# You can modify this to your preferred directory
DEFAULT_SAVE_LOCATION = os.path.expanduser("~/Documents/KindleHighlights")

# Create the directory if it doesn't exist
def ensure_save_directory():
    """Ensure the save directory exists, create it if it doesn't."""
    Path(DEFAULT_SAVE_LOCATION).mkdir(parents=True, exist_ok=True)
    return DEFAULT_SAVE_LOCATION

# Alternative save locations (uncomment and modify as needed)
# DEFAULT_SAVE_LOCATION = "/Users/username/Documents/Books/Highlights"
# DEFAULT_SAVE_LOCATION = "./highlights"
# DEFAULT_SAVE_LOCATION = os.path.expanduser("~/Desktop/KindleNotes") 