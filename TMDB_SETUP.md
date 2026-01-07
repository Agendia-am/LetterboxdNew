# TMDB Integration - Quick Start Guide

## Problem Solved
Your recommendations were showing movies you've already watched! This is because the system only had access to your watched films.

**Solution:** TMDB (The Movie Database) integration fetches thousands of movies you haven't watched yet.

## Setup (2 minutes)

### Step 1: Get a Free TMDB API Key

1. Go to [themoviedb.org/signup](https://www.themoviedb.org/signup)
2. Create a free account
3. Go to [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
4. Click "Request an API Key"
5. Choose "Developer" option
6. Fill out the form (use any website, like "https://letterboxd.com")
7. Copy your **API Key (v3 auth)**

### Step 2: Configure the System

```bash
python setup_tmdb_recommendations.py
```

Paste your API key when prompted. Done!

## How It Works Now

### Before (❌ Problem):
```
Your Watched Films (500) → Recommendations from these 500 → You've seen them all!
```

### After (✅ Fixed):
```
Your Watched Films (500) → Learn your taste
      +
TMDB Database (500+ movies) → Recommendations from UNWATCHED films
      ↓
Top 10 movies you HAVEN'T seen!
```

## Usage

```bash
# Generate recommendations (now with unwatched films!)
python movie_recommender.py your_username

# It will:
# 1. Load your watched films (to learn your taste)
# 2. Fetch 500+ movies from TMDB
# 3. Filter out movies you've already watched
# 4. Recommend top 10 unwatched films
```

## What Gets Recommended

✅ **Movies you haven't watched**
✅ **Based on your favorite genres, directors, actors**
✅ **Highly-rated by the community**
✅ **Similar to films you loved**

❌ **Movies you've already watched** (automatically excluded)

## Example Output

```
============================================================
TOP 10 RECOMMENDED MOVIES
============================================================

1. Parasite (2019)
   ⭐ Community Rating: 4.3/5
   🎭 Genres: Drama, Thriller
   🎬 Director: Bong Joon Ho
   💡 Why: Genres you love: Drama, Thriller
       High community rating: 4.3/5
   🔗 https://letterboxd.com/film/parasite-2019/
```

## Configuration

The system fetches 500 movies by default. You can adjust this:

```python
from movie_recommender import generate_recommendations

# Fetch more movies for better variety
recommendations = generate_recommendations('username', 
                                          top_n=10, 
                                          use_tmdb=True,
                                          tmdb_movie_count=1000)
```

## Troubleshooting

**"Invalid API key"**
- Make sure you copied the v3 API Key, not the v4 token
- Check there are no extra spaces

**"Already watched" still appearing**
- The system matches by exact title
- Some titles might have slight variations
- Report these and I can improve the matching

**Want to use without TMDB?**
```python
# Disable TMDB (not recommended - will recommend watched films)
recommendations = generate_recommendations('username', use_tmdb=False)
```

## Files Added

- `tmdb_integration.py` - TMDB API client
- `setup_tmdb_recommendations.py` - Easy setup script
- Updated `movie_recommender.py` - Now uses TMDB

## Cost

**FREE!** TMDB API is completely free for non-commercial use.
- Rate limit: 40 requests per 10 seconds (plenty for our use)
- No credit card required

---

Now your recommendations will be movies you actually **haven't watched yet**! 🎬
