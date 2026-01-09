"""
Letterboxd Analyzer - Backend Server
Flask API for scraping and analyzing Letterboxd profiles
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
from pathlib import Path
import traceback

# Import existing scraper functionality
from LetterboxdNew import (
    FilmScraper, 
    collect_all_films, 
    load_existing_data,
    merge_film_data
)

# Import visualization and recommendation modules
try:
    import viz_report
    VIZ_AVAILABLE = True
except ImportError:
    VIZ_AVAILABLE = False

try:
    import movie_recommender
    RECOMMENDER_AVAILABLE = True
except ImportError:
    RECOMMENDER_AVAILABLE = False

app = Flask(__name__, static_folder='frontend', template_folder='frontend')
CORS(app)  # Enable CORS for all routes

# Data directory for storing scraped data
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)


@app.route('/')
def index():
    """Serve the main frontend page"""
    return render_template('index.html')


@app.route('/api/scrape', methods=['POST'])
def scrape_profile():
    """
    Scrape a Letterboxd profile
    
    Request body:
    {
        "username": "letterboxd_username",
        "max_pages": 10 (optional),
        "parallel_workers": 5 (optional)
    }
    
    Returns:
    {
        "success": true,
        "username": "username",
        "total_films": 123,
        "films": [...],
        "stats": {...}
    }
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        max_pages = data.get('max_pages', None)
        parallel_workers = data.get('parallel_workers', 5)
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username is required'
            }), 400
        
        print(f"\n{'='*60}")
        print(f"API: Starting scrape for user: {username}")
        print(f"{'='*60}")
        
        # Check for existing data
        existing_data = load_existing_data(username)
        
        # Collect all films from profile
        all_films_basic = collect_all_films(username, max_pages=max_pages)
        
        if not all_films_basic:
            return jsonify({
                'success': False,
                'error': f'Could not find any films for user: {username}'
            }), 404
        
        print(f"\nFound {len(all_films_basic)} films on profile")
        
        # Scrape detailed information (use requests only on Vercel/production)
        import os
        is_production = os.getenv('VERCEL') or os.getenv('PRODUCTION')
        scraper = FilmScraper(
            use_playwright=not is_production, 
            use_selenium=False, 
            debug=False
        )
        
        try:
            detailed_films = scraper.scrape_all_films(
                all_films_basic,
                max_films=len(all_films_basic),
                parallel_workers=parallel_workers
            )
            
            # Merge with existing data
            if existing_data:
                detailed_films = merge_film_data(existing_data, detailed_films)
            
            # Save to file
            output_file = DATA_DIR / f'{username}_films.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_films, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Saved data to {output_file}")
            
            # Calculate stats
            stats = calculate_stats(detailed_films)
            
            return jsonify({
                'success': True,
                'username': username,
                'total_films': len(detailed_films),
                'films': detailed_films,
                'stats': stats
            })
            
        finally:
            scraper.cleanup()
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Generate movie recommendations
    
    Request body:
    {
        "username": "letterboxd_username",
        "top_n": 10 (optional)
    }
    
    Returns:
    {
        "success": true,
        "recommendations": [...]
    }
    """
    if not RECOMMENDER_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Recommender module not available'
        }), 500
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        top_n = data.get('top_n', 10)
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username is required'
            }), 400
        
        print(f"\n{'='*60}")
        print(f"API: Generating recommendations for: {username}")
        print(f"{'='*60}")
        
        # Generate recommendations
        recommendations = movie_recommender.generate_recommendations(
            username, 
            top_n=top_n,
            fetch_popular=True,
            popular_count=500
        )
        
        if not recommendations:
            return jsonify({
                'success': False,
                'error': 'Could not generate recommendations'
            }), 500
        
        return jsonify({
            'success': True,
            'username': username,
            'count': len(recommendations),
            'recommendations': recommendations
        })
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/visualizations', methods=['POST'])
def generate_visualizations():
    """
    Generate visualization data for charts
    
    Request body:
    {
        "username": "letterboxd_username"
    }
    
    Returns:
    {
        "success": true,
        "charts": {...}
    }
    """
    if not VIZ_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Visualization module not available'
        }), 500
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({
                'success': False,
                'error': 'Username is required'
            }), 400
        
        print(f"\n{'='*60}")
        print(f"API: Generating visualizations for: {username}")
        print(f"{'='*60}")
        
        # Load user data
        films_file = DATA_DIR / f'{username}_films.json'
        if not films_file.exists():
            return jsonify({
                'success': False,
                'error': f'No data found for user: {username}'
            }), 404
        
        with open(films_file, 'r', encoding='utf-8') as f:
            films = json.load(f)
        
        # Generate chart data (modify viz_report to return JSON instead of HTML)
        charts_data = generate_chart_data(films)
        
        return jsonify({
            'success': True,
            'username': username,
            'charts': charts_data
        })
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def calculate_stats(films):
    """Calculate statistics from film data"""
    stats = {
        'total_films': len(films),
        'with_ratings': 0,
        'average_rating': 0,
        'total_runtime': 0,
        'genres': {},
        'directors': {},
        'years': {}
    }
    
    total_rating = 0
    
    for film in films:
        # Ratings
        if film.get('personal_rating'):
            stats['with_ratings'] += 1
            try:
                total_rating += float(film['personal_rating'])
            except (ValueError, TypeError):
                pass
        
        # Runtime
        runtime = film.get('runtime')
        if runtime:
            try:
                if isinstance(runtime, str):
                    import re
                    match = re.search(r'(\d+)', runtime)
                    if match:
                        stats['total_runtime'] += int(match.group(1))
                else:
                    stats['total_runtime'] += int(runtime)
            except (ValueError, TypeError):
                pass
        
        # Genres
        for genre in film.get('genres', []):
            stats['genres'][genre] = stats['genres'].get(genre, 0) + 1
        
        # Directors
        for director in film.get('directors', []):
            stats['directors'][director] = stats['directors'].get(director, 0) + 1
        
        # Years
        year = film.get('year')
        if year:
            try:
                year = int(float(year))
                stats['years'][year] = stats['years'].get(year, 0) + 1
            except (ValueError, TypeError):
                pass
    
    if stats['with_ratings'] > 0:
        stats['average_rating'] = round(total_rating / stats['with_ratings'], 2)
    
    # Sort and limit
    stats['top_genres'] = sorted(stats['genres'].items(), key=lambda x: x[1], reverse=True)[:10]
    stats['top_directors'] = sorted(stats['directors'].items(), key=lambda x: x[1], reverse=True)[:10]
    
    return stats


def generate_chart_data(films):
    """Generate data for frontend charts"""
    # This will return data in a format the frontend can use
    # Instead of generating Plotly HTML, we'll return raw data
    
    return {
        'rating_distribution': get_rating_distribution(films),
        'films_by_year': get_films_by_year(films),
        'top_genres': get_top_genres(films),
        'runtime_distribution': get_runtime_distribution(films)
    }


def get_rating_distribution(films):
    """Get rating distribution data"""
    ratings = {}
    for film in films:
        rating = film.get('personal_rating')
        if rating:
            try:
                r = float(rating)
                ratings[r] = ratings.get(r, 0) + 1
            except (ValueError, TypeError):
                pass
    
    return sorted(ratings.items())


def get_films_by_year(films):
    """Get films by year data"""
    years = {}
    for film in films:
        year = film.get('year')
        if year:
            try:
                y = int(float(year))
                years[y] = years.get(y, 0) + 1
            except (ValueError, TypeError):
                pass
    
    return sorted(years.items())


def get_top_genres(films):
    """Get top genres data"""
    genres = {}
    for film in films:
        for genre in film.get('genres', []):
            genres[genre] = genres.get(genre, 0) + 1
    
    return sorted(genres.items(), key=lambda x: x[1], reverse=True)[:15]


def get_runtime_distribution(films):
    """Get runtime distribution data"""
    runtimes = []
    for film in films:
        runtime = film.get('runtime')
        if runtime:
            try:
                if isinstance(runtime, str):
                    import re
                    match = re.search(r'(\d+)', runtime)
                    if match:
                        runtimes.append(int(match.group(1)))
                else:
                    runtimes.append(int(runtime))
            except (ValueError, TypeError):
                pass
    
    return runtimes


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'features': {
            'scraping': True,
            'recommendations': RECOMMENDER_AVAILABLE,
            'visualizations': VIZ_AVAILABLE
        }
    })


if __name__ == '__main__':
    print(f"""
{'='*60}
🎬 LETTERBOXD ANALYZER SERVER
{'='*60}
Server starting on http://localhost:5000
    
Available endpoints:
  GET  /                    - Frontend homepage
  POST /api/scrape          - Scrape user profile
  POST /api/recommendations - Generate recommendations
  POST /api/visualizations  - Get visualization data
  GET  /health              - Health check
{'='*60}
""")
    
    app.run(debug=True, host='0.0.0.0', port=5005)
