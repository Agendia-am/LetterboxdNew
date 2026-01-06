"""Save and analyze the actual HTML structure"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

username = "rjbritton08"
url = f"https://letterboxd.com/{username}/films/"

print(f"Fetching: {url}")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=chrome_options)

try:
    browser.get(url)
    time.sleep(3)  # Wait for page to load
    html = browser.page_source
finally:
    browser.quit()

# Save to file
with open('page_source.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("HTML saved to page_source.html")

soup = BeautifulSoup(html, 'html.parser')

# Find all elements with rating spans
rating_spans = soup.select('span.rating')
print(f"\nFound {len(rating_spans)} rating spans total")

if rating_spans:
    print("\nAnalyzing first rating span's parent structure:")
    rs = rating_spans[0]
    
    # Walk up the tree
    current = rs
    level = 0
    while current and level < 6:
        name = current.name if hasattr(current, 'name') else 'text'
        classes = current.get('class', []) if hasattr(current, 'get') else []
        attrs = {}
        if hasattr(current, 'attrs'):
            attrs = {k: v for k, v in current.attrs.items() if k in ['data-film-id', 'data-film-slug', 'data-item-name', 'id']}
        
        print(f"{'  ' * level}{name} {classes} {attrs}")
        current = current.parent if hasattr(current, 'parent') else None
        level += 1

# Look for film links near ratings
print("\n\nLooking for film structure with ratings:")
for idx, rs in enumerate(rating_spans[:3]):
    print(f"\n=== Rating {idx} ===")
    print(f"Classes: {rs.get('class')}")
    print(f"Text: {rs.get_text()}")
    
    # Find nearest film link
    parent = rs.parent
    for _ in range(5):  # Go up 5 levels
        if parent:
            link = parent.select_one('a[href^="/film/"]')
            if link:
                print(f"Found link: {link.get('href')}")
                print(f"Link parent classes: {parent.get('class')}")
                break
            parent = parent.parent
