"""Test with Playwright to see rendered content"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

username = "rjbritton08"
url = f"https://letterboxd.com/{username}/films/"

print(f"Fetching with Playwright: {url}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, timeout=15000)
    
    # Wait for posters to load
    page.wait_for_selector("li.poster-container", timeout=10000)
    
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, 'html.parser')

# Check for poster-container
containers = soup.select("li.poster-container")
print(f"\nFound {len(containers)} li.poster-container elements")

if containers:
    print("\n=== First 3 poster-containers ===")
    for idx, container in enumerate(containers[:3]):
        print(f"\n--- Container {idx} ---")
        # Look for film link
        link = container.select_one('a')
        if link:
            href = link.get('href')
            title = link.get('data-film-name') or link.get('title') or container.get('data-film-name')
            print(f"Film: {title}")
            print(f"Link: {href}")
        
        # Look for ratings
        rating_spans = container.select('span.rating')
        print(f"Rating spans found: {len(rating_spans)}")
        for rs in rating_spans:
            classes = rs.get('class', [])
            print(f"  Classes: {classes}")
            print(f"  Text: {rs.get_text()}")
            
            # Extract rating
            for cls in classes:
                if cls.startswith('rated-'):
                    rating_10 = int(cls.replace('rated-', ''))
                    rating_5 = rating_10 / 2.0
                    print(f"  -> Rating: {rating_5}/5 (from {rating_10}/10)")
