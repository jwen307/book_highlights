#!/usr/bin/env python3
"""
Test script for config and save functionality
"""

from config import DEFAULT_SAVE_LOCATION, ensure_save_directory
from models import Book, Highlight
from datetime import datetime
import os

def test_config():
    """Test the config functionality."""
    print(f"Default save location: {DEFAULT_SAVE_LOCATION}")
    
    # Test directory creation
    save_dir = ensure_save_directory()
    print(f"Save directory: {save_dir}")
    print(f"Directory exists: {os.path.exists(save_dir)}")

def test_save_functionality():
    """Test the save functionality with sample data."""
    from kindle_highlights import KindleHighlightsExtractor
    
    # Create sample book
    book = Book(
        id="test_book_1",
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        asin="B000FCKPHG",
        url="https://www.amazon.com/dp/B000FCKPHG",
        image_url=None,
        last_annotated_date=datetime.now()
    )
    
    # Create sample highlights
    highlights = [
        Highlight(
            id="highlight_1",
            text="So we beat on, boats against the current, borne back ceaselessly into the past.",
            location="Location 1234",
            page="180",
            note="This is a note about the highlight",
            color="yellow",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight_2",
            text="I hope she'll be a fool—that's the best thing a girl can be in this world, a beautiful little fool.",
            location="Location 567",
            page="17",
            note=None,
            color="blue",
            created_date=datetime.now()
        )
    ]
    
    # Test save functions
    extractor = KindleHighlightsExtractor()
    
    print("\nTesting Markdown save...")
    extractor.save_highlights_to_markdown(highlights, book)
    
    print("\nTesting JSON save...")
    extractor.save_highlights_to_json(highlights, book)

if __name__ == "__main__":
    print("Testing config functionality...")
    test_config()
    
    print("\nTesting save functionality...")
    test_save_functionality()
    
    print("\nTest completed!") 