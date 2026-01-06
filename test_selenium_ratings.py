"""Test with Selenium to see rendered content"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

username = "rjbritton08"
url = f"https://letterboxd.com/{username}/films/"

print(f"Fetching with Selenium: {url}")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
browser = webdriver.Chrome(service=service, options=chrome_options)

try:
    browser.get(url)
    
    # Wait for posters to load
    print("Waiting for posters to load...")
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.poster-container"))
        )
    except:
        print("Timeout waiting for li.poster-container")
    
    time.sleep(2)  # Extra wait for ratings to render
    
    html = browser.page_source
finally:
    browser.quit()

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
            title = container.get('data-film-name') or container.get('data-film-slug')
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
else:
    print("\nNo li.poster-container found. Checking for other structures...")
    
    # Check what we do have
    poster_list = soup.select("ul.poster-list")
    print(f"ul.poster-list found: {len(poster_list)}")
    
    if poster_list:
        print("\nChecking children of ul.poster-list:")
        for child in poster_list[0].children:
            if hasattr(child, 'name'):
                print(f"  Child: {child.name}, classes: {child.get('class')}")
