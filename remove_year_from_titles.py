#!/usr/bin/env python3
"""Remove year in parentheses from all title fields in JSON files."""
import json
import re
from pathlib import Path

def remove_year_from_title(title):
    """Remove year in parentheses from title"""
    if not title:
        return title
    return re.sub(r'\s*\(\d{4}\)\s*$', '', title).strip()

def process_file(file_path):
    """Process a JSON file and remove years from titles"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return False
    
    if not isinstance(data, list):
        print(f"Skipping {file_path}: not a JSON array")
        return False
    
    modified = False
    for item in data:
        if isinstance(item, dict) and 'title' in item:
            original = item['title']
            item['title'] = remove_year_from_title(item['title'])
            if original != item['title']:
                modified = True
                print(f"  {original} -> {item['title']}")
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Updated {file_path}")
        return True
    return False

def main():
    root = Path(__file__).parent
    json_files = [
        root / "collected_films.json",
        root / "matt_desi_detailed_films.json",
        root / "matt_desi_films_minimal.json",
    ]
    
    print("Removing year from titles in JSON files...\n")
    
    for json_file in json_files:
        if json_file.exists():
            print(f"Processing {json_file.name}:")
            process_file(json_file)
            print()
        else:
            print(f"Skipping {json_file.name}: file not found\n")

if __name__ == '__main__':
    main()
