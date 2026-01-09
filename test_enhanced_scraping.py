"""Test enhanced Selenium and Playwright implementations"""
import time
from LetterboxdNew import FilmScraper

def test_playwright():
    """Test Playwright with optimizations"""
    print("\n" + "="*60)
    print("TESTING PLAYWRIGHT WITH OPTIMIZATIONS")
    print("="*60)
    
    scraper = FilmScraper(use_selenium=False, use_playwright=True, debug=True)
    
    # Test URL
    test_url = "https://letterboxd.com/film/the-shawshank-redemption/"
    
    print(f"\nFetching: {test_url}")
    start = time.time()
    
    try:
        html = scraper.get_page_content(test_url)
        elapsed = time.time() - start
        
        if html:
            print(f"\n✓ Success! Retrieved {len(html)} bytes in {elapsed:.2f}s")
            
            # Check for key content
            checks = {
                "Title element": "filmtitle" in html or "headline-1" in html,
                "Average rating": "average-rating" in html or "data-average-rating" in html,
                "Film poster": "film-poster" in html,
                "Director": "directedby" in html or "metadata" in html
            }
            
            print("\nContent verification:")
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}: {result}")
        else:
            print(f"\n✗ Failed to retrieve content (took {elapsed:.2f}s)")
    
    finally:
        scraper.cleanup()
        print("\n✓ Playwright test completed and cleaned up")

def test_selenium():
    """Test Selenium with optimizations"""
    print("\n" + "="*60)
    print("TESTING SELENIUM WITH OPTIMIZATIONS")
    print("="*60)
    
    scraper = FilmScraper(use_selenium=True, use_playwright=False, browser='chrome', debug=True)
    
    # Test URL
    test_url = "https://letterboxd.com/film/pulp-fiction/"
    
    print(f"\nFetching: {test_url}")
    start = time.time()
    
    try:
        html = scraper.get_page_content(test_url)
        elapsed = time.time() - start
        
        if html:
            print(f"\n✓ Success! Retrieved {len(html)} bytes in {elapsed:.2f}s")
            
            # Check for key content
            checks = {
                "Title element": "filmtitle" in html or "headline-1" in html,
                "Average rating": "average-rating" in html or "data-average-rating" in html,
                "Film poster": "film-poster" in html,
                "Director": "directedby" in html or "metadata" in html
            }
            
            print("\nContent verification:")
            for check, result in checks.items():
                status = "✓" if result else "✗"
                print(f"  {status} {check}: {result}")
        else:
            print(f"\n✗ Failed to retrieve content (took {elapsed:.2f}s)")
    
    finally:
        scraper.cleanup()
        print("\n✓ Selenium test completed and cleaned up")

def test_both_comparison():
    """Compare Playwright vs Selenium performance"""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON: PLAYWRIGHT VS SELENIUM")
    print("="*60)
    
    test_urls = [
        "https://letterboxd.com/film/the-godfather/",
        "https://letterboxd.com/film/inception/",
        "https://letterboxd.com/film/the-dark-knight/"
    ]
    
    # Test Playwright
    print("\n--- Testing with Playwright ---")
    scraper_pw = FilmScraper(use_selenium=False, use_playwright=True, debug=False)
    pw_times = []
    
    try:
        for url in test_urls:
            start = time.time()
            html = scraper_pw.get_page_content(url)
            elapsed = time.time() - start
            pw_times.append(elapsed)
            status = "✓" if html else "✗"
            print(f"{status} {url.split('/')[-2]}: {elapsed:.2f}s ({len(html) if html else 0} bytes)")
    finally:
        scraper_pw.cleanup()
    
    # Test Selenium
    print("\n--- Testing with Selenium ---")
    scraper_se = FilmScraper(use_selenium=True, use_playwright=False, browser='chrome', debug=False)
    se_times = []
    
    try:
        for url in test_urls:
            start = time.time()
            html = scraper_se.get_page_content(url)
            elapsed = time.time() - start
            se_times.append(elapsed)
            status = "✓" if html else "✗"
            print(f"{status} {url.split('/')[-2]}: {elapsed:.2f}s ({len(html) if html else 0} bytes)")
    finally:
        scraper_se.cleanup()
    
    # Summary
    print("\n--- Performance Summary ---")
    avg_pw = sum(pw_times) / len(pw_times) if pw_times else 0
    avg_se = sum(se_times) / len(se_times) if se_times else 0
    
    print(f"Playwright average: {avg_pw:.2f}s")
    print(f"Selenium average:   {avg_se:.2f}s")
    
    if avg_pw and avg_se:
        speedup = avg_se / avg_pw
        print(f"\nPlaywright is {speedup:.1f}x faster" if speedup > 1 else f"Selenium is {1/speedup:.1f}x faster")

def test_full_scraping():
    """Test full film scraping with enhanced scraper"""
    print("\n" + "="*60)
    print("TESTING FULL FILM SCRAPING")
    print("="*60)
    
    scraper = FilmScraper(use_selenium=True, use_playwright=True, browser='chrome', debug=True)
    
    test_url = "https://letterboxd.com/film/parasite-2019/"
    
    print(f"\nScraping full details: {test_url}")
    start = time.time()
    
    try:
        film_data = scraper.scrape_film_details(test_url)
        elapsed = time.time() - start
        
        print(f"\n✓ Scraping completed in {elapsed:.2f}s")
        print("\nExtracted data:")
        print(f"  Title: {film_data.get('title')}")
        print(f"  Release Date: {film_data.get('release_date')}")
        print(f"  Runtime: {film_data.get('runtime')}")
        print(f"  Genres: {film_data.get('genres')}")
        print(f"  Directors: {film_data.get('directors')}")
        print(f"  Average Rating: {film_data.get('average_rating')}")
        print(f"  Country: {film_data.get('country')}")
        print(f"  Status: {film_data.get('scrape_status')}")
        
    finally:
        scraper.cleanup()
        print("\n✓ Full scraping test completed and cleaned up")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ENHANCED SCRAPING TEST SUITE")
    print("="*60)
    print("\nThis will test both Playwright and Selenium with optimizations")
    print("Press Ctrl+C to cancel at any time\n")
    
    time.sleep(2)
    
    try:
        # Run tests
        test_playwright()
        time.sleep(1)
        
        test_selenium()
        time.sleep(1)
        
        test_both_comparison()
        time.sleep(1)
        
        test_full_scraping()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()
