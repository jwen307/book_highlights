#!/usr/bin/env python3
"""
LLM Summarizer for Kindle Highlights

Uses OpenAI API to generate summaries and key points from Kindle highlights.
"""

import os
import json
from typing import List, Dict, Optional
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from models import Highlight, Book
from config import get_openai_api_key

console = Console()


class LLMSummarizer:
    """Handles LLM summarization of Kindle highlights."""
    
    def __init__(self):
        """Initialize the LLM summarizer."""
        self.client = self._initialize_openai_client()
    
    def _initialize_openai_client(self) -> Optional[OpenAI]:
        """Initialize the OpenAI client with API key."""
        api_key = get_openai_api_key()
        if not api_key:
            console.print("[red]✗ OpenAI API key not found. Please set it in your config.[/red]")
            return None
        
        try:
            return OpenAI(api_key=api_key)
        except Exception as e:
            console.print(f"[red]✗ Failed to initialize OpenAI client: {e}[/red]")
            return None
    
    def summarize_highlights(self, highlights: List[Highlight], book: Book) -> Optional[Dict]:
        """
        Generate a summary and key points from the highlights.
        
        Returns:
            Dict containing 'summary' and 'key_points' or None if failed
        """
        if not self.client:
            return None
        
        if not highlights:
            console.print("[yellow]No highlights to summarize[/yellow]")
            return None
        
        console.print(f"[bold blue]Generating summary for '{book.title}'...[/bold blue]")
        
        try:
            # Prepare the highlights text
            highlights_text = self._prepare_highlights_text(highlights)
            
            # Create the prompt
            prompt = self._create_summary_prompt(book, highlights_text)
            
            # Generate the summary
            response = self._generate_summary(prompt)
            
            if response:
                # Parse the response
                summary_data = self._parse_summary_response(response)
                if summary_data:
                    return summary_data
            
            return None
            
        except Exception as e:
            console.print(f"[red]✗ Error generating summary: {e}[/red]")
            return None
    
    def _prepare_highlights_text(self, highlights: List[Highlight]) -> str:
        """Prepare highlights text for the LLM prompt."""
        highlights_text = []
        for i, highlight in enumerate(highlights, 1):
            highlight_text = f"{i}. {highlight.text}"
            if highlight.note:
                highlight_text += f"\n   Note: {highlight.note}"
            highlights_text.append(highlight_text)
        
        return "\n\n".join(highlights_text)
    
    def _create_summary_prompt(self, book: Book, highlights_text: str) -> str:
        """Create the prompt for the LLM."""
        return f"""You are an expert book analyst and educator. Based on the following highlights from "{book.title}" by {book.author}, please provide:

1. A one-sentence summary of the main theme or message of the book
2. A list of key points that emerge from these highlights
3. A set of flashcard questions to test understanding of the key concepts

Format your response as follows:

SUMMARY: [Your one-sentence summary here]

KEY POINTS:
- [Key point 1]
- [Key point 2]
- [Key point 3]
- [Key point 4]
- [Key point 5]
- [Key point 6]
- [Key point 7]
- [Key point 8]
- etc.

FLASHCARDS:
Q: [Question 1]
A: [Answer 1]

Q: [Question 2]
A: [Answer 2]

Q: [Question 3]
A: [Answer 3]

Q: [Question 4]
A: [Answer 4]

Q: [Question 5]
A: [Answer 5]

Here are the highlights:

{highlights_text}

Please ensure your summary captures the essence of the book, your key points are insightful and well-organized, and your flashcards test important concepts from the book."""
    
    def _generate_summary(self, prompt: str) -> Optional[str]:
        """Generate summary using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model="o4-mini",
                messages=[
                    {"role": "system", "content": "You are an expert book analyst who provides concise, insightful summaries and key points."},
                    {"role": "user", "content": prompt}
                ],
                #max_completion_tokens=5000,
                #temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[red]✗ Error calling OpenAI API: {e}[/red]")
            return None
    
    def _parse_summary_response(self, response: str) -> Optional[Dict]:
        """Parse the LLM response into structured data."""
        try:
            lines = response.strip().split('\n')
            summary = ""
            key_points = []
            flashcards = []
            
            in_key_points = False
            in_flashcards = False
            current_question = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('SUMMARY:'):
                    summary = line.replace('SUMMARY:', '').strip()
                elif line.startswith('KEY POINTS:'):
                    in_key_points = True
                    in_flashcards = False
                elif line.startswith('FLASHCARDS:'):
                    in_key_points = False
                    in_flashcards = True
                elif in_key_points and line.startswith('-'):
                    key_point = line.replace('-', '').strip()
                    if key_point:
                        key_points.append(key_point)
                elif in_flashcards and line.startswith('Q:'):
                    current_question = line.replace('Q:', '').strip()
                elif in_flashcards and line.startswith('A:') and current_question:
                    answer = line.replace('A:', '').strip()
                    flashcards.append({
                        'question': current_question,
                        'answer': answer
                    })
                    current_question = None
            
            if summary and key_points:
                return {
                    'summary': summary,
                    'key_points': key_points,
                    'flashcards': flashcards
                }
            else:
                console.print("[yellow]⚠ Could not parse LLM response properly[/yellow]")
                return None
                
        except Exception as e:
            console.print(f"[red]✗ Error parsing LLM response: {e}[/red]")
            return None
    
    def _save_summary_to_file(self, summary_data: Dict, book: Book) -> None:
        """Save the summary to a markdown file."""
        try:
            from config import ensure_save_directory
            import re
            
            save_dir = ensure_save_directory()
            
            # Sanitize filename
            safe_title = re.sub(r'[^\w\s-]', '', book.title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            filename = f"{safe_title}-summary.md"
            
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Summary: {book.title}\n\n")
                f.write(f"**Author:** {book.author}\n\n")
                f.write("---\n\n")
                
                f.write("## One-Sentence Summary\n\n")
                f.write(f"{summary_data['summary']}\n\n")
                
                f.write("## Key Points\n\n")
                for point in summary_data['key_points']:
                    f.write(f"- {point}\n")
                f.write("\n")
                
                # Add flashcards if available
                if 'flashcards' in summary_data and summary_data['flashcards']:
                    f.write("## Flashcards\n\n")
                    for i, flashcard in enumerate(summary_data['flashcards'], 1):
                        f.write(f"**Q{i}:** {flashcard['question']}\n\n")
                        f.write(f"**A{i}:** {flashcard['answer']}\n\n")
                        f.write("---\n\n")
            
            console.print(f"[green]✓ Summary saved to {filepath}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Error saving summary: {e}[/red]")


def summarize_highlights(highlights: List[Highlight], book: Book) -> Optional[Dict]:
    """Convenience function to summarize highlights."""
    summarizer = LLMSummarizer()
    return summarizer.summarize_highlights(highlights, book) 