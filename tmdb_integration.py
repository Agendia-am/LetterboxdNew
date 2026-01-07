"""
TMDB (The Movie Database) Integration
Fetches movie data for recommendations
"""

import requests
import json
import time
from pathlib import Path


class TMDBClient:
    """Client for The Movie Database API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    def __init__(self, api_key=None):
        """
        Initialize TMDB client
        
        Args:
            api_key: TMDB API key (get free at https://www.themoviedb.org/settings/api)
        """
        self.api_key = api_key or self._load_api_key()
        self.session = requests.Session()
        
    def _load_api_key(self):
        """Load API key from file or environment"""
        import os
        
        # Try environment variable first
        api_key = os.environ.get('TMDB_API_KEY')
        if api_key:
            return api_key
        
        # Try config file
        config_file = Path('.tmdb_api_key')
        if config_file.exists():
            return config_file.read_text().strip()
        
        return None
    
    def save_api_key(self, api_key):
        """Save API key to config file"""
        config_file = Path('.tmdb_api_key')
        config_file.write_text(api_key)
        self.api_key = api_key
        print(f"✅ API key saved to {config_file}")
    
    def test_connection(self):
        """Test if API key is valid"""
        if not self.api_key:
            return False
        
        try:
            url = f"{self.BASE_URL}/movie/popular"
            response = self.session.get(url, params={'api_key': self.api_key})
            return response.status_code == 200
        except:
            return False
    
    def get_popular_movies(self, pages=10, min_vote_count=100):
        """
        Get popular movies from TMDB
        
        Args:
            pages: Number of pages to fetch (20 movies per page)
            min_vote_count: Minimum number of votes required
        
        Returns:
            List of movie dictionaries
        """
        movies = []
        
        for page in range(1, pages + 1):
            try:
                url = f"{self.BASE_URL}/movie/popular"
                params = {
                    'api_key': self.api_key,
                    'page': page,
                    'language': 'en-US'
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for movie in data.get('results', []):
                    if movie.get('vote_count', 0) >= min_vote_count:
                        movies.append(self._convert_tmdb_movie(movie))
                
                time.sleep(0.25)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                continue
        
        return movies
    
    def get_top_rated_movies(self, pages=10, min_vote_count=500):
        """Get top rated movies from TMDB"""
        movies = []
        
        for page in range(1, pages + 1):
            try:
                url = f"{self.BASE_URL}/movie/top_rated"
                params = {
                    'api_key': self.api_key,
                    'page': page,
                    'language': 'en-US'
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for movie in data.get('results', []):
                    if movie.get('vote_count', 0) >= min_vote_count:
                        movies.append(self._convert_tmdb_movie(movie))
                
                time.sleep(0.25)
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                continue
        
        return movies
    
    def get_movies_by_genre(self, genre_ids, pages=5):
        """
        Get movies by genre IDs
        
        Args:
            genre_ids: List of genre IDs (e.g., [18, 80] for Drama, Crime)
            pages: Number of pages to fetch
        """
        movies = []
        genre_string = ','.join(map(str, genre_ids))
        
        for page in range(1, pages + 1):
            try:
                url = f"{self.BASE_URL}/discover/movie"
                params = {
                    'api_key': self.api_key,
                    'page': page,
                    'language': 'en-US',
                    'with_genres': genre_string,
                    'sort_by': 'vote_average.desc',
                    'vote_count.gte': 100
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for movie in data.get('results', []):
                    movies.append(self._convert_tmdb_movie(movie))
                
                time.sleep(0.25)
                
            except Exception as e:
                print(f"Error fetching genre page {page}: {e}")
                continue
        
        return movies
    
    def get_movie_details(self, tmdb_id):
        """Get detailed information about a movie"""
        try:
            url = f"{self.BASE_URL}/movie/{tmdb_id}"
            params = {
                'api_key': self.api_key,
                'append_to_response': 'credits,keywords'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return self._convert_detailed_movie(data)
            
        except Exception as e:
            print(f"Error fetching movie {tmdb_id}: {e}")
            return None
    
    def _convert_tmdb_movie(self, tmdb_movie):
        """Convert TMDB movie format to our format"""
        # Extract year from release_date
        release_year = None
        if tmdb_movie.get('release_date'):
            try:
                release_year = tmdb_movie['release_date'][:4]
            except:
                pass
        
        # Map TMDB genre IDs to names
        genre_map = {
            28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
            80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
            14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
            9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
            10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
        }
        
        genres = [genre_map.get(g['id'], g['name']) for g in tmdb_movie.get('genre_ids', []) if isinstance(g, dict)] if isinstance(tmdb_movie.get('genre_ids', [{}])[0], dict) else [genre_map.get(gid) for gid in tmdb_movie.get('genre_ids', []) if genre_map.get(gid)]
        
        # Convert rating from 0-10 to 0-5
        average_rating = None
        if tmdb_movie.get('vote_average'):
            average_rating = round(tmdb_movie['vote_average'] / 2, 1)
        
        return {
            'title': tmdb_movie.get('title', 'Unknown'),
            'release_date': release_year,
            'genres': genres,
            'directors': [],  # Need details call for this
            'actors': [],  # Need details call for this
            'average_rating': average_rating,
            'personal_rating': None,
            'description': tmdb_movie.get('overview', ''),
            'runtime': None,  # Need details call for this
            'url': f"https://letterboxd.com/tmdb/{tmdb_movie.get('id')}/",
            'tmdb_id': tmdb_movie.get('id'),
            'vote_count': tmdb_movie.get('vote_count', 0)
        }
    
    def _convert_detailed_movie(self, data):
        """Convert detailed TMDB movie to our format"""
        # Extract directors from crew
        directors = []
        crew = data.get('credits', {}).get('crew', [])
        for person in crew:
            if person.get('job') == 'Director':
                directors.append(person.get('name'))
        
        # Extract top actors from cast
        actors = []
        cast = data.get('credits', {}).get('cast', [])
        for person in cast[:10]:  # Top 10 actors
            actors.append(person.get('name'))
        
        # Extract year
        release_year = None
        if data.get('release_date'):
            try:
                release_year = data['release_date'][:4]
            except:
                pass
        
        # Extract genres
        genres = [g['name'] for g in data.get('genres', [])]
        
        # Convert rating
        average_rating = None
        if data.get('vote_average'):
            average_rating = round(data['vote_average'] / 2, 1)
        
        return {
            'title': data.get('title', 'Unknown'),
            'release_date': release_year,
            'genres': genres,
            'directors': directors,
            'actors': actors,
            'average_rating': average_rating,
            'personal_rating': None,
            'description': data.get('overview', ''),
            'runtime': f"{data.get('runtime', 0)} mins" if data.get('runtime') else None,
            'url': f"https://letterboxd.com/tmdb/{data.get('id')}/",
            'tmdb_id': data.get('id'),
            'vote_count': data.get('vote_count', 0)
        }


def setup_tmdb():
    """Interactive setup for TMDB API"""
    print("=" * 70)
    print("TMDB API SETUP")
    print("=" * 70)
    print("\nTo use movie recommendations, you need a free TMDB API key.")
    print("\n📝 How to get an API key:")
    print("   1. Go to: https://www.themoviedb.org/signup")
    print("   2. Create a free account")
    print("   3. Go to: https://www.themoviedb.org/settings/api")
    print("   4. Request an API key (choose 'Developer')")
    print("   5. Copy your API Key (v3 auth)")
    
    print("\n" + "=" * 70)
    api_key = input("\nEnter your TMDB API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("\n⚠️  Skipping TMDB setup. Recommendations will only work with scraped data.")
        return None
    
    # Test the key
    client = TMDBClient(api_key)
    print("\n🔍 Testing API key...")
    
    if client.test_connection():
        print("✅ API key is valid!")
        client.save_api_key(api_key)
        return client
    else:
        print("❌ API key is invalid. Please check and try again.")
        return None


def fetch_tmdb_movies(client, user_preferences=None, count=500):
    """
    Fetch movies from TMDB based on user preferences
    
    Args:
        client: TMDBClient instance
        user_preferences: Dict with user's favorite genres, directors, etc.
        count: Target number of movies to fetch
    
    Returns:
        List of movie dictionaries
    """
    if not client or not client.api_key:
        print("❌ TMDB client not configured. Run setup_tmdb() first.")
        return []
    
    print(f"\n📥 Fetching {count} movies from TMDB...")
    movies = []
    
    # Fetch popular movies
    print("   • Fetching popular movies...")
    popular = client.get_popular_movies(pages=5)
    movies.extend(popular)
    print(f"     Got {len(popular)} popular movies")
    
    # Fetch top rated
    print("   • Fetching top rated movies...")
    top_rated = client.get_top_rated_movies(pages=5)
    movies.extend(top_rated)
    print(f"     Got {len(top_rated)} top rated movies")
    
    # If we have user preferences, fetch genre-specific movies
    if user_preferences and user_preferences.get('favorite_genres'):
        genre_map = {
            "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35,
            "Crime": 80, "Documentary": 99, "Drama": 18, "Family": 10751,
            "Fantasy": 14, "History": 36, "Horror": 27, "Music": 10402,
            "Mystery": 9648, "Romance": 10749, "Science Fiction": 878,
            "Sci-Fi": 878, "Thriller": 53, "War": 10752, "Western": 37
        }
        
        favorite_genre_ids = []
        for genre in user_preferences['favorite_genres'][:3]:  # Top 3 genres
            genre_id = genre_map.get(genre)
            if genre_id:
                favorite_genre_ids.append(genre_id)
        
        if favorite_genre_ids:
            print(f"   • Fetching movies matching your favorite genres...")
            genre_movies = client.get_movies_by_genre(favorite_genre_ids, pages=3)
            movies.extend(genre_movies)
            print(f"     Got {len(genre_movies)} genre-matched movies")
    
    # Remove duplicates based on TMDB ID
    seen_ids = set()
    unique_movies = []
    for movie in movies:
        tmdb_id = movie.get('tmdb_id')
        if tmdb_id and tmdb_id not in seen_ids:
            seen_ids.add(tmdb_id)
            unique_movies.append(movie)
    
    print(f"\n✅ Fetched {len(unique_movies)} unique movies from TMDB")
    
    return unique_movies[:count]


if __name__ == "__main__":
    # Test TMDB integration
    client = setup_tmdb()
    if client:
        movies = fetch_tmdb_movies(client, count=50)
        print(f"\nSample movies:")
        for i, movie in enumerate(movies[:5], 1):
            print(f"{i}. {movie['title']} ({movie.get('release_date')}) - {movie.get('average_rating')}/5")
