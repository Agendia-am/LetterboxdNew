"""Test if li.poster-container has ratings"""
import requests
from bs4 import BeautifulSoup

username = "rjbritton08"
url = f"https://letterboxd.com/{username}/films/"

print(f"Fetching: {url}")
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Check for poster-container
containers = soup.select("li.poster-container")
print(f"\nFound {len(containers)} li.poster-container elements")

if containers:
    print("\n=== First poster-container ===")
    first = containers[0]
    print(str(first)[:1000])
    
    # Look for ratings inside
    rating_spans = first.select('span.rating')
    print(f"\nRating spans inside: {len(rating_spans)}")
    for rs in rating_spans:
        print(f"  Classes: {rs.get('class')}")
        print(f"  Text: {rs.get_text()}")
        
    # Look for film link
    link = first.select_one('a')
    if link:
        print(f"\nFilm link: {link.get('href')}")
        print(f"Film title: {link.get('title') or link.get('data-original-title')}")

# Also try ul.poster-list > li
print("\n\n=== Testing ul.poster-list > li ===")
containers2 = soup.select("ul.poster-list > li")
print(f"Found {len(containers2)} ul.poster-list > li elements")

if containers2:
    print("\n=== First ul.poster-list > li ===")
    first = containers2[0]
    print(str(first)[:1000])
    
    rating_spans = first.select('span.rating')
    print(f"\nRating spans inside: {len(rating_spans)}")
    for rs in rating_spans:
        print(f"  Classes: {rs.get('class')}")
        print(f"  Text: {rs.get_text()}")
