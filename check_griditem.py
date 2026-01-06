"""Check li.griditem structure"""
from bs4 import BeautifulSoup

with open('page_source.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

griditems = soup.select('li.griditem')
print(f"Found {len(griditems)} li.griditem elements\n")

if griditems:
    for idx, item in enumerate(griditems[:5]):
        print(f"=== Grid item {idx} ===")
        
        # Look for film link
        link = item.select_one('a[href^="/film/"]')
        if link:
            print(f"Link: {link.get('href')}")
            # Check for title
            img = link.select_one('img')
            if img:
                print(f"Title (from img alt): {img.get('alt')}")
        
        # Look for rating
        rating_span = item.select_one('span.rating')
        if rating_span:
            classes = rating_span.get('class', [])
            print(f"Rating classes: {classes}")
            for cls in classes:
                if cls.startswith('rated-'):
                    rating_10 = int(cls.replace('rated-', ''))
                    rating_5 = rating_10 / 2.0
                    print(f"Rating: {rating_5}/5")
        else:
            print("No rating found")
        
        print()
