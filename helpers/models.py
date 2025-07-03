from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

@dataclass
class Book:
    id: str
    title: str
    author: str
    asin: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    last_annotated_date: Optional[datetime] = None

@dataclass
class Highlight:
    id: str
    text: str
    location: Optional[str] = None
    page: Optional[str] = None
    note: Optional[str] = None
    color: Optional[str] = None  # 'pink' | 'blue' | 'yellow' | 'orange'
    created_date: Optional[datetime] = None

@dataclass
class BookHighlight:
    book: Book
    highlights: List[Highlight]
    metadata: Optional['BookMetadata'] = None

@dataclass
class BookMetadata:
    isbn: Optional[str] = None
    pages: Optional[str] = None
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    author_url: Optional[str] = None

@dataclass
class KindleFrontmatter:
    book_id: str
    title: str
    author: str
    asin: str
    last_annotated_date: Optional[str] = None
    book_image_url: str = ''
    highlights_count: int = 0

@dataclass
class KindleFile:
    file: str  # Path to file or file identifier
    frontmatter: KindleFrontmatter
    book: Optional[Book] = None

# Amazon region types
AMAZON_REGIONS = [
    'global', 'india', 'japan', 'spain', 'germany', 'italy', 'UK', 'france'
]

@dataclass
class AmazonAccount:
    name: str
    hostname: str
    kindle_reader_url: str
    notebook_url: str 