#!/usr/bin/env python3
"""
Kindle Highlights with LLM Summary

A comprehensive script that extracts Kindle highlights from Amazon's notebook,
generates summaries and key points using LLM, and saves everything to markdown files.
"""

import sys
import os
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from kindle_highlights import KindleHighlightsExtractor
from llm_summarizer import LLMSummarizer
from models import Book, Highlight
from config import ensure_save_directory

console = Console()


class KindleHighlightsWithSummary:
    """Main class that combines Kindle highlights extraction with LLM summarization."""
    
    def __init__(self):
        """Initialize the combined extractor and summarizer."""
        self.extractor = KindleHighlightsExtractor()
        self.summarizer = LLMSummarizer()
        self.save_dir = ensure_save_directory()
    
    def run(self) -> None:
        """Main execution method."""
        try:
            self._show_welcome_message()
            
            # Step 1: Setup and login
            if not self._setup_and_login():
                return
            
            # Step 2: Get available books
            books = self._get_available_books()
            if not books:
                return
            
            # Step 3: Select book and extract highlights
            selected_book = self._select_book(books)
            if not selected_book:
                return
            
            highlights = self._extract_highlights(selected_book)
            if not highlights:
                return
            
            # Step 4: Generate LLM summary
            summary_data = self._generate_summary(highlights, selected_book)
            
            # Step 5: Save everything to markdown
            self._save_comprehensive_markdown(selected_book, highlights, summary_data)
            
            # Step 6: Show final summary
            self._show_final_summary(selected_book, highlights, summary_data)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Process interrupted by user.[/yellow]")
        except Exception as e:
            console.print(f"[red]✗ Unexpected error: {e}[/red]")
        finally:
            self._cleanup()
    
    def _show_welcome_message(self) -> None:
        """Display the welcome message."""
        console.print(Panel.fit(
            "[bold blue]Kindle Highlights with LLM Summary[/bold blue]\n"
            "Extract highlights, generate summaries, and save everything to markdown",
            border_style="blue"
        ))
    
    def _setup_and_login(self) -> bool:
        """Setup the extractor and handle login."""
        console.print("[bold blue]Step 1: Setting up Kindle Highlights Extractor[/bold blue]")
        
        try:
            self.extractor.setup_driver()
            self.extractor.launch_amazon_notebook()
            
            console.print("[bold blue]Step 2: Login to Amazon[/bold blue]")
            if self.extractor.wait_for_login():
                console.print("[green]✓ Login successful![/green]")
                return True
            else:
                console.print("[red]✗ Login failed or timed out[/red]")
                return False
                
        except Exception as e:
            console.print(f"[red]✗ Setup failed: {e}[/red]")
            return False
    
    def _get_available_books(self) -> List[Book]:
        """Get available books from the notebook."""
        console.print("[bold blue]Step 3: Scanning for available books[/bold blue]")
        
        books = self.extractor.get_available_books()
        if not books:
            console.print("[red]No books found. Please check your account or try refreshing.[/red]")
            return []
        
        console.print(f"[green]✓ Found {len(books)} books[/green]")
        return books
    
    def _select_book(self, books: List[Book]) -> Optional[Book]:
        """Allow user to select a book."""
        console.print("[bold blue]Step 4: Select a book[/bold blue]")
        
        self.extractor.display_books(books)
        selected_book = self.extractor.select_book_interactive(books)
        
        if selected_book:
            console.print(f"[green]✓ Selected: {selected_book.title}[/green]")
        else:
            console.print("[yellow]No book selected[/yellow]")
        
        return selected_book
    
    def _extract_highlights(self, book: Book) -> List[Highlight]:
        """Extract highlights from the selected book."""
        console.print(f"[bold blue]Step 5: Extracting highlights from '{book.title}'[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Extracting highlights...", total=None)
            
            highlights = self.extractor.extract_highlights_from_book(book)
            
            progress.update(task, description=f"✓ Extracted {len(highlights)} highlights")
        
        if highlights:
            console.print(f"[green]✓ Successfully extracted {len(highlights)} highlights[/green]")
        else:
            console.print("[yellow]No highlights found for this book[/yellow]")
        
        return highlights
    
    def _generate_summary(self, highlights: List[Highlight], book: Book) -> Optional[dict]:
        """Generate LLM summary of the highlights."""
        console.print(f"[bold blue]Step 6: Generating LLM summary for '{book.title}'[/bold blue]")
        
        if not self.summarizer.client:
            console.print("[red]✗ LLM summarizer not available. Check your OpenAI API key.[/red]")
            return None
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating summary...", total=None)
            
            summary_data = self.summarizer.summarize_highlights(highlights, book)
            
            progress.update(task, description="✓ Summary generated")
        
        if summary_data:
            console.print("[green]✓ LLM summary generated successfully[/green]")
        else:
            console.print("[yellow]⚠ Could not generate LLM summary[/yellow]")
        
        return summary_data
    
    def _save_comprehensive_markdown(self, book: Book, highlights: List[Highlight], summary_data: Optional[dict]) -> None:
        """Save everything to a comprehensive markdown file."""
        console.print("[bold blue]Step 7: Saving comprehensive markdown file[/bold blue]")
        
        try:
            # Create filename
            safe_title = self._sanitize_filename(book.title)
            filename = f"{safe_title}-complete.md"
            filepath = os.path.join(self.save_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"# {book.title}\n\n")
                f.write(f"**Author:** {book.author}\n\n")
                if book.asin:
                    f.write(f"**ASIN:** {book.asin}\n\n")
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
                f.write(f"## 📖 Highlights ({len(highlights)} total)\n\n")
                
                for i, highlight in enumerate(highlights, 1):
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
            
            console.print(f"[green]✓ Comprehensive markdown saved to: {filepath}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Error saving comprehensive markdown: {e}[/red]")
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize a title for use as a filename."""
        import re
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        return re.sub(r'[-\s]+', '-', safe_title)
    
    def _show_final_summary(self, book: Book, highlights: List[Highlight], summary_data: Optional[dict]) -> None:
        """Show the final summary of what was accomplished."""
        console.print("\n" + "="*60)
        console.print("[bold green]🎉 PROCESS COMPLETE![/bold green]")
        console.print("="*60)
        
        console.print(f"[bold]Book:[/bold] {book.title}")
        console.print(f"[bold]Author:[/bold] {book.author}")
        console.print(f"[bold]Highlights extracted:[/bold] {len(highlights)}")
        
        if summary_data:
            console.print(f"[bold]LLM Summary:[/bold] {summary_data['summary']}")
            console.print(f"[bold]Key points generated:[/bold] {len(summary_data['key_points'])}")
            if 'flashcards' in summary_data and summary_data['flashcards']:
                console.print(f"[bold]Flashcards generated:[/bold] {len(summary_data['flashcards'])}")
        
        console.print(f"[bold]Save location:[/bold] {self.save_dir}")
        
        # Show the file that was created
        safe_title = self._sanitize_filename(book.title)
        complete_file = f"{safe_title}-complete.md"
        
        if os.path.exists(os.path.join(self.save_dir, complete_file)):
            console.print(f"\n[bold]File created:[/bold]")
            console.print(f"  • {complete_file}")
        
        console.print("\n[green]✓ All done! You can now review your highlights and summary.[/green]")
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'extractor'):
            self.extractor._cleanup()


def main():
    """Main entry point."""
    processor = KindleHighlightsWithSummary()
    processor.run()


if __name__ == "__main__":
    main() 