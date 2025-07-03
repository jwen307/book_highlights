# Kindle Highlights Toolkit

A Python application to extract, summarize, and study your Kindle highlights using Amazon's notebook, OpenAI LLMs, and Anki flashcards through a GUI interface.

This code was inspired by the [Obsidian Kindle Highlights plugin](https://github.com/hadynz/obsidian-kindle-plugin/tree/master).

---

## Overview
This application was designed to turn your Kindle highlights into useful Anki flashcards automatically. The flow of operations for highlight extraction and summarization are:

1. Opens a browser to have you sign into your Amazon account
2. Has you select which books you would like to extract the highlights from and summarize
3. Generates a Markdown file with the summary and highlights

Then, you can select which files you would like turned into an Anki flashcard, and these will be automatically created.


## Features

- **GUI Application**: Easy-to-use Tkinter interface for all workflows
- **Amazon Login**: Secure, manual login to your Kindle notebook (no password storage)
- **Book Discovery**: Automatic listing of all your Kindle books
- **Highlight Extraction**: Extracts all highlights, notes, and metadata for any book
- **LLM Summarization**: Summarizes highlights and generates key points and flashcards using an LLM
- **Comprehensive Markdown Export**: Saves summary, key points, flashcards, and highlights in a single markdown file
- **Anki Flashcard Creation**: Converts markdown summaries into Anki flashcards via AnkiConnect
- **Settings Management**: GUI for configuring save location, OpenAI API key, and model

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- [Anki](https://apps.ankiweb.net/) with [AnkiConnect](https://foosoft.net/projects/anki-connect/) (for flashcard export)
- An [OpenAI API key](https://platform.openai.com/account/api-keys) (for LLM features)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jwen307/book_highlights.git
   cd book_highlights
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Launch the GUI

```bash
python book_highlights_gui.py
```

### Set your settings
- Press the settings button and add you desired save location and OpenAI API key

### Main Workflows

- **Summarize Book**:  
  1. Log in to Amazon when prompted  
  2. Select one or more books  
  3. Extracts highlights, summarizes with LLM, and saves a comprehensive markdown file

- **Create Flashcard**:  
  1. Select one or more markdown summary files  
  2. Creates Anki flashcards for each, using the summary, key points, and flashcards

- **Settings**:  
  - Set your save location, OpenAI API key, and model

---

## Project Structure

```
book_highlights/
│
├── book_highlights_gui.py         # Main GUI application
│
├── helpers/                       # All business logic modules
│   ├── amazon_helper.py           # Amazon login & highlight extraction
│   ├── llm_helper.py              # LLM summarization (OpenAI GPT)
│   ├── anki_helper.py             # Anki flashcard creation & markdown parsing
│   ├── markdown_helper.py         # Markdown export utilities
│   ├── config_helper.py           # Config file management
│   ├── models.py                  # Data models (Book, Highlight, etc.)
│   └── __init__.py
│
├── tests/                         # All test files
│   ├── test_flashcards.py
│   ├── test_llm_summarizer.py
│   ├── test_anki_creation.py
│   ├── test_config.py
│   ├── test_kindle_login.py
│   ├── test_combined_functionality.py
│   ├── test_openai_simple.py
│   └── test_url_comparison.py
│
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Configuration

- User settings (save location, OpenAI API key, model) are stored in a JSON file in your home directory (e.g., `~/.book_highlights/user_config.json`).
- You can edit these via the GUI Settings page.

---

## Running Tests

From the project root, run:

```bash
pytest tests/
```

---

## Advanced: Packaging as a Standalone App

You can use [PyInstaller](https://pyinstaller.org/) or [py2app](https://py2app.readthedocs.io/en/latest/) to bundle the GUI as a standalone application for your OS.


---

## Contributing

Pull requests and issues are welcome! Please open an issue for bugs or feature requests.

---

## Note

This project was created as a fun first test of new "vibe coding" tools and was created almost exclusively  using agents in Cursor AI

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Enjoy your smarter Kindle highlights workflow!** 