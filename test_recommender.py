"""
Test script for the Movie Recommendation System
Creates sample data to demonstrate the recommender
"""

import json
from movie_recommender import MovieRecommender, generate_recommendations


def create_sample_data():
    """Create sample movie data for testing"""
    sample_films = [
        {
            "title": "The Shawshank Redemption",
            "release_date": "1994",
            "genres": ["Drama", "Crime"],
            "directors": ["Frank Darabont"],
            "actors": ["Tim Robbins", "Morgan Freeman", "Bob Gunton"],
            "average_rating": 4.5,
            "personal_rating": 5.0,
            "description": "Two imprisoned men bond over years, finding redemption through compassion.",
            "runtime": "142 mins",
            "url": "https://letterboxd.com/film/the-shawshank-redemption/"
        },
        {
            "title": "The Godfather",
            "release_date": "1972",
            "genres": ["Crime", "Drama"],
            "directors": ["Francis Ford Coppola"],
            "actors": ["Marlon Brando", "Al Pacino", "James Caan"],
            "average_rating": 4.6,
            "personal_rating": 5.0,
            "description": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
            "runtime": "175 mins",
            "url": "https://letterboxd.com/film/the-godfather/"
        },
        {
            "title": "The Dark Knight",
            "release_date": "2008",
            "genres": ["Action", "Crime", "Drama"],
            "directors": ["Christopher Nolan"],
            "actors": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
            "average_rating": 4.3,
            "personal_rating": 4.5,
            "description": "Batman faces the Joker, a criminal mastermind who wants to plunge Gotham into anarchy.",
            "runtime": "152 mins",
            "url": "https://letterboxd.com/film/the-dark-knight/"
        },
        {
            "title": "Pulp Fiction",
            "release_date": "1994",
            "genres": ["Crime", "Drama"],
            "directors": ["Quentin Tarantino"],
            "actors": ["John Travolta", "Samuel L. Jackson", "Uma Thurman"],
            "average_rating": 4.4,
            "personal_rating": 4.5,
            "description": "The lives of two mob hitmen, a boxer, and a pair of diner bandits intertwine.",
            "runtime": "154 mins",
            "url": "https://letterboxd.com/film/pulp-fiction/"
        },
        {
            "title": "Fight Club",
            "release_date": "1999",
            "genres": ["Drama"],
            "directors": ["David Fincher"],
            "actors": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter"],
            "average_rating": 4.2,
            "personal_rating": 4.0,
            "description": "An insomniac office worker forms an underground fight club.",
            "runtime": "139 mins",
            "url": "https://letterboxd.com/film/fight-club/"
        },
        # Films not yet rated (for recommendations)
        {
            "title": "The Godfather Part II",
            "release_date": "1974",
            "genres": ["Crime", "Drama"],
            "directors": ["Francis Ford Coppola"],
            "actors": ["Al Pacino", "Robert De Niro", "Robert Duvall"],
            "average_rating": 4.5,
            "personal_rating": None,
            "description": "The early life and career of Vito Corleone in 1920s New York.",
            "runtime": "202 mins",
            "url": "https://letterboxd.com/film/the-godfather-part-ii/"
        },
        {
            "title": "Goodfellas",
            "release_date": "1990",
            "genres": ["Crime", "Drama"],
            "directors": ["Martin Scorsese"],
            "actors": ["Robert De Niro", "Ray Liotta", "Joe Pesci"],
            "average_rating": 4.4,
            "personal_rating": None,
            "description": "The story of Henry Hill and his life in the mob.",
            "runtime": "145 mins",
            "url": "https://letterboxd.com/film/goodfellas/"
        },
        {
            "title": "Inception",
            "release_date": "2010",
            "genres": ["Action", "Sci-Fi", "Thriller"],
            "directors": ["Christopher Nolan"],
            "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"],
            "average_rating": 4.2,
            "personal_rating": None,
            "description": "A thief who steals corporate secrets through dream-sharing technology.",
            "runtime": "148 mins",
            "url": "https://letterboxd.com/film/inception/"
        },
        {
            "title": "The Prestige",
            "release_date": "2006",
            "genres": ["Drama", "Mystery", "Sci-Fi"],
            "directors": ["Christopher Nolan"],
            "actors": ["Christian Bale", "Hugh Jackman", "Scarlett Johansson"],
            "average_rating": 4.1,
            "personal_rating": None,
            "description": "Two magicians engage in a bitter rivalry.",
            "runtime": "130 mins",
            "url": "https://letterboxd.com/film/the-prestige/"
        },
        {
            "title": "Casino",
            "release_date": "1995",
            "genres": ["Crime", "Drama"],
            "directors": ["Martin Scorsese"],
            "actors": ["Robert De Niro", "Sharon Stone", "Joe Pesci"],
            "average_rating": 4.2,
            "personal_rating": None,
            "description": "A tale of greed, deception, money, power, and murder.",
            "runtime": "178 mins",
            "url": "https://letterboxd.com/film/casino/"
        },
        {
            "title": "The Departed",
            "release_date": "2006",
            "genres": ["Crime", "Drama", "Thriller"],
            "directors": ["Martin Scorsese"],
            "actors": ["Leonardo DiCaprio", "Matt Damon", "Jack Nicholson"],
            "average_rating": 4.1,
            "personal_rating": None,
            "description": "An undercover cop and a mole in the police attempt to identify each other.",
            "runtime": "151 mins",
            "url": "https://letterboxd.com/film/the-departed/"
        },
        {
            "title": "Se7en",
            "release_date": "1995",
            "genres": ["Crime", "Mystery", "Thriller"],
            "directors": ["David Fincher"],
            "actors": ["Brad Pitt", "Morgan Freeman", "Kevin Spacey"],
            "average_rating": 4.3,
            "personal_rating": None,
            "description": "Two detectives hunt a serial killer who uses the seven deadly sins as his motives.",
            "runtime": "127 mins",
            "url": "https://letterboxd.com/film/se7en/"
        },
        {
            "title": "Zodiac",
            "release_date": "2007",
            "genres": ["Crime", "Drama", "Mystery"],
            "directors": ["David Fincher"],
            "actors": ["Jake Gyllenhaal", "Robert Downey Jr.", "Mark Ruffalo"],
            "average_rating": 4.0,
            "personal_rating": None,
            "description": "A San Francisco cartoonist becomes an amateur detective obsessed with tracking down the Zodiac Killer.",
            "runtime": "157 mins",
            "url": "https://letterboxd.com/film/zodiac/"
        },
        {
            "title": "Memento",
            "release_date": "2000",
            "genres": ["Mystery", "Thriller"],
            "directors": ["Christopher Nolan"],
            "actors": ["Guy Pearce", "Carrie-Anne Moss", "Joe Pantoliano"],
            "average_rating": 4.2,
            "personal_rating": None,
            "description": "A man with short-term memory loss attempts to track down his wife's murderer.",
            "runtime": "113 mins",
            "url": "https://letterboxd.com/film/memento/"
        },
        {
            "title": "Reservoir Dogs",
            "release_date": "1992",
            "genres": ["Crime", "Thriller"],
            "directors": ["Quentin Tarantino"],
            "actors": ["Harvey Keitel", "Tim Roth", "Steve Buscemi"],
            "average_rating": 4.1,
            "personal_rating": None,
            "description": "After a heist goes wrong, a group of criminals suspects one of them is a police informer.",
            "runtime": "99 mins",
            "url": "https://letterboxd.com/film/reservoir-dogs/"
        }
    ]
    
    return sample_films


