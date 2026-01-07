"""
Movie Recommendation System for Letterboxd Data
Uses scikit-learn for content-based and hybrid recommendations
Scrapes popular films from Letterboxd for recommendations
"""

import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from sklearn.preprocessing import MinMaxScaler
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


class MovieRecommender:
    """
    Hybrid Movie Recommendation System
    Combines content-based filtering with user preference analysis
    """
    
    def __init__(self, films_data):
        """
        Initialize recommender with user's film data
        
        Args:
            films_data: List of film dictionaries from scraped Letterboxd data
        """
        self.films_data = films_data
        self.df = self._prepare_dataframe()
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.content_similarity = None
        
    def _prepare_dataframe(self):
        """Convert films data to pandas DataFrame and clean it"""
        df = pd.DataFrame(self.films_data)
        
        # Ensure all necessary columns exist
        required_cols = ['title', 'genres', 'directors', 'actors', 'average_rating', 
                        'personal_rating', 'description', 'release_date', 'runtime']
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        
        # Clean and normalize data
        df['genres'] = df['genres'].apply(lambda x: x if isinstance(x, list) else [])
        df['directors'] = df['directors'].apply(lambda x: x if isinstance(x, list) else [])
        df['actors'] = df['actors'].apply(lambda x: x if isinstance(x, list) else [])
        df['description'] = df['description'].fillna('')
        
        # Convert ratings to numeric
        df['average_rating'] = pd.to_numeric(df['average_rating'], errors='coerce')
        df['personal_rating'] = pd.to_numeric(df['personal_rating'], errors='coerce')
        
        # Extract year from release_date
        df['year'] = df['release_date'].apply(self._extract_year)
        
        # Convert runtime to numeric (handle strings like "120 mins")
        df['runtime_mins'] = df['runtime'].apply(self._parse_runtime)
        
        return df
    
    def _extract_year(self, release_date):
        """Extract year from various release_date formats"""
        if pd.isna(release_date) or release_date is None:
            return None
        if isinstance(release_date, (int, float)):
            return int(release_date)
        try:
            # Try to extract 4-digit year
            import re
            match = re.search(r'\b(19|20)\d{2}\b', str(release_date))
            if match:
                return int(match.group())
        except:
            pass
        return None
    
    def _parse_runtime(self, runtime):
        """Parse runtime from various formats"""
        if pd.isna(runtime) or runtime is None:
            return None
        try:
            if isinstance(runtime, (int, float)):
                return float(runtime)
            # Extract numeric value from string like "120 mins"
            import re
            match = re.search(r'(\d+)', str(runtime))
            if match:
                return float(match.group(1))
        except:
            pass
        return None
    
    def build_content_features(self):
        """Build TF-IDF features from content (genres, directors, actors, description)"""
        # Create content string for each movie
        self.df['content'] = self.df.apply(self._create_content_string, axis=1)
        
        # Build TF-IDF matrix
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.df['content'])
        
        # Compute cosine similarity matrix
        self.content_similarity = linear_kernel(self.tfidf_matrix, self.tfidf_matrix)
        
        return self.content_similarity
    
    def _create_content_string(self, row):
        """Create a content string combining all features"""
        parts = []
        
        # Add genres (weight them by repeating)
        if row['genres']:
            parts.extend([genre.lower().replace(' ', '_') for genre in row['genres']] * 3)
        
        # Add directors (weight them highly)
        if row['directors']:
            parts.extend([f"director_{d.lower().replace(' ', '_')}" for d in row['directors']] * 4)
        
        # Add top actors
        if row['actors']:
            top_actors = row['actors'][:5]  # Use top 5 actors
            parts.extend([f"actor_{a.lower().replace(' ', '_')}" for a in top_actors] * 2)
        
        # Add description keywords
        if row['description']:
            parts.append(row['description'][:200])  # First 200 chars
        
        return ' '.join(parts)
    
    def analyze_user_preferences(self):
        """Analyze user's rating patterns to understand preferences"""
        rated_films = self.df[self.df['personal_rating'].notna()].copy()
        
        if len(rated_films) == 0:
            return None
        
        # Calculate high-rated threshold (4+ or top 30%)
        threshold = max(4.0, rated_films['personal_rating'].quantile(0.7))
        
        preferences = {
            'favorite_genres': self._get_top_from_rated(rated_films, 'genres', threshold),
            'favorite_directors': self._get_top_from_rated(rated_films, 'directors', threshold),
            'favorite_actors': self._get_top_from_rated(rated_films, 'actors', threshold),
            'avg_runtime_preference': rated_films[rated_films['personal_rating'] >= threshold]['runtime_mins'].mean(),
            'avg_year_preference': rated_films[rated_films['personal_rating'] >= threshold]['year'].mean(),
            'rating_threshold': threshold,
            'avg_personal_rating': rated_films['personal_rating'].mean(),
            'total_rated': len(rated_films)
        }
        
        return preferences
    
    def _get_top_from_rated(self, rated_films, column, threshold, top_n=10):
        """Get top items from highly rated films"""
        high_rated = rated_films[rated_films['personal_rating'] >= threshold]
        
        all_items = []
        for items in high_rated[column]:
            if isinstance(items, list):
                all_items.extend(items)
        
        if not all_items:
            return []
        
        counter = Counter(all_items)
        return [item for item, count in counter.most_common(top_n)]
    
    def get_content_based_recommendations(self, film_index, top_n=10):
        """Get recommendations based on content similarity to a specific film"""
        if self.content_similarity is None:
            self.build_content_features()
        
        # Get similarity scores for this film
        sim_scores = list(enumerate(self.content_similarity[film_index]))
        
        # Sort by similarity score
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar films (excluding the film itself)
        sim_scores = sim_scores[1:top_n+1]
        
        film_indices = [i[0] for i in sim_scores]
        
        return self.df.iloc[film_indices]
    
    def get_hybrid_recommendations(self, top_n=10, exclude_rated=True):
        """
        Generate hybrid recommendations based on:
        1. User's rating preferences
        2. Content similarity to highly-rated films
        3. Average ratings
        4. Preference alignment
        
        Args:
            top_n: Number of recommendations to return
            exclude_rated: Whether to exclude already rated films
        
        Returns:
            DataFrame with top N recommended films
        """
        if self.content_similarity is None:
            self.build_content_features()
        
        # Get user preferences
        preferences = self.analyze_user_preferences()
        
        # Start with all films
        candidates = self.df.copy()
        
        # Exclude already rated films if requested
        if exclude_rated and preferences:
            candidates = candidates[candidates['personal_rating'].isna()]
        
        if len(candidates) == 0:
            print("All films have been rated. Showing top-rated films instead.")
            return self.df.nlargest(top_n, 'average_rating')
        
        # Initialize recommendation score
        candidates['rec_score'] = 0.0
        
        # Score 1: Average rating (20% weight)
        if candidates['average_rating'].notna().any():
            scaler = MinMaxScaler()
            valid_ratings = candidates['average_rating'].notna()
            candidates.loc[valid_ratings, 'rating_score'] = scaler.fit_transform(
                candidates.loc[valid_ratings, 'average_rating'].values.reshape(-1, 1)
            ).flatten()
            candidates['rec_score'] += candidates['rating_score'].fillna(0) * 0.2
        
        # Score 2: Content similarity to user's favorites (40% weight)
        if preferences and preferences['total_rated'] > 0:
            # Get indices of highly rated films
            high_rated_indices = self.df[
                (self.df['personal_rating'].notna()) & 
                (self.df['personal_rating'] >= preferences['rating_threshold'])
            ].index.tolist()
            
            if high_rated_indices:
                # Calculate average similarity to all high-rated films
                for idx in candidates.index:
                    if idx in self.df.index:
                        df_position = self.df.index.get_loc(idx)
                        similarities = [self.content_similarity[df_position][self.df.index.get_loc(hr_idx)] 
                                      for hr_idx in high_rated_indices 
                                      if hr_idx in self.df.index]
                        if similarities:
                            candidates.loc[idx, 'content_sim_score'] = np.mean(similarities)
                
                # Normalize and add to rec_score
                if candidates['content_sim_score'].notna().any():
                    scaler = MinMaxScaler()
                    valid_sim = candidates['content_sim_score'].notna()
                    candidates.loc[valid_sim, 'content_sim_normalized'] = scaler.fit_transform(
                        candidates.loc[valid_sim, 'content_sim_score'].values.reshape(-1, 1)
                    ).flatten()
                    candidates['rec_score'] += candidates['content_sim_normalized'].fillna(0) * 0.4
        
        # Score 3: Genre preference match (20% weight)
        if preferences and preferences['favorite_genres']:
            candidates['genre_match_score'] = candidates['genres'].apply(
                lambda x: len(set(x) & set(preferences['favorite_genres'])) / len(preferences['favorite_genres'])
                if isinstance(x, list) and len(x) > 0 else 0
            )
            candidates['rec_score'] += candidates['genre_match_score'] * 0.2
        
        # Score 4: Director preference match (15% weight)
        if preferences and preferences['favorite_directors']:
            candidates['director_match_score'] = candidates['directors'].apply(
                lambda x: len(set(x) & set(preferences['favorite_directors'])) / len(preferences['favorite_directors'])
                if isinstance(x, list) and len(x) > 0 else 0
            )
            candidates['rec_score'] += candidates['director_match_score'] * 0.15
        
        # Score 5: Actor preference match (5% weight)
        if preferences and preferences['favorite_actors']:
            candidates['actor_match_score'] = candidates['actors'].apply(
                lambda x: len(set(x) & set(preferences['favorite_actors'])) / max(len(preferences['favorite_actors']), 1)
                if isinstance(x, list) and len(x) > 0 else 0
            )
            candidates['rec_score'] += candidates['actor_match_score'] * 0.05
        
        # Sort by recommendation score
        recommendations = candidates.nlargest(top_n, 'rec_score')
        
        return recommendations
    
    def explain_recommendation(self, film_row, preferences=None):
        """Generate explanation for why a film was recommended"""
        reasons = []
        
        if preferences:
            # Check genre matches
            if film_row.get('genres') and preferences.get('favorite_genres'):
                matching_genres = set(film_row['genres']) & set(preferences['favorite_genres'])
                if matching_genres:
                    reasons.append(f"Genres you love: {', '.join(list(matching_genres)[:3])}")
            
            # Check director matches
            if film_row.get('directors') and preferences.get('favorite_directors'):
                matching_directors = set(film_row['directors']) & set(preferences['favorite_directors'])
                if matching_directors:
                    reasons.append(f"Director you enjoy: {', '.join(list(matching_directors)[:2])}")
            
            # Check actor matches
            if film_row.get('actors') and preferences.get('favorite_actors'):
                matching_actors = set(film_row['actors']) & set(preferences['favorite_actors'])
                if matching_actors:
                    reasons.append(f"Actors you like: {', '.join(list(matching_actors)[:2])}")
        
        # Check high average rating
        if pd.notna(film_row.get('average_rating')) and film_row['average_rating'] >= 3.5:
            reasons.append(f"High community rating: {film_row['average_rating']:.1f}/5")
        
        return reasons if reasons else ["Recommended based on your viewing patterns"]


