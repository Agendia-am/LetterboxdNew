#!/usr/bin/env python3
"""Normalize any JSON array of film objects to the `films_progress_10.json` schema.

Creates `<original>_normalized.json` for each input JSON file in the current folder.
"""
import json
from pathlib import Path
from datetime import datetime

SCHEMA_KEYS = [
    'url','title','release_date','runtime','genres','directors','actors','studios',
    'language','country','writers','composer','cinematographer','average_rating',
    'description','scrape_status','last_scraped'
]

ROOT = Path(__file__).parent

def to_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]

def normalize_item(item: dict) -> dict:
    # Map common alternatives to target keys
    release_date = item.get('release_date') or item.get('release_year') or item.get('year')
    runtime = item.get('runtime')
    genres = item.get('genres') or []
    directors = item.get('directors') or to_list(item.get('director'))
    actors = item.get('actors') or []
    studios = item.get('studios') or []
    language = item.get('language')
    country = item.get('country') or []
    writers = item.get('writers') or []
    composer = item.get('composer')
    cinematographer = item.get('cinematographer')
    average_rating = item.get('average_rating') or item.get('rating')
    description = item.get('description') or item.get('summary')
    scrape_status = item.get('scrape_status') or ('success' if item.get('fetched') else 'failed')
    last_scraped = item.get('last_scraped') or datetime.now().isoformat()

    normalized = {
        'url': item.get('url'),
        'title': item.get('title'),
        'release_date': release_date,
        'runtime': runtime,
        'genres': genres,
        'directors': directors,
        'actors': actors,
        'studios': studios,
        'language': language,
        'country': country,
        'writers': writers,
        'composer': composer,
        'cinematographer': cinematographer,
        'average_rating': average_rating,
        'description': description,
        'scrape_status': scrape_status,
        'last_scraped': last_scraped
    }
    return normalized

def main():
    json_files = [p for p in ROOT.iterdir() if p.suffix == '.json']
    if not json_files:
        print('No JSON files found in folder.')
        return

    for p in json_files:
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"Skipping {p.name}: failed to read JSON: {e}")
            continue

        if not isinstance(data, list):
            print(f"Skipping {p.name}: JSON root is not a list")
            continue

        out = [normalize_item(item) for item in data]
        out_path = p.with_name(p.stem + '_normalized.json')
        out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"Wrote {out_path.name} ({len(out)} items)")

if __name__ == '__main__':
    main()
