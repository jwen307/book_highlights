#!/usr/bin/env python3
"""
Test script for Anki flashcard creation

Tests the Anki flashcard creator with sample data.
"""

import sys
import os
import tempfile
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from create_anki_flashcards import AnkiFlashcardCreator

console = Console()


def create_test_markdown_file():
    """Create a test markdown file for testing."""
    
    test_content = """# The Psychology of Money

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

**Q4:** What is the difference between getting money and keeping money?

**A4:** Getting money and keeping money require different skills and mindsets.

---

**Q5:** How do personal experiences influence financial behavior?

**A5:** Personal history and experiences heavily influence financial behavior more than mathematical calculations.

---

## 📖 Highlights (7 total)

### Highlight 1

The highest form of wealth is the ability to wake up every morning and say, 'I can do whatever I want today.'

*Location: Location 123, Page: 15, Color: yellow*

**Note:** This defines true financial freedom.

---
"""
    
    # Create a temporary file
    temp_dir = Path(tempfile.gettempdir())
    test_file = temp_dir / "test-psychology-of-money-complete.md"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    return test_file


def test_markdown_parsing():
    """Test the markdown parsing functionality."""
    console.print(Panel.fit(
        "[bold blue]Testing Markdown Parsing[/bold blue]\n"
        "Testing the ability to parse markdown files and extract data",
        title="Parsing Test"
    ))
    
    # Create test file
    test_file = create_test_markdown_file()
    console.print(f"[green]✓ Created test file: {test_file.name}[/green]")
    
    # Test parsing
    creator = AnkiFlashcardCreator()
    book_data = creator.parse_markdown_file(test_file)
    
    if book_data:
        console.print("[green]✓ Markdown parsing successful![/green]")
        
        # Display parsed data
        console.print(f"\n[bold]Parsed Data:[/bold]")
        console.print(f"• Book: {book_data['book_title']}")
        console.print(f"• Author: {book_data['author']}")
        console.print(f"• ASIN: {book_data['asin']}")
        console.print(f"• Summary: {book_data['summary'][:80]}...")
        console.print(f"• Key Points: {len(book_data['key_points'])}")
        console.print(f"• Flashcards: {len(book_data['flashcards'])}")
        
        # Show flashcards
        console.print(f"\n[bold]Flashcards:[/bold]")
        for i, flashcard in enumerate(book_data['flashcards'], 1):
            console.print(f"Q{i}: {flashcard['question']}")
            console.print(f"A{i}: {flashcard['answer']}")
            console.print("---")
        
        # Clean up
        test_file.unlink()
        console.print(f"[green]✓ Test file cleaned up[/green]")
        
        return True
    else:
        console.print("[red]✗ Markdown parsing failed[/red]")
        return False


def test_anki_connect():
    """Test AnkiConnect connectivity."""
    console.print(Panel.fit(
        "[bold blue]Testing AnkiConnect[/bold blue]\n"
        "Testing connection to AnkiConnect API",
        title="AnkiConnect Test"
    ))
    
    creator = AnkiFlashcardCreator()
    
    if creator.test_anki_connect():
        console.print("[green]✓ AnkiConnect is available[/green]")
        return True
    else:
        console.print("[yellow]⚠ AnkiConnect is not available (this is expected if Anki is not running)[/yellow]")
        console.print("[blue]This test will pass if AnkiConnect responds, even if Anki is not running[/blue]")
        return False


def test_deck_creation():
    """Test deck creation functionality."""
    console.print(Panel.fit(
        "[bold blue]Testing Deck Creation[/bold blue]\n"
        "Testing the ability to create Anki decks",
        title="Deck Test"
    ))
    
    creator = AnkiFlashcardCreator()
    
    # Test deck creation
    test_deck_name = "Kindle Highlights::Test-Deck"
    if creator.create_deck(test_deck_name):
        console.print(f"[green]✓ Deck '{test_deck_name}' created successfully[/green]")
        return True
    else:
        console.print(f"[yellow]⚠ Could not create deck '{test_deck_name}' (Anki may not be running)[/yellow]")
        return False


def main():
    """Main test function."""
    try:
        console.print("[bold blue]Testing Anki Flashcard Creation Functionality[/bold blue]\n")
        
        # Test 1: Markdown parsing
        parsing_success = test_markdown_parsing()
        
        # Test 2: AnkiConnect connectivity
        anki_success = test_anki_connect()
        
        # Test 3: Deck creation
        deck_success = test_deck_creation()
        
        # Summary
        console.print("\n" + "="*60)
        console.print("[bold]Test Results:[/bold]")
        console.print(f"• Markdown Parsing: {'✓' if parsing_success else '✗'}")
        console.print(f"• AnkiConnect: {'✓' if anki_success else '⚠'}")
        console.print(f"• Deck Creation: {'✓' if deck_success else '⚠'}")
        
        if parsing_success:
            console.print("\n[bold green]🎉 Core functionality is working![/bold green]")
            console.print("[green]The script can parse markdown files and extract flashcard data.[/green]")
            
            if anki_success and deck_success:
                console.print("[green]Anki integration is also working![/green]")
            else:
                console.print("[yellow]Anki integration requires Anki to be running with AnkiConnect installed.[/yellow]")
            
            sys.exit(0)
        else:
            console.print("\n[bold red]❌ Core functionality failed![/bold red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 