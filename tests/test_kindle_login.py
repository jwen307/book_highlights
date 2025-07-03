from helpers.amazon_helper import KindleHighlightsExtractor
import time

if __name__ == "__main__":
    extractor = KindleHighlightsExtractor()
    extractor.setup_driver()
    extractor.launch_amazon_notebook()
    
    print("Please log in to your Amazon account in the opened browser window.")
    print("After login, your Kindle books should appear. You have 5 minutes.")
    
    # Wait for login (reuse the extractor's method)
    success = extractor.wait_for_login()
    if success:
        print("[SUCCESS] KindleHighlightsExtractor login test passed.")
        books = extractor.get_available_books()
        extractor.display_books(books)
        
        if books:
            # Extract highlights from the first book
            first_book = books[0]
            print(f"\nExtracting highlights from: {first_book.title}")
            highlights = extractor.extract_highlights_from_book(first_book)
            
            if highlights:
                print(f"[SUCCESS] Found {len(highlights)} highlights in '{first_book.title}'")
            else:
                print("[FAILURE] No highlights found in the first book")
        else:
            print("[FAILURE] No books found after login")
    else:
        print("[FAILURE] KindleHighlightsExtractor login test failed.")
    time.sleep(2)
    extractor.driver.quit() 
    