"""Print full HTML of first griditem"""
from bs4 import BeautifulSoup

with open('page_source.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

griditems = soup.select('li.griditem')
if griditems:
    print("=== First griditem full HTML ===\n")
    print(griditems[0].prettify())
