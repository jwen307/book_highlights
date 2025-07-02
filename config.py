#!/usr/bin/env python3
"""
Configuration file for Kindle Highlights Extractor
"""

import os
from pathlib import Path

# Default save location for highlights
# You can modify this to your preferred directory
DEFAULT_SAVE_LOCATION = os.path.expanduser("~/Documents/KindleHighlights")

# OpenAI API Configuration
# Set your OpenAI API key here or use environment variable
#OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # You can set this in your environment
# Or uncomment and set directly:
OPENAI_API_KEY = "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"

# Create the directory if it doesn't exist
def ensure_save_directory():
    """Ensure the save directory exists, create it if it doesn't."""
    Path(DEFAULT_SAVE_LOCATION).mkdir(parents=True, exist_ok=True)
    return DEFAULT_SAVE_LOCATION

def get_openai_api_key() -> str:
    """Get the OpenAI API key from configuration or environment."""
    return OPENAI_API_KEY

# Alternative save locations (uncomment and modify as needed)
# DEFAULT_SAVE_LOCATION = "/Users/username/Documents/Books/Highlights"
# DEFAULT_SAVE_LOCATION = "./highlights"
# DEFAULT_SAVE_LOCATION = os.path.expanduser("~/Desktop/KindleNotes") 