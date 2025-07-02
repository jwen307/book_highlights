#!/usr/bin/env python3
"""
Test script for LLM Summarizer

Tests the LLM summarizer with a small example set of highlights to ensure it works correctly.
"""

import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from models import Book, Highlight
from llm_summarizer import LLMSummarizer

console = Console()


def create_test_highlights() -> tuple[Book, list[Highlight]]:
    """Create a test book and sample highlights for testing."""
    
    # Create a test book
    test_book = Book(
        id="test-book-123",
        title="Atomic Habits",
        author="James Clear",
        asin="B07RFSSYBH",
        url="https://read.amazon.com/notebook?asin=B07RFSSYBH",
        last_annotated_date=datetime.now()
    )
    
    # Create sample highlights
    test_highlights = [
        Highlight(
            id="highlight-1",
            text="Every action you take is a vote for the type of person you wish to become.",
            location="Location 123",
            page="15",
            note="This is the core principle of identity-based habits.",
            color="yellow",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-2",
            text="Habits are the compound interest of self-improvement.",
            location="Location 456",
            page="23",
            note="Small changes compound over time.",
            color="blue",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-3",
            text="You do not rise to the level of your goals. You fall to the level of your systems.",
            location="Location 789",
            page="27",
            note="Systems are more important than goals.",
            color="pink",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-4",
            text="The most effective way to change your habits is to focus not on what you want to achieve, but on who you wish to become.",
            location="Location 1011",
            page="31",
            note="Identity change is the key to lasting change.",
            color="yellow",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-5",
            text="Environment is the invisible hand that shapes human behavior.",
            location="Location 1213",
            page="82",
            note="Design your environment to support good habits.",
            color="orange",
            created_date=datetime.now()
        )
    ]
    
    return test_book, test_highlights


def test_llm_summarizer():
    """Test the LLM summarizer with sample data."""
    
    console.print(Panel.fit(
        "[bold blue]Testing LLM Summarizer[/bold blue]\n"
        "This test will verify that the LLM summarizer can process highlights and generate summaries.",
        title="LLM Summarizer Test"
    ))
    
    # Create test data
    console.print("[yellow]Creating test data...[/yellow]")
    test_book, test_highlights = create_test_highlights()
    
    console.print(f"[green]✓ Created test book: '{test_book.title}' by {test_book.author}[/green]")
    console.print(f"[green]✓ Created {len(test_highlights)} test highlights[/green]")
    
    # Display sample highlights
    console.print("\n[bold]Sample Highlights:[/bold]")
    for i, highlight in enumerate(test_highlights[:3], 1):
        console.print(f"{i}. {highlight.text[:80]}...")
        if highlight.note:
            console.print(f"   Note: {highlight.note}")
    
    # Initialize the LLM summarizer
    console.print("\n[yellow]Initializing LLM summarizer...[/yellow]")
    summarizer = LLMSummarizer()
    
    if not summarizer.client:
        console.print("[red]✗ Failed to initialize OpenAI client. Please check your API key.[/red]")
        return False
    
    console.print("[green]✓ LLM summarizer initialized successfully[/green]")
    
    # Test the summarization
    console.print("\n[yellow]Testing highlight summarization...[/yellow]")
    try:
        result = summarizer.summarize_highlights(test_highlights, test_book)
        
        if result:
            console.print("[green]✓ Summarization completed successfully![/green]")
            
            # Display the results
            console.print("\n[bold green]Generated Summary:[/bold green]")
            console.print(f"[cyan]{result['summary']}[/cyan]")
            
            console.print("\n[bold green]Key Points:[/bold green]")
            for i, point in enumerate(result['key_points'], 1):
                console.print(f"{i}. {point}")
            
            console.print("\n[green]✓ Test passed! The LLM summarizer is working correctly.[/green]")
            return True
        else:
            console.print("[red]✗ Summarization failed - no result returned[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ Error during summarization: {e}[/red]")
        return False


def main():
    """Main test function."""
    try:
        success = test_llm_summarizer()
        
        if success:
            console.print("\n[bold green]🎉 All tests passed![/bold green]")
            sys.exit(0)
        else:
            console.print("\n[bold red]❌ Tests failed![/bold red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 