def load_user_data(username):
    """Load user's film data from JSON files"""
    # Try minimal file first, then detailed file
    filenames = [
        f'{username}_films_minimal.json',
        f'{username}_detailed_films.json',
        'collected_films.json'
    ]
    
    for filename in filenames:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    print(f"Loaded {len(data)} films from {filename}")
                    return data
        except FileNotFoundError:
            continue
    
    return None


def generate_recommendations(username, top_n=10, fetch_popular=True, popular_count=500):
    """
    Main function to generate movie recommendations
    
    Args:
        username: Letterboxd username
        top_n: Number of recommendations to return (default 10)
        fetch_popular: Whether to fetch popular films from Letterboxd (default True)
        popular_count: Number of popular films to fetch (default 500)
    
    Returns:
        List of recommended films with explanations
    """
    # Load user data (watched films)
    watched_films = load_user_data(username)
    
    if not watched_films:
        print(f"Error: No data found for user '{username}'")
        print("Please run the main scraper first to collect film data.")
        return None
    
    print(f"\n{'='*60}")
    print(f"GENERATING RECOMMENDATIONS FOR {username.upper()}")
    print(f"{'='*60}")
    print(f"\n📊 Your watched films: {len(watched_films)}")
    
    # Get popular films from Letterboxd if requested
    popular_films = []
    if fetch_popular:
        print(f"\n🌐 Fetching popular films from Letterboxd...")
        
        try:
            # Import the collection function
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from LetterboxdNew import collect_popular_films
            
            # Fetch popular films
            popular_films = collect_popular_films(max_films=popular_count, min_pages=10)
            
            if popular_films:
                # Filter out movies the user has already watched
                watched_urls = set(film.get('url') for film in watched_films if film.get('url'))
                watched_titles = set(film.get('title', '').lower().strip() for film in watched_films if film.get('title'))
                
                # Remove watched movies from popular list
                unwatched_popular = []
                for movie in popular_films:
                    movie_url = movie.get('url')
                    movie_title = movie.get('title', '').lower().strip()
                    
                    # Skip if URL matches or title matches
                    if movie_url not in watched_urls and movie_title not in watched_titles:
                        unwatched_popular.append(movie)
                
                print(f"✅ Found {len(unwatched_popular)} unwatched films from Letterboxd")
                popular_films = unwatched_popular
        except Exception as e:
            print(f"⚠️  Error fetching popular films: {e}")
            print("Continuing with only your watched films...")
            popular_films = []
    
    # Combine datasets: watched films + unwatched popular films
    if popular_films:
        # Now scrape details for popular films
        print(f"\n📥 Scraping details for {len(popular_films)} popular films...")
        print("(This may take a few minutes...)")
        
        try:
            from LetterboxdNew import FilmScraper
            scraper = FilmScraper(use_playwright=True, use_selenium=False, debug=False)
            
            # Scrape popular films in batches with progress
            from tqdm import tqdm
            detailed_popular = []
            
            for film in tqdm(popular_films, desc="Scraping popular films", unit="film"):
                film_url = film.get('url')
                if film_url:
                    details = scraper.scrape_film_details(film_url)
                    if details and details.get('scrape_status') == 'success':
                        detailed_popular.append(details)
                    
                    # Stop if we have enough
                    if len(detailed_popular) >= popular_count:
                        break
            
            print(f"✅ Scraped details for {len(detailed_popular)} films")
            popular_films = detailed_popular
            
        except Exception as e:
            print(f"⚠️  Error scraping details: {e}")
            print("Using popular films without full details...")
    
    # Combine datasets
    if popular_films:
        all_films = watched_films + popular_films
        print(f"\n📚 Total dataset: {len(all_films)} films ({len(watched_films)} watched + {len(popular_films)} unwatched)")
    else:
        all_films = watched_films
        print(f"\n⚠️  Working with only your watched films ({len(watched_films)} films)")
        print("     Recommendations may include films you've already seen.")
    
    # Initialize recommender with combined dataset
    recommender = MovieRecommender(all_films)
    
    # Analyze preferences
    preferences = recommender.analyze_user_preferences()
    
    if preferences:
        print(f"\n📊 Your Viewing Profile:")
        print(f"   Films rated: {preferences['total_rated']}")
        print(f"   Average rating: {preferences['avg_personal_rating']:.2f}/5")
        print(f"\n🎭 Favorite Genres: {', '.join(preferences['favorite_genres'][:5])}")
        print(f"🎬 Favorite Directors: {', '.join(preferences['favorite_directors'][:5])}")
        print(f"⭐ Favorite Actors: {', '.join(preferences['favorite_actors'][:5])}")
    else:
        print("\n⚠️  No ratings found. Recommendations based on community ratings only.")
    
    # Generate recommendations (exclude watched films)
    print(f"\n{'='*60}")
    print(f"TOP {top_n} RECOMMENDED MOVIES (UNWATCHED)")
    print(f"{'='*60}\n")
    
    recommendations = recommender.get_hybrid_recommendations(top_n=top_n, exclude_rated=True)
    
    # Display recommendations with details
    results = []
    for idx, (_, film) in enumerate(recommendations.iterrows(), 1):
        print(f"{idx}. {film['title']} ({film.get('year', 'N/A')})")
        print(f"   ⭐ Community Rating: {film.get('average_rating', 'N/A')}/5")
        
        # Show genres
        if film.get('genres'):
            print(f"   🎭 Genres: {', '.join(film['genres'][:3])}")
        
        # Show directors
        if film.get('directors'):
            print(f"   🎬 Director: {', '.join(film['directors'][:2])}")
        
        # Show explanation
        reasons = recommender.explain_recommendation(film, preferences)
        print(f"   💡 Why: {reasons[0]}")
        if len(reasons) > 1:
            for reason in reasons[1:3]:
                print(f"       {reason}")
        
        # Show URL
        if film.get('url'):
            print(f"   🔗 {film['url']}")
        
        print()
        
        results.append({
            'rank': idx,
            'title': film['title'],
            'year': film.get('year'),
            'average_rating': film.get('average_rating'),
            'genres': film.get('genres'),
            'directors': film.get('directors'),
            'url': film.get('url'),
            'reasons': reasons,
            'rec_score': film.get('rec_score', 0)
        })
    
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    else:
        username = input("Enter Letterboxd username: ").strip()
        top_n = 10
    
    if username:
        recommendations = generate_recommendations(username, top_n)
        
        if recommendations:
            # Save recommendations to file
            output_file = f'{username}_recommendations.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Recommendations saved to '{output_file}'")
    else:
        print("Error: Username cannot be empty!")
