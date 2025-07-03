import os
from typing import Optional, List
from helpers.models import Book, Highlight

def save_comprehensive_markdown(book: Book, highlights: List[Highlight], summary_data: Optional[dict], save_dir: str) -> None:
    """Save everything to a comprehensive markdown file."""
    import re
    try:
        # Create filename
        safe_title = re.sub(r'[^\w\s-]', '', book.title).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = f"{safe_title}-complete.md"
        filepath = os.path.join(save_dir, filename)
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
        print(f"[green]✓ Comprehensive markdown saved to: {filepath}[/green]")
    except Exception as e:
        print(f"[red]✗ Error saving comprehensive markdown: {e}[/red]") 