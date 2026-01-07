# Movie Recommendation System for Letterboxd

A machine learning-based recommendation system that generates personalized movie recommendations based on your Letterboxd viewing history and ratings.

## Features

- **Hybrid Recommendation Algorithm**: Combines multiple recommendation strategies:
  - Content-based filtering using TF-IDF and cosine similarity
  - User preference analysis based on your ratings
  - Genre, director, and actor preference matching
  - Community rating signals

- **Intelligent Scoring**: Recommendations are scored based on:
  - 40% Content similarity to your highly-rated films
  - 20% Average community rating
  - 20% Genre preference match
  - 15% Director preference match
  - 5% Actor preference match

- **Personalized Explanations**: Each recommendation includes reasons why it was suggested

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

Required packages:
- `scikit-learn>=1.3.0` - Machine learning algorithms
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing

## Usage

### Method 1: Integrated with Main Scraper

After scraping your Letterboxd data, the main script will prompt you to generate recommendations:

```bash
python LetterboxdNew.py
```

Follow the prompts and when asked "Would you like to generate movie recommendations?", answer `yes`.

### Method 2: Standalone Recommendation Script

Generate recommendations directly from existing data:

```bash
python movie_recommender.py
```

Or specify the username:

```bash
python movie_recommender.py your_letterboxd_username
```

### Method 3: Import as Module

Use the recommender in your own Python scripts:

```python
from movie_recommender import MovieRecommender, generate_recommendations

# Generate recommendations
recommendations = generate_recommendations('username', top_n=10)

# Or use the class directly
from movie_recommender import load_user_data, MovieRecommender

films_data = load_user_data('username')
recommender = MovieRecommender(films_data)

# Analyze preferences
preferences = recommender.analyze_user_preferences()
print(f"Favorite genres: {preferences['favorite_genres']}")

# Get recommendations
recommendations = recommender.get_hybrid_recommendations(top_n=10)
```

## How It Works

### 1. Data Preparation
- Loads your scraped Letterboxd data (ratings, genres, directors, actors, etc.)
- Cleans and normalizes the data into a pandas DataFrame
- Extracts features for machine learning

### 2. User Preference Analysis
- Identifies your highly-rated films (4+ stars or top 30%)
- Analyzes patterns in:
  - Favorite genres
  - Favorite directors
  - Favorite actors
  - Preferred runtime and release periods

### 3. Content Feature Engineering
- Creates rich content representations using TF-IDF vectorization
- Combines multiple features:
  - Genres (weighted 3x)
  - Directors (weighted 4x)
  - Top 5 actors (weighted 2x)
  - Film descriptions
- Computes content similarity matrix using cosine similarity

### 4. Hybrid Recommendation Scoring
For each candidate film, calculates a composite score:

```
rec_score = 0.20 * normalized_avg_rating
          + 0.40 * avg_similarity_to_favorites
          + 0.20 * genre_match_ratio
          + 0.15 * director_match_ratio
          + 0.05 * actor_match_ratio
```

### 5. Results & Explanations
- Ranks films by recommendation score
- Excludes already-rated films (configurable)
- Provides personalized explanations for each recommendation

## Output

The recommendation system generates:

1. **Console Output**: Formatted list of top 10 recommendations with:
   - Film title and year
   - Community rating
   - Genres and director
   - Personalized explanation
   - Letterboxd URL

2. **JSON File**: `{username}_recommendations.json` containing:
   ```json
   [
     {
       "rank": 1,
       "title": "Film Title",
       "year": 2023,
       "average_rating": 4.2,
       "genres": ["Drama", "Thriller"],
       "directors": ["Director Name"],
       "url": "https://letterboxd.com/film/...",
       "reasons": ["Genres you love: Drama", "Director you enjoy: ..."],
       "rec_score": 0.85
     }
   ]
   ```

## Example Output

```
============================================================
GENERATING RECOMMENDATIONS FOR YOUR_USERNAME
============================================================

📊 Your Viewing Profile:
   Films rated: 247
   Average rating: 3.85/5

🎭 Favorite Genres: Drama, Crime, Thriller
🎬 Favorite Directors: Christopher Nolan, Martin Scorsese, Quentin Tarantino
⭐ Favorite Actors: Leonardo DiCaprio, Tom Hanks, Morgan Freeman

============================================================
TOP 10 RECOMMENDED MOVIES
============================================================

1. The Godfather Part II (1974)
   ⭐ Community Rating: 4.5/5
   🎭 Genres: Crime, Drama
   🎬 Director: Francis Ford Coppola
   💡 Why: Genres you love: Crime, Drama
       High community rating: 4.5/5
   🔗 https://letterboxd.com/film/the-godfather-part-ii/

...
```

## Configuration

You can customize the recommendation behavior:

```python
# Change number of recommendations
recommendations = generate_recommendations('username', top_n=20)

# Include already-rated films
recommender = MovieRecommender(films_data)
recommendations = recommender.get_hybrid_recommendations(
    top_n=10, 
    exclude_rated=False
)

# Get content-based recommendations for a specific film
film_index = 0  # Index of the film in your dataset
similar_films = recommender.get_content_based_recommendations(
    film_index, 
    top_n=5
)
```

## Testing

Run the test suite to verify the system works correctly:

```bash
python test_recommender.py
```

This creates sample data and tests all components of the recommendation system.

## Technical Details

### Algorithms Used

- **TF-IDF Vectorization**: Converts text features into numerical vectors
- **Cosine Similarity**: Measures similarity between film content
- **MinMax Scaling**: Normalizes scores to [0, 1] range
- **Weighted Hybrid Scoring**: Combines multiple signals

### Performance

- Handles datasets of 1000+ films efficiently
- Real-time recommendations (<5 seconds for typical datasets)
- Memory efficient with sparse matrix representations

### Limitations

- Requires at least a few rated films for personalized recommendations
- Cold start: New users without ratings get generic recommendations
- Limited to films in your scraped dataset
- No collaborative filtering (doesn't use other users' data)

## Troubleshooting

**No recommendations generated?**
- Ensure you have rated at least 3-5 films
- Check that your data files exist (run the scraper first)
- Verify packages are installed: `pip list | grep -i "scikit-learn\|pandas\|numpy"`

**All recommendations are the same?**
- Rate more diverse films to improve preference detection
- The system learns from your rating patterns

**Import errors?**
- Reinstall packages: `pip install -r requirements.txt`
- Check Python version: Requires Python 3.8+

## Future Enhancements

Possible improvements:
- Collaborative filtering using similar users
- Deep learning models (neural collaborative filtering)
- Temporal dynamics (preferences changing over time)
- Diversity promotion to avoid echo chambers
- Integration with TMDB/IMDB for expanded metadata

## Credits

Built with:
- scikit-learn for machine learning
- pandas for data manipulation
- numpy for numerical computing

## License

Part of the LetterboxdNew project.
