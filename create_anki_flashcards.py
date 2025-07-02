#!/usr/bin/env python3
"""
Anki Flashcard Creator for Kindle Highlights

This script finds generated markdown files, lets you choose one, and creates
Anki flashcards using the AnkiConnect API.
"""

import os
import json
import re
import requests
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from config import ensure_save_directory

console = Console()

# AnkiConnect API configuration
ANKI_CONNECT_URL = "http://localhost:8765"
DEFAULT_DECK_NAME = "Kindle Highlights"


class AnkiFlashcardCreator:
    """Creates Anki flashcards from markdown files."""
    
    def __init__(self):
        """Initialize the Anki flashcard creator."""
        self.save_dir = ensure_save_directory()
        self.anki_url = ANKI_CONNECT_URL
    
    def find_markdown_files(self) -> List[Path]:
        """Find all markdown files in the save directory."""
        md_files = []
        for file_path in Path(self.save_dir).glob("*-complete.md"):
            if file_path.is_file():
                md_files.append(file_path)
        
        return sorted(md_files)
    
    def display_available_files(self, md_files: List[Path]) -> None:
        """Display available markdown files in a table."""
        if not md_files:
            console.print("[red]No markdown files found in the save directory.[/red]")
            console.print(f"[blue]Save directory: {self.save_dir}[/blue]")
            return
        
        table = Table(title="Available Markdown Files")
        table.add_column("Number", style="cyan", no_wrap=True)
        table.add_column("Filename", style="green")
        table.add_column("Size", style="blue")
        
        for i, file_path in enumerate(md_files, 1):
            size = file_path.stat().st_size
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            table.add_row(str(i), file_path.name, size_str)
        
        console.print(table)
    
    def select_file(self, md_files: List[Path]) -> Optional[Path]:
        """Let user select a markdown file."""
        if not md_files:
            return None
        
        while True:
            try:
                choice = Prompt.ask(
                    f"\nSelect a file (1-{len(md_files)})",
                    default="1"
                )
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(md_files):
                    selected_file = md_files[choice_num - 1]
                    console.print(f"[green]✓ Selected: {selected_file.name}[/green]")
                    return selected_file
                else:
                    console.print(f"[red]Please enter a number between 1 and {len(md_files)}[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Selection cancelled[/yellow]")
                return None
    
    def parse_markdown_file(self, file_path: Path) -> Dict:
        """Parse the markdown file to extract book info, summary, key points, and flashcards."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract book title
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            book_title = title_match.group(1) if title_match else "Unknown Book"
            
            # Extract author
            author_match = re.search(r'\*\*Author:\*\* (.+)$', content, re.MULTILINE)
            author = author_match.group(1) if author_match else "Unknown Author"
            
            # Extract ASIN
            asin_match = re.search(r'\*\*ASIN:\*\* (.+)$', content, re.MULTILINE)
            asin = asin_match.group(1) if asin_match else None
            
            # Extract summary
            summary_match = re.search(r'\*\*One-Sentence Summary:\*\* (.+)$', content, re.MULTILINE)
            summary = summary_match.group(1) if summary_match else "No summary available"
            
            # Extract key points
            key_points = []
            key_points_section = re.search(r'\*\*Key Points:\*\*(.*?)(?=\n\n|\n##|\Z)', content, re.DOTALL)
            if key_points_section:
                points_text = key_points_section.group(1)
                points = re.findall(r'\d+\. (.+?)(?=\n\d+\.|\n\n|\Z)', points_text, re.DOTALL)
                key_points = [point.strip() for point in points if point.strip()]
            
            # Extract flashcards
            flashcards = []
            flashcards_section = re.search(r'## 🎯 Flashcards(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if flashcards_section:
                flashcard_text = flashcards_section.group(1)
                qa_pairs = re.findall(r'\*\*Q(\d+):\*\* (.+?)\n\n\*\*A\1:\*\* (.+?)(?=\n\n---|\n\n\*\*Q|\Z)', flashcard_text, re.DOTALL)
                for _, question, answer in qa_pairs:
                    flashcards.append({
                        'question': question.strip(),
                        'answer': answer.strip()
                    })
            
            return {
                'book_title': book_title,
                'author': author,
                'asin': asin,
                'summary': summary,
                'key_points': key_points,
                'flashcards': flashcards,
                'file_path': file_path
            }
            
        except Exception as e:
            console.print(f"[red]✗ Error parsing markdown file: {e}[/red]")
            return None
    
    def test_anki_connect(self) -> bool:
        """Test if AnkiConnect is available."""
        try:
            response = requests.post(
                self.anki_url,
                json={
                    "action": "version",
                    "version": 6
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    console.print(f"[green]✓ AnkiConnect is available (version: {result['result']})[/green]")
                    return True
            
            console.print("[red]✗ AnkiConnect is not responding correctly[/red]")
            return False
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗ Cannot connect to AnkiConnect: {e}[/red]")
            console.print("[yellow]Make sure Anki is running and the AnkiConnect addon is installed[/yellow]")
            return False
    
    def create_deck(self, deck_name: str) -> bool:
        """Create a deck in Anki if it doesn't exist."""
        try:
            response = requests.post(
                self.anki_url,
                json={
                    "action": "createDeck",
                    "version": 6,
                    "params": {
                        "deck": deck_name
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result:
                    console.print(f"[green]✓ Deck '{deck_name}' is ready[/green]")
                    return True
            
            console.print(f"[red]✗ Failed to create deck '{deck_name}'[/red]")
            return False
            
        except Exception as e:
            console.print(f"[red]✗ Error creating deck: {e}[/red]")
            return False
    
    def create_flashcard(self, deck_name: str, front: str, back: str) -> bool:
        """Create a single flashcard in Anki."""
        try:
            response = requests.post(
                self.anki_url,
                json={
                    "action": "addNote",
                    "version": 6,
                    "params": {
                        "note": {
                            "deckName": deck_name,
                            "modelName": "Basic",
                            "fields": {
                                "Front": front,
                                "Back": back
                            },
                            "options": {
                                "allowDuplicate": False
                            },
                            "tags": ["kindle-highlights"]
                        }
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'result' in result and result['result'] is not None:
                    return True
            
            return False
            
        except Exception as e:
            console.print(f"[red]✗ Error creating flashcard: {e}[/red]")
            return False
    
    def create_flashcards_from_book(self, book_data: Dict) -> bool:
        """Create flashcards for a book."""
        if not book_data['flashcards']:
            console.print("[yellow]No flashcards found in the markdown file[/yellow]")
            return False
        
        # Use the default deck name for all cards
        deck_name = DEFAULT_DECK_NAME
        
        # Create deck
        if not self.create_deck(deck_name):
            return False
        
        # Prepare back content
        back_content = []
        back_content.append(f"<b>Book:</b> {book_data['book_title']}")
        back_content.append(f"<b>Author:</b> {book_data['author']}")
        if book_data['asin']:
            back_content.append(f"<b>ASIN:</b> {book_data['asin']}")
        back_content.append("")
        
        back_content.append("<b>Summary:</b>")
        back_content.append(book_data['summary'])
        back_content.append("")
        
        if book_data['key_points']:
            back_content.append("<b>Key Points:</b>")
            for i, point in enumerate(book_data['key_points'], 1):
                back_content.append(f"{i}. {point}")
            back_content.append("")
        
        back_content.append("<b>Answers:</b>")
        for i, flashcard in enumerate(book_data['flashcards'], 1):
            back_content.append(f"Q{i}: {flashcard['answer']}")
        
        # Join with <br> for Anki HTML rendering
        back_text = "<br>".join(back_content)
        
        # Create front content
        front_content = []
        front_content.append(f"<b>{book_data['book_title']}</b>")
        front_content.append(f"by {book_data['author']}")
        front_content.append("")
        front_content.append("<b>Questions:</b>")
        for i, flashcard in enumerate(book_data['flashcards'], 1):
            front_content.append(f"Q{i}: {flashcard['question']}")
        
        # Join with <br> for Anki HTML rendering
        front_text = "<br>".join(front_content)
        
        # Create the flashcard
        console.print("[yellow]Creating Anki flashcard...[/yellow]")
        if self.create_flashcard(deck_name, front_text, back_text):
            console.print(f"[green]✓ Flashcard created successfully in deck '{deck_name}'[/green]")
            return True
        else:
            console.print("[red]✗ Failed to create flashcard[/red]")
            return False
    
    def run(self) -> None:
        """Main execution method."""
        try:
            console.print(Panel.fit(
                "[bold blue]Anki Flashcard Creator[/bold blue]\n"
                "Create Anki flashcards from your Kindle highlights",
                border_style="blue"
            ))
            
            # Find markdown files
            console.print("[bold blue]Step 1: Finding markdown files...[/bold blue]")
            md_files = self.find_markdown_files()
            self.display_available_files(md_files)
            
            if not md_files:
                console.print("[red]No markdown files found. Please run the Kindle highlights extractor first.[/red]")
                return
            
            # Select file
            console.print("[bold blue]Step 2: Select a file[/bold blue]")
            selected_file = self.select_file(md_files)
            if not selected_file:
                return
            
            # Parse file
            console.print("[bold blue]Step 3: Parsing markdown file...[/bold blue]")
            book_data = self.parse_markdown_file(selected_file)
            if not book_data:
                console.print("[red]Failed to parse the markdown file[/red]")
                return
            
            # Display parsed data
            console.print(f"[green]✓ Parsed: {book_data['book_title']} by {book_data['author']}[/green]")
            console.print(f"[blue]Summary: {book_data['summary'][:100]}...[/blue]")
            console.print(f"[blue]Key points: {len(book_data['key_points'])}[/blue]")
            console.print(f"[blue]Flashcards: {len(book_data['flashcards'])}[/blue]")
            
            # Test AnkiConnect
            console.print("[bold blue]Step 4: Testing AnkiConnect...[/bold blue]")
            if not self.test_anki_connect():
                console.print("[red]AnkiConnect is not available. Please make sure Anki is running.[/red]")
                return
            
            # Confirm creation
            if not Confirm.ask(f"\nCreate Anki flashcard for '{book_data['book_title']}'?"):
                console.print("[yellow]Flashcard creation cancelled[/yellow]")
                return
            
            # Create flashcards
            console.print("[bold blue]Step 5: Creating Anki flashcard...[/bold blue]")
            if self.create_flashcards_from_book(book_data):
                console.print("\n[bold green]🎉 Anki flashcard created successfully![/bold green]")
                console.print("[green]Open Anki to review your new flashcard.[/green]")
            else:
                console.print("\n[bold red]❌ Failed to create Anki flashcard[/bold red]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Process interrupted by user.[/yellow]")
        except Exception as e:
            console.print(f"[red]✗ Unexpected error: {e}[/red]")


def main():
    """Main entry point."""
    creator = AnkiFlashcardCreator()
    creator.run()


if __name__ == "__main__":
    main() 