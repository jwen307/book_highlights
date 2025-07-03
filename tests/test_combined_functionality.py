#!/usr/bin/env python3
"""
Test script for combined Kindle Highlights + LLM Summary functionality

Tests the complete pipeline using sample data to ensure everything works together.
"""

import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from helpers.models import Book, Highlight
from helpers.config_helper import load_config, save_config, ensure_save_directory
from helpers.llm_helper import LLMSummarizer
from helpers.amazon_helper import KindleHighlightsExtractor

console = Console()


def create_test_data():
    """Create comprehensive test data for the combined functionality."""
    
    # Create a test book
    test_book = Book(
        id="test-book-123",
        title="The Psychology of Money",
        author="Morgan Housel",
        asin="B08D9WJ9G7",
        url="https://read.amazon.com/notebook?asin=B08D9WJ9G7",
        last_annotated_date=datetime.now()
    )
    
    # Create sample highlights
    test_highlights = [
        Highlight(
            id="highlight-1",
            text="The highest form of wealth is the ability to wake up every morning and say, 'I can do whatever I want today.'",
            location="Location 123",
            page="15",
            note="This defines true financial freedom.",
            color="yellow",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-2",
            text="Money's greatest intrinsic value is its ability to give you control over your time.",
            location="Location 456",
            page="23",
            note="Time is the ultimate luxury.",
            color="blue",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-3",
            text="The world is full of people who look modest but are wealthy and people who look rich but live at the razor's edge of insolvency.",
            location="Location 789",
            page="27",
            note="Appearances can be deceiving.",
            color="pink",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-4",
            text="Wealth is what you don't see. It's the cars not purchased. The diamonds not bought. The watches not worn.",
            location="Location 1011",
            page="31",
            note="Wealth is invisible assets.",
            color="yellow",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-5",
            text="The ability to do what you want, when you want, with who you want, for as long as you want, is priceless.",
            location="Location 1213",
            page="82",
            note="Freedom is the ultimate goal.",
            color="orange",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-6",
            text="Getting money is one thing. Keeping it is another.",
            location="Location 1415",
            page="95",
            note="Preservation is as important as accumulation.",
            color="blue",
            created_date=datetime.now()
        ),
        Highlight(
            id="highlight-7",
            text="The more you want something to be true, the more likely you are to believe a story that overestimates the odds of it being true.",
            location="Location 1617",
            page="108",
            note="Bias affects financial decisions.",
            color="yellow",
            created_date=datetime.now()
        )
    ]
    
    return test_book, test_highlights


def test_llm_summarization():
    """Test the LLM summarization component."""
    console.print(Panel.fit(
        "[bold blue]Testing LLM Summarization[/bold blue]\n"
        "Testing the LLM summarizer with sample highlights",
        title="LLM Test"
    ))
    
    # Create test data
    test_book, test_highlights = create_test_data()
    
    # Initialize summarizer
    summarizer = LLMSummarizer()
    
    if not summarizer.client:
        console.print("[red]✗ LLM summarizer not available. Check your OpenAI API key.[/red]")
        return False, None, None
    
    # Test summarization
    console.print("[yellow]Generating summary...[/yellow]")
    summary_data = summarizer.summarize_highlights(test_highlights, test_book)
    
    if summary_data:
        console.print("[green]✓ LLM summarization successful![/green]")
        return True, test_book, test_highlights, summary_data
    else:
        console.print("[red]✗ LLM summarization failed[/red]")
        return False, test_book, test_highlights, None


