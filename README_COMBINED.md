# Kindle Highlights with LLM Summary

A comprehensive Python tool that extracts Kindle highlights from Amazon's notebook, generates AI-powered summaries and key points, and saves everything to beautifully formatted markdown files.

## Features

- 🔍 **Automatic Kindle Highlights Extraction**: Pulls highlights directly from Amazon's notebook
- 🤖 **AI-Powered Summaries**: Uses OpenAI's GPT to generate intelligent summaries and key points
- 🎯 **Flashcard Generation**: Creates study flashcards to test understanding of key concepts
- 📝 **Comprehensive Markdown Output**: Saves everything in a well-organized markdown format
- 🎯 **Interactive Book Selection**: Choose which book to process from your library
- 📊 **Rich Metadata**: Includes location, page numbers, colors, and notes
- 🚀 **Progress Tracking**: Real-time progress indicators during extraction and processing

## Quick Start

### 1. Setup

```bash
# Clone the repository
git clone <repository-url>
cd book_highlights

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key in config.py
# Edit config.py and add your API key:
# OPENAI_API_KEY = "your-openai-api-key-here"
```

### 2. Run the Combined Tool

```bash
python kindle_highlights_with_summary.py
```

### 3. Follow the Interactive Process

1. **Setup**: The tool will launch Chrome and navigate to Amazon's notebook
2. **Login**: Complete the login process in the browser window
3. **Book Selection**: Choose from your available books
4. **Extraction**: Watch as highlights are automatically extracted
5. **AI Summary**: The tool generates a summary and key points using GPT
6. **Save**: Everything is saved to a comprehensive markdown file

## Output Files

The tool creates a single comprehensive file in your configured save directory:

- `{Book-Title}-complete.md` - **Complete file** with everything (summary + flashcards + highlights)

### Example Output Structure

```markdown
# The Psychology of Money

**Author:** Morgan Housel
**ASIN:** B08D9WJ9G7

---

## 📝 AI-Generated Summary

**One-Sentence Summary:** The book explores how personal psychology and behavior patterns shape financial decisions more than mathematical calculations.

**Key Points:**
1. Wealth is often invisible - it's the money not spent
2. Financial freedom is about control over your time
3. Personal history and experiences heavily influence financial behavior
4. Getting money and keeping money require different skills
5. Appearances can be deceiving in wealth assessment

## 🎯 Flashcards

*Test your understanding of the key concepts*

**Q1:** What is the highest form of wealth according to the book?

**A1:** The ability to wake up every morning and say, 'I can do whatever I want today.'

---

**Q2:** What is money's greatest intrinsic value?

**A2:** Its ability to give you control over your time.

---

**Q3:** What does the book say about wealth and appearances?

**A3:** Wealth is what you don't see - the cars not purchased, diamonds not bought, watches not worn.

---

## 📖 Highlights (7 total)

### Highlight 1

The highest form of wealth is the ability to wake up every morning and say, 'I can do whatever I want today.'

*Location: Location 123, Page: 15, Color: yellow*

**Note:** This defines true financial freedom.

---
```

## Configuration

### Save Location

Edit `config.py` to change where files are saved:

```python
# Default save location
DEFAULT_SAVE_LOCATION = os.path.expanduser("~/Documents/KindleHighlights")
```

### OpenAI API Key

Set your OpenAI API key in `config.py`:

```python
# Option 1: Direct assignment
OPENAI_API_KEY = "your-api-key-here"

# Option 2: Environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
```

## Testing

### Test the LLM Component

```bash
python test_llm_summarizer.py
```

### Test the Combined Functionality

```bash
python test_combined_functionality.py
```

### Test Kindle Login

```bash
python test_kindle_login.py
```

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Set your API key in `config.py`
   - Or set the `OPENAI_API_KEY` environment variable

2. **"No books found"**
   - Make sure you're logged into the correct Amazon account
   - Try refreshing the page in the browser
   - Check that you have highlights in your Kindle library

3. **"Failed to initialize OpenAI client"**
   - Check your internet connection
   - Verify your API key is correct
   - Ensure you have sufficient OpenAI credits

4. **Browser issues**
   - Make sure Chrome is installed
   - Try updating Chrome to the latest version
   - Check that ChromeDriver is compatible

### Debug Mode

If you encounter issues, the tool creates debug files:
- `debug_{ASIN}.html` - Page structure for analysis
- `page_debug.html` - General page debugging

## File Structure

```
book_highlights/
├── kindle_highlights_with_summary.py  # Main combined script (generates single output file)
├── kindle_highlights.py               # Kindle extraction component
├── llm_summarizer.py                  # LLM summarization component
├── models.py                          # Data models
├── config.py                          # Configuration
├── test_combined_functionality.py     # Combined functionality test
├── test_llm_summarizer.py            # LLM component test
├── test_flashcards.py                # Flashcard generation test
├── test_kindle_login.py              # Login test
└── requirements.txt                   # Dependencies
```

## Dependencies

- `selenium` - Web automation
- `openai` - OpenAI API integration
- `rich` - Beautiful terminal output
- `webdriver-manager` - Chrome driver management
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the debug files created by the tool
3. Open an issue on GitHub with details about your problem

## Roadmap

- [ ] Support for multiple books in batch
- [ ] Export to different formats (PDF, EPUB)
- [ ] Integration with note-taking apps (Obsidian, Notion)
- [ ] Custom LLM prompts for different book types
- [ ] Highlight clustering and theme analysis
- [ ] Reading progress tracking 