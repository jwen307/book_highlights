#!/usr/bin/env python3
"""
Kindle Highlights Extractor

A Python script to extract highlights from Amazon's Kindle notebook.
"""

# Standard library imports
import time
import json
import os
import platform
import re
from typing import Optional, Dict, List
from datetime import datetime

# Third-party imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

# Local imports
from models import Book, Highlight
from config import DEFAULT_SAVE_LOCATION, ensure_save_directory


# Constants
AMAZON_NOTEBOOK_URL = "https://read.amazon.com/notebook"
LOGIN_TIMEOUT = 120  # seconds
LOGIN_POLL_INTERVAL = 2  # seconds
WEBDRIVER_WAIT_TIMEOUT = 30  # seconds
PAGE_LOAD_DELAY = 3  # seconds

# CSS Selectors
BOOK_SELECTOR = ".kp-notebook-library-each-book"
BOOK_TITLE_SELECTOR = "h2.kp-notebook-searchable"
BOOK_AUTHOR_SELECTOR = "p.kp-notebook-searchable"
BOOK_COVER_SELECTOR = ".kp-notebook-cover-image"
BOOK_DATE_SELECTOR = "[id^='kp-notebook-annotated-date']"
HIGHLIGHT_SELECTOR = ".a-row.a-spacing-base"
HIGHLIGHT_TEXT_SELECTOR = "#highlight"
HIGHLIGHT_COLOR_SELECTOR = ".kp-notebook-highlight"
HIGHLIGHT_LOCATION_SELECTOR = "#kp-annotation-location"
HIGHLIGHT_HEADER_SELECTOR = "#annotationNoteHeader"
HIGHLIGHT_NOTE_SELECTOR = "#note"
NEXT_PAGE_STATE_SELECTOR = ".kp-notebook-content-limit-state"
NEXT_PAGE_TOKEN_SELECTOR = ".kp-notebook-annotations-next-page-start"

# Chrome options
CHROME_OPTIONS = {
    "detach": True,
    "excludeSwitches": ["enable-automation"],
    "useAutomationExtension": False
}

# macOS Chrome path
MACOS_CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


console = Console()