def test_comprehensive_save(test_book, test_highlights, summary_data):
    """Test saving everything to a comprehensive markdown file."""
    console.print(Panel.fit(
        "[bold blue]Testing Comprehensive Save[/bold blue]\n"
        "Testing the complete markdown save functionality",
        title="Save Test"
    ))
    
    try:
        save_dir = ensure_save_directory()
        
        # Create filename
        safe_title = test_book.title.replace(' ', '-').replace(':', '').replace('/', '-')
        filename = f"{safe_title}-test-complete.md"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {test_book.title}\n\n")
            f.write(f"**Author:** {test_book.author}\n\n")
            f.write(f"**ASIN:** {test_book.asin}\n\n")
            f.write("---\n\n")
            
            # Write LLM summary if available
            if summary_data:
                f.write("## 📝 AI-Generated Summary\n\n")
                f.write(f"**One-Sentence Summary:** {summary_data['summary']}\n\n")
                
                f.write("**Key Points:**\n")
                for i, point in enumerate(summary_data['key_points'], 1):
                    f.write(f"{i}. {point}\n")
                f.write("\n")
                
                # Add flashcards if available
                if 'flashcards' in summary_data and summary_data['flashcards']:
                    f.write("## 🎯 Flashcards\n\n")
                    f.write("*Test your understanding of the key concepts*\n\n")
                    for i, flashcard in enumerate(summary_data['flashcards'], 1):
                        f.write(f"**Q{i}:** {flashcard['question']}\n\n")
                        f.write(f"**A{i}:** {flashcard['answer']}\n\n")
                        f.write("---\n\n")
                
                f.write("---\n\n")
            
            # Write highlights
            f.write(f"## 📖 Highlights ({len(test_highlights)} total)\n\n")
            
            for i, highlight in enumerate(test_highlights, 1):
                f.write(f"### Highlight {i}\n\n")
                f.write(f"{highlight.text}\n\n")
                
                # Add metadata if available
                metadata_parts = []
                if highlight.location:
                    metadata_parts.append(f"Location: {highlight.location}")
                if highlight.page:
                    metadata_parts.append(f"Page: {highlight.page}")
                if highlight.color:
                    metadata_parts.append(f"Color: {highlight.color}")
                
                if metadata_parts:
                    f.write(f"*{', '.join(metadata_parts)}*\n\n")
                
                if highlight.note:
                    f.write(f"**Note:** {highlight.note}\n\n")
                
                f.write("---\n\n")
        
        console.print(f"[green]✓ Complete markdown saved to: {filepath}[/green]")
        
        # Verify file was created and has content
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            console.print(f"[green]✓ Complete file created successfully (size: {file_size} bytes)[/green]")
            return True
        else:
            console.print("[red]✗ Complete file was not created[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]✗ Error saving test file: {e}[/red]")
        return False


def main():
    """Main test function."""
    try:
        console.print("[bold blue]Testing Combined Kindle Highlights + LLM Summary Functionality[/bold blue]\n")
        
        # Test 1: LLM Summarization
        llm_success, test_book, test_highlights, summary_data = test_llm_summarization()
        
        if not llm_success:
            console.print("[red]❌ LLM test failed. Cannot proceed with combined test.[/red]")
            sys.exit(1)
        
        # Test 2: Comprehensive Save
        save_success = test_comprehensive_save(test_book, test_highlights, summary_data)
        
        if save_success:
            console.print("\n[bold green]🎉 All tests passed![/bold green]")
            console.print("\n[bold]Summary:[/bold]")
            console.print(f"• Book: {test_book.title}")
            console.print(f"• Highlights: {len(test_highlights)}")
            console.print(f"• LLM Summary: {'✓' if summary_data else '✗'}")
            if summary_data and 'flashcards' in summary_data:
                console.print(f"• Flashcards: {len(summary_data['flashcards'])} generated")
            console.print(f"• Save functionality: ✓")
            
            if summary_data:
                console.print(f"\n[bold]Generated Summary:[/bold]")
                console.print(f"[cyan]{summary_data['summary']}[/cyan]")
                
                console.print(f"\n[bold]Key Points:[/bold]")
                for i, point in enumerate(summary_data['key_points'], 1):
                    console.print(f"{i}. {point}")
                
                if 'flashcards' in summary_data and summary_data['flashcards']:
                    console.print(f"\n[bold]Flashcards:[/bold]")
                    for i, flashcard in enumerate(summary_data['flashcards'], 1):
                        console.print(f"Q{i}: {flashcard['question']}")
                        console.print(f"A{i}: {flashcard['answer']}")
                        console.print("---")
            
            console.print("\n[green]✓ The combined functionality is working correctly![/green]")
            sys.exit(0)
        else:
            console.print("\n[bold red]❌ Save test failed![/bold red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main() 