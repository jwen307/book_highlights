#!/usr/bin/env python3
"""
Config helper for Kindle Highlights Extractor
"""
import os
import sys
import json
from pathlib import Path

CONFIG_DIR_NAME = ".book_highlights"
CONFIG_FILENAME = "user_config.json"

DEFAULTS = {
    "save_location": os.path.expanduser("~/Documents/KindleHighlights"),
    "openai_api_key": "",
    "openai_model": "gpt-3.5-turbo"
}

def get_config_dir():
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        return Path(base) / "book_highlights"
    else:
        return Path(os.path.expanduser(f"~/{CONFIG_DIR_NAME}"))

def get_config_path():
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / CONFIG_FILENAME

def load_config():
    path = get_config_path()
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
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

def ensure_save_directory():
    config = load_config()
    save_dir = Path(config['save_location'])
    save_dir.mkdir(parents=True, exist_ok=True)
    return str(save_dir)

def get_openai_api_key() -> str:
    return load_config().get('openai_api_key', '')

def get_openai_model() -> str:
    return load_config().get('openai_model', 'gpt-3.5-turbo') 