def test_recommender():
    """Test the recommendation system with sample data"""
    print("=" * 70)
    print("MOVIE RECOMMENDATION SYSTEM - TEST MODE")
    print("=" * 70)
    
    # Create sample data
    sample_films = create_sample_data()
    
    # Save to test file
    test_username = "test_user"
    with open(f'{test_username}_films_minimal.json', 'w', encoding='utf-8') as f:
        json.dump(sample_films, f, indent=2, ensure_ascii=False)
    
    print(f"\nCreated test data with {len(sample_films)} films")
    print(f"- {sum(1 for f in sample_films if f['personal_rating'])} films rated")
    print(f"- {sum(1 for f in sample_films if not f['personal_rating'])} films unrated")
    
    # Test the recommender
    print("\n" + "=" * 70)
    print("Testing MovieRecommender class...")
    print("=" * 70)
    
    recommender = MovieRecommender(sample_films)
    
    # Test preference analysis
    print("\n1. Analyzing user preferences...")
    preferences = recommender.analyze_user_preferences()
    if preferences:
        print(f"   ✓ Analyzed {preferences['total_rated']} rated films")
        print(f"   ✓ Favorite genres: {', '.join(preferences['favorite_genres'][:3])}")
        print(f"   ✓ Favorite directors: {', '.join(preferences['favorite_directors'][:3])}")
    
    # Test content features
    print("\n2. Building content features...")
    recommender.build_content_features()
    print(f"   ✓ Built TF-IDF matrix with shape: {recommender.tfidf_matrix.shape}")
    print(f"   ✓ Computed similarity matrix: {recommender.content_similarity.shape}")
    
    # Test content-based recommendations
    print("\n3. Testing content-based recommendations...")
    content_recs = recommender.get_content_based_recommendations(0, top_n=3)
    print(f"   ✓ Found {len(content_recs)} similar films to '{sample_films[0]['title']}'")
    for idx, (_, film) in enumerate(content_recs.iterrows(), 1):
        print(f"      {idx}. {film['title']} ({film.get('year', 'N/A')})")
    
    # Test hybrid recommendations
    print("\n4. Testing hybrid recommendations...")
    hybrid_recs = recommender.get_hybrid_recommendations(top_n=5, exclude_rated=True)
    print(f"   ✓ Generated {len(hybrid_recs)} recommendations")
    for idx, (_, film) in enumerate(hybrid_recs.iterrows(), 1):
        print(f"      {idx}. {film['title']} (Score: {film.get('rec_score', 0):.3f})")
    
    # Test full recommendation generation
    print("\n" + "=" * 70)
    print("Testing complete recommendation pipeline...")
    print("=" * 70)
    
    recommendations = generate_recommendations(test_username, top_n=10)
    
    if recommendations:
        print(f"\n✅ SUCCESS! Generated {len(recommendations)} recommendations")
        print("\nTest passed! The recommendation system is working correctly.")
    else:
        print("\n❌ FAILED! Could not generate recommendations")
    
    # Cleanup test file
    import os
    try:
        os.remove(f'{test_username}_films_minimal.json')
        if os.path.exists(f'{test_username}_recommendations.json'):
            print(f"\n📄 Test recommendations saved to '{test_username}_recommendations.json'")
    except:
        pass
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_recommender()
