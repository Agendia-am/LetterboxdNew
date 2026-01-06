"""Test script to diagnose rating extraction issues"""
import requests
from bs4 import BeautifulSoup

username = "rjbritton08"  # Replace with your username
url = f"https://letterboxd.com/{username}/films/"

print(f"Fetching: {url}")
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Try different selectors
print("\n=== Testing different selectors ===\n")

selectors_to_test = [
    ("li.poster-container", "Full poster container"),
    ("div.react-component[data-component-class='LazyPoster']", "React LazyPoster component"),
    ("li[data-film-id]", "List item with film ID"),
]

for selector, description in selectors_to_test:
    containers = soup.select(selector)
    print(f"{description}: {selector}")
    print(f"  Found {len(containers)} containers")
    
    if containers:
        # Look at first container
        first = containers[0]
        print(f"\n  First container HTML (first 800 chars):")
        print(f"  {str(first)[:800]}")
        
        # Try to find rating
        rating_spans = first.select('span.rating')
        print(f"\n  Found {len(rating_spans)} span.rating elements")
        
        if rating_spans:
            for idx, rs in enumerate(rating_spans[:3]):
                print(f"    Rating span {idx}: classes={rs.get('class')}, text={rs.get_text()}")
        
        # Try broader search
        all_spans = first.select('span')
        rated_spans = [s for s in all_spans if any('rated-' in c for c in s.get('class', []))]
        print(f"\n  Found {len(rated_spans)} spans with 'rated-' in classes")
        for rs in rated_spans[:3]:
            print(f"    Span: classes={rs.get('class')}, text={rs.get_text()}")
    
    print("\n" + "="*70 + "\n")

# Also check if ratings exist anywhere on the page
print("\n=== Looking for any rating spans on the page ===\n")
all_rating_spans = soup.select('span.rating')
print(f"Total span.rating elements on page: {len(all_rating_spans)}")

if all_rating_spans:
    print("\nFirst 5 rating spans:")
    for idx, rs in enumerate(all_rating_spans[:5]):
        classes = rs.get('class', [])
        parent = rs.parent
        parent_classes = parent.get('class', []) if parent else []
        print(f"  {idx}: classes={classes}")
        print(f"       text={rs.get_text()}")
        print(f"       parent={parent.name if parent else 'None'}, parent_classes={parent_classes}")
        print()
