#!/usr/bin/env python3
"""Convert collected_films_enriched.json to minimal schema used by LetterboxdNew.

Writes `collected_films_minimal.json` with fields:
  title, release_year, runtime, average_rating, genres, directors, actors,
  studios, language, country, writers, composer, cinematographer, description, url
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
IN_FILE = ROOT / "collected_films_enriched.json"
OUT_FILE = ROOT / "collected_films_minimal.json"

def to_list(maybe):
    if maybe is None:
        return []
    if isinstance(maybe, list):
        return maybe
    return [maybe]

def convert_item(item: dict) -> dict:
    # Prefer scraped `release_date`, fall back to parsed `year`
    release_date = item.get('release_date') or item.get('year')

    directors = item.get('directors')
    if not directors:
        # some items have singular 'director'
        if item.get('director'):
            directors = to_list(item.get('director'))
        else:
            directors = []

    # Derive scrape_status and last_scraped
    if item.get('scrape_status'):
        scrape_status = item.get('scrape_status')
    else:
        scrape_status = 'success' if item.get('fetched') else 'failed'

    last_scraped = item.get('last_scraped')

    minimal = {
        'title': item.get('title'),
        'release_date': release_date,
        'runtime': item.get('runtime'),
        'genres': item.get('genres') or [],
        'directors': directors,
        'actors': item.get('actors') or [],
        'studios': item.get('studios') or [],
        'language': item.get('language'),
        'country': item.get('country') or [],
        'writers': item.get('writers') or [],
        'composer': item.get('composer'),
        'cinematographer': item.get('cinematographer'),
        'average_rating': item.get('average_rating'),
        'description': item.get('description'),
        'scrape_status': scrape_status,
        'last_scraped': last_scraped,
        'url': item.get('url')
    }
    return minimal

def main():
    if not IN_FILE.exists():
        print(f"Input file not found: {IN_FILE}")
        return

    with IN_FILE.open('r', encoding='utf-8') as f:
        items = json.load(f)

    out = [convert_item(i) for i in items]

    with OUT_FILE.open('w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote minimal file: {OUT_FILE} (items: {len(out)})")

if __name__ == '__main__':
    main()
