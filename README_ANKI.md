# Anki Flashcard Integration

This document explains how to use the Anki flashcard creation feature that converts your Kindle highlights into Anki flashcards for spaced repetition learning.

## Overview

The Anki integration allows you to:
- Find generated markdown files from your Kindle highlights
- Select a book to create flashcards for
- Automatically create Anki flashcards with questions on the front and comprehensive answers on the back
- Organize flashcards in a hierarchical deck structure

## Prerequisites

### 1. Install Anki
Download and install Anki from [https://apps.ankiweb.net/](https://apps.ankiweb.net/)

### 2. Install AnkiConnect Addon
1. Open Anki
2. Go to **Tools** → **Add-ons**
3. Click **Browse & Install**
4. Enter the code: `2055492159`
5. Click **OK** and restart Anki

### 3. Verify AnkiConnect Installation
1. Start Anki
2. The AnkiConnect addon should be active (you'll see it in the add-ons list)
3. AnkiConnect runs a local server on `http://localhost:8765`

## Usage

### Step 1: Generate Kindle Highlights
First, use the main script to extract highlights and generate summaries:

```bash
python kindle_highlights_with_summary.py
```

This will create a markdown file like `{Book-Title}-complete.md` in your save directory.

### Step 2: Create Anki Flashcards
Run the Anki flashcard creator:

```bash
python create_anki_flashcards.py
```

The script will:
1. Find all `*-complete.md` files in your save directory
2. Display them in a table for selection
3. Parse the selected file to extract book info, summary, key points, and flashcards
4. Test the AnkiConnect connection
5. Create a single comprehensive flashcard in Anki

### Step 3: Review in Anki
1. Open Anki
2. Look for the deck: `Kindle Highlights::{Book-Title}`
3. Start reviewing your new flashcard

## Flashcard Structure

### Front of the Card
- Book title and author
- All flashcard questions from the markdown file

**Example:**
```
**The Psychology of Money**
by Morgan Housel

**Questions:**
Q1: What is the highest form of wealth according to the book?
Q2: What is money's greatest intrinsic value?
Q3: What does the book say about wealth and appearances?
Q4: What is the difference between getting money and keeping money?
Q5: How do personal experiences influence financial behavior?
```

### Back of the Card
- Book metadata (title, author, ASIN)
- AI-generated summary
- Key points from the book
- Answers to all questions

**Example:**
```
**Book:** The Psychology of Money
**Author:** Morgan Housel
**ASIN:** B08D9WJ9G7

**Summary:**
The book explores how personal psychology and behavior patterns shape financial decisions more than mathematical calculations.

**Key Points:**
1. Wealth is often invisible - it's the money not spent
2. Financial freedom is about control over your time
3. Personal history and experiences heavily influence financial behavior
4. Getting money and keeping money require different skills
5. Appearances can be deceiving in wealth assessment

**Answers:**
Q1: The ability to wake up every morning and say, 'I can do whatever I want today.'
Q2: Its ability to give you control over your time.
Q3: Wealth is what you don't see - the cars not purchased, diamonds not bought, watches not worn.
Q4: Getting money and keeping money require different skills and mindsets.
Q5: Personal history and experiences heavily influence financial behavior more than mathematical calculations.
```

## Deck Organization

Flashcards are organized in a hierarchical structure:
- **Main Deck:** `Kindle Highlights`
- **Sub-decks:** `Kindle Highlights::{Book-Title}`

This allows you to:
- Study all your book flashcards together
- Focus on specific books when needed
- Keep your Kindle highlights separate from other Anki content

## Testing

### Test the Core Functionality
```bash
python test_anki_creation.py
```

This test will:
- Test markdown parsing with sample data
- Test AnkiConnect connectivity
- Test deck creation functionality

### Test with Real Data
1. Generate a markdown file using the main script
2. Run the Anki creator
3. Verify the flashcard appears in Anki

## Troubleshooting

### "Cannot connect to AnkiConnect"
- Make sure Anki is running
- Verify AnkiConnect addon is installed and enabled
- Check that AnkiConnect is running on `http://localhost:8765`

### "No markdown files found"
- Run the main Kindle highlights script first
- Check that files end with `-complete.md`
- Verify the save directory path in `config.py`

### "Failed to create deck"
- Make sure Anki is running
- Check that you have permission to create decks
- Try restarting Anki

### "Failed to create flashcard"
- Check Anki's error log (Help → About → Show Debug Info)
- Verify the note type is "Basic"
- Make sure the deck exists

## Configuration

### AnkiConnect URL
The default AnkiConnect URL is `http://localhost:8765`. You can modify this in the script if needed:

```python
ANKI_CONNECT_URL = "http://localhost:8765"
```

### Deck Name
The default deck name is "Kindle Highlights". You can change this:

```python
DEFAULT_DECK_NAME = "Kindle Highlights"
```

### Note Type
The script uses the "Basic" note type. To use a different type, modify the `create_flashcard` method:

```python
"modelName": "Basic",  # Change to your preferred note type
```

## Advanced Usage

### Custom Note Types
You can create custom note types in Anki for different flashcard layouts:

1. In Anki, go to **Tools** → **Manage Note Types**
2. Create a new note type based on "Basic"
3. Add fields like "Book", "Author", "Summary", "Questions", "Answers"
4. Modify the script to use your custom note type

### Multiple Flashcards per Book
Currently, the script creates one comprehensive flashcard per book. To create individual flashcards for each question:

1. Modify the `create_flashcards_from_book` method
2. Create separate flashcards for each Q&A pair
3. Use different note types for different content types

### Tags and Metadata
The script adds the tag "kindle-highlights" to all flashcards. You can add more tags:

```python
"tags": ["kindle-highlights", "book-summary", "ai-generated"]
```

## Integration with Spaced Repetition

The beauty of Anki integration is that you get spaced repetition learning:

1. **Review Schedule:** Anki will show you cards at optimal intervals
2. **Retention Tracking:** Monitor your learning progress
3. **Customizable Intervals:** Adjust review timing based on difficulty
4. **Statistics:** Track your performance over time

## Tips for Effective Learning

1. **Review Regularly:** Use Anki's spaced repetition to reinforce concepts
2. **Customize Intervals:** Adjust card intervals based on your learning pace
3. **Add Personal Notes:** Use Anki's note editing to add your own insights
4. **Study in Context:** Review related cards together
5. **Track Progress:** Monitor your retention rates and adjust study habits

## File Structure

```
book_highlights/
├── create_anki_flashcards.py    # Main Anki creation script
├── test_anki_creation.py        # Test script for Anki functionality
├── kindle_highlights_with_summary.py  # Main script (generates markdown)
└── README_ANKI.md              # This documentation
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the test script to isolate problems
3. Check Anki's debug information
4. Verify AnkiConnect is working with a simple test
5. Review the AnkiConnect documentation: [https://foosoft.net/projects/anki-connect/](https://foosoft.net/projects/anki-connect/) 