class KindleHighlightsExtractor:
    """Main class for extracting Kindle highlights from Amazon's notebook."""
    
    def __init__(self):
        """Initialize the Kindle Highlights Extractor."""
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.is_logged_in = False
        
    def setup_driver(self) -> None:
        """Set up the Chrome WebDriver with appropriate options."""
        console.print("[bold blue]Setting up Chrome WebDriver...[/bold blue]")
        
        chrome_options = self._create_chrome_options()
        self._setup_macos_chrome_path(chrome_options)
        self._initialize_driver(chrome_options)
        self._configure_driver()
        
        console.print("[green]✓ WebDriver setup complete[/green]")
    
    def _create_chrome_options(self) -> Options:
        """Create Chrome options with automation detection prevention."""
        chrome_options = Options()
        for option, value in CHROME_OPTIONS.items():
            chrome_options.add_experimental_option(option, value)
        return chrome_options
    
    def _setup_macos_chrome_path(self, chrome_options: Options) -> None:
        """Set up Chrome binary path for macOS if available."""
        if platform.system() == "Darwin" and os.path.exists(MACOS_CHROME_PATH):
            chrome_options.binary_location = MACOS_CHROME_PATH
            console.print("[blue]Using macOS Chrome binary[/blue]")
    
    def _initialize_driver(self, chrome_options: Options) -> None:
        """Initialize the Chrome driver with fallback options."""
        try:
            # Try to use webdriver-manager first
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            console.print(f"[yellow]WebDriver manager failed: {e}[/yellow]")
            console.print("[yellow]Trying to use system ChromeDriver...[/yellow]")
            
            try:
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e2:
                console.print(f"[red]System ChromeDriver also failed: {e2}[/red]")
                console.print("[red]Please ensure Chrome is installed and ChromeDriver is available in PATH[/red]")
                raise
    
    def _configure_driver(self) -> None:
        """Configure the driver with additional settings."""
        # Remove webdriver property to avoid detection
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set up wait object
        self.wait = WebDriverWait(self.driver, WEBDRIVER_WAIT_TIMEOUT)
    
    def launch_amazon_notebook(self) -> None:
        """Launch the Amazon notebook website."""
        console.print("[bold blue]Launching Amazon Notebook...[/bold blue]")
        
        try:
            self.driver.get(AMAZON_NOTEBOOK_URL)
            console.print("[green]✓ Amazon Notebook page loaded[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to load Amazon Notebook: {e}[/red]")
            raise
    
    def wait_for_login(self) -> bool:
        """Automatically wait for login by checking the URL, no user input required."""
        self._show_login_instructions()
        return self._poll_for_login()
    
    def _show_login_instructions(self) -> None:
        """Display login instructions to the user."""
        console.print("\n[bold yellow]Please log in to your Amazon account manually.[/bold yellow]")
        console.print("[yellow]The browser window will remain open for you to complete the login process.[/yellow]")

        instructions = Text()
        instructions.append("1. Complete the login process in the browser window\n", style="cyan")
        instructions.append("2. You will be automatically detected as logged in when the page is ready\n", style="cyan")
        instructions.append(f"3. Make sure you are on {AMAZON_NOTEBOOK_URL}\n", style="cyan")
        console.print(Panel(instructions, title="Login Instructions", border_style="blue"))
    
    def _poll_for_login(self) -> bool:
        """Poll for login completion by checking URL changes."""
        waited = 0

        while waited < LOGIN_TIMEOUT:
            try:
                current_url = self.driver.current_url
                if self._is_on_notebook_page(current_url):
                    console.print("[green]✓ On notebook page, assuming login successful[/green]")
                    self.is_logged_in = True
                    return True
                time.sleep(LOGIN_POLL_INTERVAL)
                waited += LOGIN_POLL_INTERVAL
            except Exception as e:
                console.print(f"[yellow]Waiting for login... ({e})[/yellow]")
                time.sleep(LOGIN_POLL_INTERVAL)
                waited += LOGIN_POLL_INTERVAL

        console.print("[red]✗ Timed out waiting for login. Please try again.[/red]")
        return False
    
    def _is_on_notebook_page(self, url: str) -> bool:
        """Check if the current URL indicates we're on the notebook page."""
        return "read.amazon.com/notebook" in url
    
    def get_available_books(self) -> List["Book"]:
        """Get list of available books from the notebook page."""
        if not self.is_logged_in:
            console.print("[red]✗ Not logged in. Please complete login first.[/red]")
            return []
        
        console.print("[bold blue]Scanning for available books...[/bold blue]")
        
        try:
            time.sleep(2)
            book_elements = self.driver.find_elements(By.CSS_SELECTOR, BOOK_SELECTOR)
            
            if not book_elements:
                console.print("[yellow]⚠ No books found with TypeScript selector[/yellow]")
                return []
            
            books = [self._extract_book_data(element, i) for i, element in enumerate(book_elements)]
            books = [book for book in books if book is not None]  # Filter out None values
            
            console.print(f"[green]✓ Successfully extracted {len(books)} books[/green]")
            return books
            
        except Exception as e:
            console.print(f"[red]✗ Error getting books: {e}[/red]")
            return []
    
    def _extract_book_data(self, book_element, index: int) -> Optional["Book"]:
        """Extract book data from a book element."""
        try:
            title = self._extract_book_title(book_element)
            author = self._extract_book_author(book_element)
            asin = book_element.get_attribute("id")
            url = f"https://www.amazon.com/dp/{asin}" if asin else None
            image_url = self._extract_book_image(book_element)
            last_annotated_date = self._extract_book_date(book_element)
            
            return Book(
                id=asin or f"book_{index}",
                title=title,
                author=author,
                asin=asin,
                url=url,
                image_url=image_url,
                last_annotated_date=last_annotated_date
            )
        except Exception as e:
            console.print(f"[yellow]⚠ Error extracting book {index}: {e}[/yellow]")
            return None
    
    def _extract_book_title(self, book_element) -> str:
        """Extract book title from element."""
        try:
            title_element = book_element.find_element(By.CSS_SELECTOR, BOOK_TITLE_SELECTOR)
            return title_element.text.strip()
        except:
            return "Unknown Book"
    
    def _extract_book_author(self, book_element) -> str:
        """Extract book author from element."""
        try:
            author_element = book_element.find_element(By.CSS_SELECTOR, BOOK_AUTHOR_SELECTOR)
            return author_element.text.strip().replace("Author: ", "").strip()
        except:
            return "Unknown Author"
    
    def _extract_book_image(self, book_element) -> Optional[str]:
        """Extract book image URL from element."""
        try:
            img_element = book_element.find_element(By.CSS_SELECTOR, BOOK_COVER_SELECTOR)
            return img_element.get_attribute("src")
        except:
            return None
    
    def _extract_book_date(self, book_element) -> Optional[datetime]:
        """Extract book last annotated date from element."""
        try:
            date_element = book_element.find_element(By.CSS_SELECTOR, BOOK_DATE_SELECTOR)
            date_val = date_element.get_attribute("value")
            # Try to parse date (format: 'Sunday October 24, 2021')
            date_match = re.search(r"(\w+ \w+ \d{1,2}, \d{4})", date_val or "")
            if date_match:
                return datetime.strptime(date_match.group(1), "%B %d, %Y")
        except:
            pass
        return None
    
    def display_books(self, books: List[Book]) -> None:
        """Display available books to the user."""
        if not books:
            console.print("[red]No books found.[/red]")
            return

        console.print(f"\n[bold green]Found {len(books)} books:[/bold green]")
        for idx, book in enumerate(books):
            asin_info = f" (ASIN: {book.asin})" if book.asin else ""
            console.print(f"[cyan]{idx + 1}.[/cyan] [bold]{book.title}[/bold] by [italic]{book.author}[/italic]{asin_info}")
    
    def debug_page_structure(self, filename: str = "page_debug.html") -> None:
        """Save the current page structure for debugging purposes."""
        try:
            page_source = self.driver.page_source
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(page_source)
            console.print(f"[green]✓ Page source saved to {filename}[/green]")
            
            # Also save a simplified version with just the body content
            try:
                body_element = self.driver.find_element(By.TAG_NAME, "body")
                body_text = body_element.text
                with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
                    f.write(body_text)
                console.print(f"[green]✓ Page text saved to {filename}.txt[/green]")
            except:
                pass
                
        except Exception as e:
            console.print(f"[red]✗ Error saving page structure: {e}[/red]")

    def highlights_url(self, book, state=None):
        # TypeScript: `${region.notebookUrl}?asin=${book.asin}&contentLimitState=${state?.contentLimitState ?? ''}&token=${state?.token ?? ''}`
        # We'll use US/global for now
        base_url = "https://read.amazon.com/notebook"
        content_limit_state = state.get('contentLimitState', '') if state else ''
        token = state.get('token', '') if state else ''
        url = f"{base_url}?asin={book.asin}&contentLimitState={content_limit_state}&token={token}"
        print(url)
        return url

    def parse_next_page_state(self):
        """Parse the next page state from the current page."""
        try:
            content_limit_state_elem = self.driver.find_element(By.CSS_SELECTOR, NEXT_PAGE_STATE_SELECTOR)
            token_elem = self.driver.find_element(By.CSS_SELECTOR, NEXT_PAGE_TOKEN_SELECTOR)
            content_limit_state = content_limit_state_elem.get_attribute("value") if content_limit_state_elem else ""
            token = token_elem.get_attribute("value") if token_elem else ""
            if token:
                return {"contentLimitState": content_limit_state, "token": token}
            else:
                return None
        except Exception:
            return None

    def map_text_to_color(self, highlight_classes: str):
        # TypeScript: /kp-notebook-highlight-(.*)/
        match = re.search(r'kp-notebook-highlight-(\w+)', highlight_classes or "")
        return match.group(1) if match else None

    def br2ln(self, html: str):
        if not html:
            return None
        # Replace <br>, <br/>, <br /> with newlines, then strip tags
        html = re.sub(r'<br\s*/?>', '\n', html)
        html = re.sub(r'<[^>]+>', '', html)
        return html.strip()
    
    def extract_highlights_from_book(self, book: "Book") -> List["Highlight"]:
        """Extract highlights from a specific book."""
        if not self._validate_extraction_prerequisites(book):
            return []

        console.print(f"[bold blue]Extracting highlights from '{book.title}'...[/bold blue]")

        highlights: List[Highlight] = []
        url = self.highlights_url(book)
        page_count = 0

        while True:
            page_count += 1
            console.print(f"[blue]Processing page {page_count}...[/blue]")
            
            page_highlights = self._extract_highlights_from_page(url, book, page_count)
            if page_highlights is None:  # Error occurred
                break
                
            highlights.extend(page_highlights)
            
            # Check for next page
            next_page_state = self.parse_next_page_state()
            if next_page_state:
                url = self.highlights_url(book, next_page_state)
            else:
                break

        console.print(f"[green]✓ Successfully extracted {len(highlights)} highlights from '{book.title}'[/green]")
        return [h for h in highlights if h.text]  # Only return highlights with text
    
    def _validate_extraction_prerequisites(self, book: "Book") -> bool:
        """Validate prerequisites for highlight extraction."""
        if not self.is_logged_in:
            console.print("[red]✗ Not logged in. Please complete login first.[/red]")
            return False

        if not book.asin:
            console.print("[red]✗ Book has no ASIN - cannot extract highlights[/red]")
            return False
            
        return True
    
    def _extract_highlights_from_page(self, url: str, book: "Book", page_count: int) -> Optional[List["Highlight"]]:
        """Extract highlights from a single page."""
        try:
            self.driver.get(url)
            time.sleep(PAGE_LOAD_DELAY)

            highlight_elements = self.driver.find_elements(By.CSS_SELECTOR, HIGHLIGHT_SELECTOR)
            
            if not highlight_elements:
                console.print("[yellow]No highlights found on this page[/yellow]")
                if page_count == 1:
                    self.debug_page_structure(f"debug_{book.asin}.html")
                return []

            return [self._extract_highlight_data(element, i, book, page_count) 
                   for i, element in enumerate(highlight_elements)]
                   
        except Exception as e:
            console.print(f"[red]Error finding highlight elements: {e}[/red]")
            return None
    
    def _extract_highlight_data(self, highlight_element, index: int, book: "Book", page_count: int) -> Optional["Highlight"]:
        """Extract highlight data from a highlight element."""
        try:
            text = self._extract_highlight_text(highlight_element)
            if not text:
                return None

            color = self._extract_highlight_color(highlight_element)
            location = self._extract_highlight_location(highlight_element)
            page = self._extract_highlight_page(highlight_element)
            note = self._extract_highlight_note(highlight_element)

            highlight = Highlight(
                id=f"{book.asin}_{index}_{page_count}_{hash(text)}",
                text=text,
                location=location,
                page=page,
                note=note,
                color=color,
                created_date=None  # Kindle web does not expose this
            )
            
            console.print(f"[green]✓ Extracted highlight: {text[:50]}...[/green]")
            return highlight
            
        except Exception as e:
            console.print(f"[yellow]⚠ Error extracting highlight {index+1}: {e}[/yellow]")
            return None
    
    def _extract_highlight_text(self, highlight_element) -> str:
        """Extract highlight text from element."""
        try:
            text_elem = highlight_element.find_element(By.CSS_SELECTOR, HIGHLIGHT_TEXT_SELECTOR)
            return text_elem.text.strip()
        except Exception:
            return highlight_element.text.strip()
    
    def _extract_highlight_color(self, highlight_element) -> Optional[str]:
        """Extract highlight color from element."""
        try:
            highlight_classes = highlight_element.find_element(By.CSS_SELECTOR, HIGHLIGHT_COLOR_SELECTOR).get_attribute("class")
            return self.map_text_to_color(highlight_classes)
        except Exception:
            return None
    
    def _extract_highlight_location(self, highlight_element) -> Optional[str]:
        """Extract highlight location from element."""
        try:
            location_elem = highlight_element.find_element(By.CSS_SELECTOR, HIGHLIGHT_LOCATION_SELECTOR)
            return location_elem.get_attribute("value")
        except Exception:
            return None
    
    def _extract_highlight_page(self, highlight_element) -> Optional[str]:
        """Extract highlight page number from element."""
        try:
            header_elem = highlight_element.find_element(By.CSS_SELECTOR, HIGHLIGHT_HEADER_SELECTOR)
            header_text = header_elem.text
            page_match = re.search(r'\d+$', header_text)
            return page_match.group(0) if page_match else None
        except Exception:
            return None
    
    def _extract_highlight_note(self, highlight_element) -> Optional[str]:
        """Extract highlight note from element."""
        try:
            note_elem = highlight_element.find_element(By.CSS_SELECTOR, HIGHLIGHT_NOTE_SELECTOR)
            note_html = note_elem.get_attribute("innerHTML")
            return self.br2ln(note_html)
        except Exception:
            return None
    
    def save_highlights_to_markdown(self, highlights: List["Highlight"], book: "Book" = None, filename: str = None) -> None:
        """Save highlights to a Markdown file."""
        if not highlights:
            console.print("[yellow]No highlights to save[/yellow]")
            return
        
        filepath = self._prepare_save_path(book, filename, ".md")
        self._write_markdown_file(filepath, highlights, book)
    
    def _prepare_save_path(self, book: "Book", filename: str, extension: str) -> str:
        """Prepare the full file path for saving."""
        save_dir = ensure_save_directory()
        
        if not filename:
            if book and book.title:
                safe_title = self._sanitize_filename(book.title)
                filename = f"{safe_title}{extension}"
            else:
                filename = f"kindle_highlights{extension}"
        
        return os.path.join(save_dir, filename)
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize a title for use as a filename."""
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        return re.sub(r'[-\s]+', '-', safe_title)
    
    def _write_markdown_file(self, filepath: str, highlights: List["Highlight"], book: "Book" = None) -> None:
        """Write highlights to a markdown file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                self._write_markdown_header(f, book)
                self._write_markdown_highlights(f, highlights)
            
            console.print(f"[green]✓ Highlights saved to {filepath}[/green]")
            console.print(f"[blue]Total highlights: {len(highlights)}[/blue]")
            
        except Exception as e:
            console.print(f"[red]✗ Error saving highlights: {e}[/red]")
    
    def _write_markdown_header(self, file, book: "Book" = None) -> None:
        """Write the markdown file header."""
        if book:
            file.write(f"# {book.title}\n\n")
            if book.author:
                file.write(f"**Author:** {book.author}\n\n")
            if book.asin:
                file.write(f"**ASIN:** {book.asin}\n\n")
            file.write("---\n\n")
        else:
            file.write("# Kindle Highlights\n\n")
    
    def _write_markdown_highlights(self, file, highlights: List["Highlight"]) -> None:
        """Write highlights to the markdown file."""
        for i, highlight in enumerate(highlights, 1):
            file.write(f"## Highlight {i} \n\n")
            file.write(f"{highlight.text}\n")
            if highlight.note:
                file.write(f"**Note:** {highlight.note}\n")
            
            file.write("---\n\n")
    
    def save_highlights_to_json(self, highlights: List["Highlight"], book: "Book" = None, filename: str = None) -> None:
        """Save highlights to a JSON file."""
        if not highlights:
            console.print("[yellow]No highlights to save[/yellow]")
            return
        
        filepath = self._prepare_save_path(book, filename, ".json")
        self._write_json_file(filepath, highlights)
    
    def _write_json_file(self, filepath: str, highlights: List["Highlight"]) -> None:
        """Write highlights to a JSON file."""
        try:
            highlights_dict = self._convert_highlights_to_dict(highlights)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(highlights_dict, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✓ Highlights saved to {filepath}[/green]")
            console.print(f"[blue]Total highlights: {len(highlights)}[/blue]")
            
        except Exception as e:
            console.print(f"[red]✗ Error saving highlights: {e}[/red]")
    
    def _convert_highlights_to_dict(self, highlights: List["Highlight"]) -> List[Dict]:
        """Convert Highlight dataclass objects to dictionaries for JSON serialization."""
        highlights_dict = []
        for highlight in highlights:
            highlight_dict = {
                'id': highlight.id,
                'text': highlight.text,
                'location': highlight.location,
                'page': highlight.page,
                'note': highlight.note,
                'color': highlight.color,
                'created_date': highlight.created_date.isoformat() if highlight.created_date else None
            }
            highlights_dict.append(highlight_dict)
        return highlights_dict
    
    # Select the book to extract highlights from using the input
    def select_book_interactive(self, books: List["Book"]) -> "Book":
        """Allow user to select a book interactively."""
        if not books:
            console.print("[red]No books available for selection[/red]")
            return None
        
        console.print("\n[bold blue]Select a book to extract highlights from:[/bold blue]")
        
        for i, book in enumerate(books):
            asin_info = f" (ASIN: {book.asin})" if book.asin else ""
            console.print(f"[cyan]{i + 1}.[/cyan] [bold]{book.title}[/bold] by [italic]{book.author}[/italic]{asin_info}")
        
        while True:
            try:
                choice = input(f"\nEnter book number (1-{len(books)}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(books):
                    selected_book = books[choice_num - 1]
                    console.print(f"[green]✓ Selected: {selected_book.title}[/green]")
                    return selected_book
                else:
                    console.print(f"[red]Please enter a number between 1 and {len(books)}[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Selection cancelled[/yellow]")
                return None
    
    def run(self) -> None:
        """Main execution method."""
        try:
            self._show_welcome_message()
            self._setup_and_launch()
            
            if self._handle_login():
                self._process_books()
            else:
                console.print("[red]✗ Login verification failed. Please try again.[/red]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Process interrupted by user.[/yellow]")
        except Exception as e:
            console.print(f"[red]✗ Unexpected error: {e}[/red]")
        finally:
            self._cleanup()
    
    def _show_welcome_message(self) -> None:
        """Display the welcome message."""
        console.print(Panel.fit(
            "[bold blue]Kindle Highlights Extractor[/bold blue]\n"
            "Extract your Kindle highlights from Amazon's notebook",
            border_style="blue"
        ))
    
    def _setup_and_launch(self) -> None:
        """Set up the driver and launch the notebook page."""
        self.setup_driver()
        self.launch_amazon_notebook()
        time.sleep(2)
    
    def _handle_login(self) -> bool:
        """Handle the login process."""
        if self.wait_for_login():
            console.print("[green]✓ Login process completed successfully![/green]")
            return True
        return False
    
    def _process_books(self) -> None:
        """Process the available books."""
        books = self.get_available_books()
        self.display_books(books)
        
        if not books:
            console.print("\n[yellow]No books found. You may need to refresh the page or check your account.[/yellow]")
            return
        
        selected_book = self.select_book_interactive(books)
        if not selected_book:
            console.print("[yellow]No book selected. Exiting.[/yellow]")
            return
        
        self._extract_and_save_highlights(selected_book)
    
    def _extract_and_save_highlights(self, selected_book: "Book") -> None:
        """Extract and save highlights for the selected book."""
        highlights = self.extract_highlights_from_book(selected_book)
        
        if highlights:
            self.save_highlights_to_markdown(highlights, selected_book)
            self._show_extraction_summary(selected_book, highlights)
        else:
            self._handle_no_highlights(selected_book)
    
    def _show_extraction_summary(self, book: "Book", highlights: List["Highlight"]) -> None:
        """Show the extraction summary."""
        console.print(f"\n[bold green]Extraction Complete![/bold green]")
        console.print(f"[blue]Book: {book.title}[/blue]")
        console.print(f"[blue]Author: {book.author}[/blue]")
        console.print(f"[blue]Highlights extracted: {len(highlights)}[/blue]")
    
    def _handle_no_highlights(self, book: "Book") -> None:
        """Handle the case when no highlights are found."""
        console.print("[yellow]No highlights found for the selected book.[/yellow]")
        console.print("[yellow]Check the debug files (debug_*.html) for page structure analysis.[/yellow]")
        
        try:
            save_debug = input("\nSave page structure for debugging? (y/n): ").strip().lower()
            if save_debug == 'y':
                self.debug_page_structure(f"manual_debug_{book.asin}.html")
                console.print("[green]✓ Page structure saved for manual inspection[/green]")
        except:
            pass
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
                console.print("[green]✓ Browser closed successfully[/green]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not close browser cleanly: {e}[/yellow]")


def main():
    """Main entry point."""
    extractor = KindleHighlightsExtractor()
    extractor.run()


if __name__ == "__main__":
    main() 