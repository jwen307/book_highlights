#!/usr/bin/env python3
"""
Test script for flashcard generation functionality

Tests that the LLM can generate flashcards from highlights.
"""

import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from models import Book, Highlight
from helpers.llm_helper import LLMSummarizer

console = Console()


def create_test_data():
    """Create test data for flashcard generation."""
    
    test_book = Book(
        id="test-book-123",
        title="Atomic Habits",
        author="James Clear",
        asin="B07RFSSYBH",
        url="https://read.amazon.com/notebook?asin=B07RFSSYBH",
        last_annotated_date=datetime.now()
    )
    
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


def test_flashcard_generation():
    """Test flashcard generation."""
    console.print(Panel.fit(
        "[bold blue]Testing Flashcard Generation[/bold blue]\n"
        "Testing the LLM's ability to generate flashcards from highlights",
        title="Flashcard Test"
    ))
    
    # Create test data
    test_book, test_highlights = create_test_data()
    
    # Initialize summarizer
    summarizer = LLMSummarizer()
    
    if not summarizer.client:
        console.print("[red]✗ LLM summarizer not available. Check your OpenAI API key.[/red]")
        return False
    
    # Test summarization with flashcards
    console.print("[yellow]Generating summary and flashcards...[/yellow]")
    summary_data = summarizer.summarize_highlights(test_highlights, test_book)
    
    if summary_data and 'flashcards' in summary_data:
        console.print("[green]✓ Flashcard generation successful![/green]")
        
        # Display results
        console.print(f"\n[bold]Generated Summary:[/bold]")
        console.print(f"[cyan]{summary_data['summary']}[/cyan]")
        
        console.print(f"\n[bold]Key Points:[/bold]")
        for i, point in enumerate(summary_data['key_points'], 1):
            console.print(f"{i}. {point}")
        
        console.print(f"\n[bold]Flashcards Generated:[/bold] {len(summary_data['flashcards'])}")
        for i, flashcard in enumerate(summary_data['flashcards'], 1):
            console.print(f"\n[bold cyan]Q{i}:[/bold cyan] {flashcard['question']}")
            console.print(f"[bold green]A{i}:[/bold green] {flashcard['answer']}")
        
        return True
    else:
        console.print("[red]✗ Flashcard generation failed[/red]")
        if summary_data:
            console.print("[yellow]Summary generated but no flashcards found[/yellow]")
        return False


def main():
    """Main test function."""
    try:
        success = test_flashcard_generation()
        
        if success:
            console.print("\n[bold green]🎉 Flashcard test passed![/bold green]")
            sys.exit(0)
        else:
            console.print("\n[bold red]❌ Flashcard test failed![/bold red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 