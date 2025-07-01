# Kindle Highlights Extractor

A Python tool to extract your Kindle highlights from Amazon's notebook at https://read.amazon.com/notebook.

## Features

- 🔐 Manual login support (avoids automation detection)
- 📚 Automatic book discovery from your Kindle library
- 🎯 Interactive book selection
- 📝 Highlight extraction with full metadata
- 📁 JSON export with structured data
- 🛡️ Anti-detection measures for web scraping
- 🎨 Rich terminal interface with progress indicators

## Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- Amazon account with Kindle books and highlights

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd book_highlights
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
python kindle_highlights.py
```

2. The script will:
   - Launch a Chrome browser window
   - Navigate to Amazon's notebook page
   - Wait for you to manually log in
   - Verify your login status
   - Display available books from your library
   - Allow you to select a book interactively
   - Extract all highlights from the selected book
   - Save highlights to a JSON file

3. Follow the on-screen instructions to complete the login process

## How it Works

### Login Process
- The script opens a Chrome browser window with anti-detection measures
- You manually log in to your Amazon account (this avoids automation detection)
- The script verifies successful login by checking for book content using the same selectors as the Obsidian Kindle plugin
- The browser remains open for further development

### Book Discovery
- After successful login, the script scans the notebook page for your books
- Uses the same CSS selectors as the TypeScript implementation for maximum compatibility
- Extracts book titles, authors, ASINs, and metadata
- Books are displayed in a numbered list for selection

### Highlight Extraction
- Navigates to the book's highlights page using the ASIN
- Extracts highlights using the same selectors as the TypeScript implementation
- Handles pagination automatically to get all highlights
- Extracts text, location, page numbers, notes, and highlight colors
- Saves everything to a structured JSON file

## Output Format

The script generates a JSON file with the following structure:

```json
[
  {
    "text": "The actual highlighted text",
    "location": "Location information",
    "page": "Page number",
    "note": "Any notes you added to the highlight",
    "color": "yellow|blue|pink|orange",
    "book_title": "Book Title",
    "book_author": "Author Name",
    "asin": "Book ASIN"
  }
]
```

## Current Status

✅ **Phase 1 Complete**: Login and book discovery
✅ **Phase 2 Complete**: Book selection and highlight extraction
✅ **Phase 3 Complete**: JSON export functionality

## Troubleshooting

### No books found
- Ensure you're logged into the correct Amazon account
- Check that you have Kindle books with highlights
- Try refreshing the page manually in the browser
- The page structure may have changed - check the console output for debugging info

### Login issues
- Make sure you complete the full login process including any 2FA
- Navigate to https://read.amazon.com/notebook manually if needed
- Wait for the page to fully load before pressing Enter

### Chrome driver issues
- The script automatically downloads the appropriate ChromeDriver
- Ensure Chrome browser is installed and up to date
- If issues persist, try updating Chrome or reinstalling the dependencies

### No highlights found
- Ensure the selected book actually has highlights
- Check that you're viewing the correct book (some books may have similar titles)
- The highlights page may take time to load - the script includes delays for this

## Development

The project is structured to be easily extensible:

- `KindleHighlightsExtractor` class handles the main functionality
- Login verification uses multiple fallback methods
- Book discovery uses the same selectors as the Obsidian Kindle plugin for maximum compatibility
- Highlight extraction handles pagination and various data formats
- Rich console output provides clear feedback and debugging information

## Technical Details

This implementation is based on the [Obsidian Kindle Plugin](https://github.com/hadynz/obsidian-kindle-plugin) TypeScript code, ensuring:

- Same CSS selectors for maximum compatibility
- Same URL patterns for navigation
- Same data extraction logic
- Same pagination handling

## Next Steps

1. **Batch Processing**: Handle multiple books at once
2. **Different Formats**: Export to Markdown, CSV, or other formats
3. **Incremental Updates**: Only extract new highlights since last sync
4. **Error Recovery**: Better handling of network issues and page changes
5. **Regional Support**: Support for different Amazon regions

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 