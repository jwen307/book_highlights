#!/usr/bin/env python3
"""
Test script to compare URL construction with the Obsidian Kindle plugin
"""

from kindle_highlights import KindleHighlightsExtractor
import time

def test_url_construction():
    """Test the URL construction logic from the TypeScript plugin"""
    
    # Amazon regions from the TypeScript plugin
    amazon_regions = {
        'global': {
            'name': 'Global',
            'hostname': 'amazon.com',
            'kindle_reader_url': 'https://read.amazon.com',
            'notebook_url': 'https://read.amazon.com/notebook',
        },
        'UK': {
            'name': 'UK',
            'hostname': 'amazon.co.uk',
            'kindle_reader_url': 'https://read.amazon.co.uk',
            'notebook_url': 'https://read.amazon.co.uk/notebook',
        }
    }
    
    def highlights_url(book, region='global', state=None):
        """Replicate the TypeScript highlightsUrl function"""
        base_url = amazon_regions[region]['notebook_url']
        url = f"{base_url}?asin={book.asin}"
        if state:
            url += f"&contentLimitState={state.get('contentLimitState', '')}&token={state.get('token', '')}"
        return url
    
    print("=== Kindle URL Construction Test ===\n")
    
    # Initialize extractor
    extractor = KindleHighlightsExtractor()
    extractor.setup_driver()
    extractor.launch_amazon_notebook()
    
    print("Please log in to your Amazon account in the opened browser window.")
    print("After login, your Kindle books should appear.\n")
    
    # Wait for login
    success = extractor.wait_for_login()
    if not success:
        print("[FAILURE] Login failed")
        extractor.driver.quit()
        return
    
    print("[SUCCESS] Login successful!\n")
    
    # Get books
    books = extractor.get_available_books()
    if not books:
        print("[FAILURE] No books found")
        extractor.driver.quit()
        return
    
    # Display books
    extractor.display_books(books)
    
    # Test URL construction for first book
    first_book = books[0]
    print(f"\n=== URL Construction for '{first_book.title}' ===")
    print(f"Book ASIN: {first_book.asin}")
    print(f"Book ID: {first_book.id}")
    
    # Test our Python implementation
    print(f"\n--- Our Python Implementation ---")
    python_url = extractor.highlights_url(first_book)
    print(f"Python URL: {python_url}")
    
    # Test TypeScript-style implementation
    print(f"\n--- TypeScript-Style Implementation ---")
    ts_url = highlights_url(first_book, 'global')
    print(f"TypeScript URL: {ts_url}")
    
    # Test with different regions
    print(f"\n--- Different Regions ---")
    for region in ['global', 'UK']:
        region_url = highlights_url(first_book, region)
        print(f"{region.upper()} URL: {region_url}")
    
    # Test with pagination state (empty)
    print(f"\n--- With Pagination State (empty) ---")
    empty_state = {'contentLimitState': '', 'token': ''}
    pagination_url = highlights_url(first_book, 'global', empty_state)
    print(f"Pagination URL: {pagination_url}")
    
    # Test with sample pagination state
    print(f"\n--- With Sample Pagination State ---")
    sample_state = {'contentLimitState': 'abc123', 'token': 'xyz789'}
    sample_pagination_url = highlights_url(first_book, 'global', sample_state)
    print(f"Sample Pagination URL: {sample_pagination_url}")
    
    # Compare URLs
    print(f"\n=== URL Comparison ===")
    print(f"Python URL == TypeScript URL: {python_url == ts_url}")
    
    if python_url != ts_url:
        print(f"\n[DIFFERENCE DETECTED]")
        print(f"Python:  {python_url}")
        print(f"TypeScript: {ts_url}")
        
        # Analyze differences
        if "contentLimitState" in python_url and "contentLimitState" not in ts_url:
            print("Python includes contentLimitState, TypeScript doesn't")
        if "token" in python_url and "token" not in ts_url:
            print("Python includes token, TypeScript doesn't")
    
    print(f"\n=== Test Complete ===")
    extractor.driver.quit()

if __name__ == "__main__":
    test_url_construction() 