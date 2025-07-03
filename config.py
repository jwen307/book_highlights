#!/usr/bin/env python3
"""
Configuration file for Kindle Highlights Extractor
"""

import os
import json
from pathlib import Path

CONFIG_FILE = "user_config.json"
DEFAULTS = {
    "save_location": os.path.expanduser("~/Documents/KindleHighlights"),
    "openai_api_key": "",
    "openai_model": "gpt-3.5-turbo"
}

def get_config_path():
    return Path(__file__).parent / CONFIG_FILE

def load_config():
    path = get_config_path()
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Fill in any missing defaults
        for k, v in DEFAULTS.items():
            if k not in data:
                data[k] = v
        return data
    else:
        return DEFAULTS.copy()

def save_config(config):
    path = get_config_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

# Accessors for current config values
_config = load_config()
DEFAULT_SAVE_LOCATION = _config['save_location']
OPENAI_API_KEY = _config['openai_api_key']
OPENAI_MODEL = _config.get('openai_model', 'gpt-3.5-turbo')

# Create the directory if it doesn't exist
def ensure_save_directory():
    """Ensure the save directory exists, create it if it doesn't."""
    Path(DEFAULT_SAVE_LOCATION).mkdir(parents=True, exist_ok=True)
    return DEFAULT_SAVE_LOCATION

def get_openai_api_key() -> str:
    """Get the OpenAI API key from user config."""
    return OPENAI_API_KEY

def get_openai_model() -> str:
    """Get the OpenAI model from user config."""
    return OPENAI_MODEL

# Alternative save locations (uncomment and modify as needed)
# DEFAULT_SAVE_LOCATION = "/Users/username/Documents/Books/Highlights"
# DEFAULT_SAVE_LOCATION = "./highlights"
# DEFAULT_SAVE_LOCATION = os.path.expanduser("~/Desktop/KindleNotes") 