#!/usr/bin/env python3
"""
Example: Using the Movie Recommender as a Python Module

This script demonstrates how to use the movie_recommender module
programmatically in your own Python code.
"""

from movie_recommender import MovieRecommender, load_user_data, generate_recommendations


def example_1_simple_usage():
    """Example 1: Simple usage - generate recommendations"""
    print("=" * 70)
    print("EXAMPLE 1: Simple Recommendation Generation")
    print("=" * 70)
    
    username = "test_user"  # Replace with actual username
    
    # Generate recommendations (all-in-one function)
    recommendations = generate_recommendations(username, top_n=5)
    
    if recommendations:
        print(f"\n✅ Got {len(recommendations)} recommendations!")
        for rec in recommendations:
            print(f"  - {rec['title']} (Score: {rec['rec_score']:.3f})")
    else:
        print("\n❌ No recommendations generated")


def example_2_detailed_usage():
    """Example 2: Using the MovieRecommender class directly"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Using MovieRecommender Class")
    print("=" * 70)
    
    username = "test_user"  # Replace with actual username
    
    # Load data
    films_data = load_user_data(username)
    if not films_data:
        print("❌ No data found")
        return
    
    print(f"\n✅ Loaded {len(films_data)} films")
    
    # Create recommender instance
    recommender = MovieRecommender(films_data)
    
    # Analyze user preferences
    preferences = recommender.analyze_user_preferences()
    if preferences:
        print(f"\n📊 User Profile:")
        print(f"   Total rated: {preferences['total_rated']}")
        print(f"   Avg rating: {preferences['avg_personal_rating']:.2f}/5")
        print(f"   Top genres: {', '.join(preferences['favorite_genres'][:3])}")
        print(f"   Top directors: {', '.join(preferences['favorite_directors'][:3])}")
    
    # Build content features
    print(f"\n🔨 Building content features...")
    recommender.build_content_features()
    print(f"   Matrix shape: {recommender.tfidf_matrix.shape}")
    
    # Get recommendations
    print(f"\n🎬 Generating recommendations...")
    recommendations = recommender.get_hybrid_recommendations(top_n=5, exclude_rated=True)
    
    print(f"\n✅ Top 5 Recommendations:")
    for idx, (_, film) in enumerate(recommendations.iterrows(), 1):
        print(f"   {idx}. {film['title']} (Score: {film['rec_score']:.3f})")


def example_3_content_based():
    """Example 3: Content-based recommendations for a specific film"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Content-Based Recommendations")
    print("=" * 70)
    
    username = "test_user"  # Replace with actual username
    
    # Load data
    films_data = load_user_data(username)
    if not films_data:
        print("❌ No data found")
        return
    
    # Create recommender
    recommender = MovieRecommender(films_data)
    recommender.build_content_features()
    
    # Find similar films to the first film
    seed_film = recommender.df.iloc[0]
    print(f"\n🎯 Finding films similar to: {seed_film['title']}")
    
    similar_films = recommender.get_content_based_recommendations(0, top_n=5)
    
    print(f"\n✅ Similar Films:")
    for idx, (_, film) in enumerate(similar_films.iterrows(), 1):
        print(f"   {idx}. {film['title']}")
        if film.get('genres'):
            print(f"      Genres: {', '.join(film['genres'][:3])}")


def example_4_custom_scoring():
    """Example 4: Access recommendation scores and explanations"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Custom Analysis and Scoring")
    print("=" * 70)
    
    username = "test_user"  # Replace with actual username
    
    # Load data
    films_data = load_user_data(username)
    if not films_data:
        print("❌ No data found")
        return
    
    # Create recommender
    recommender = MovieRecommender(films_data)
    preferences = recommender.analyze_user_preferences()
    
    # Get recommendations with all scores
    recommendations = recommender.get_hybrid_recommendations(top_n=3, exclude_rated=True)
    
    print(f"\n📊 Detailed Scoring Breakdown:")
    for idx, (_, film) in enumerate(recommendations.iterrows(), 1):
        print(f"\n{idx}. {film['title']}")
        print(f"   Final Score: {film.get('rec_score', 0):.3f}")
        print(f"   Rating Score: {film.get('rating_score', 0):.3f}")
        print(f"   Content Similarity: {film.get('content_sim_score', 0):.3f}")
        print(f"   Genre Match: {film.get('genre_match_score', 0):.3f}")
        print(f"   Director Match: {film.get('director_match_score', 0):.3f}")
        
        # Get explanation
        reasons = recommender.explain_recommendation(film, preferences)
        print(f"   Reasons: {'; '.join(reasons)}")


def example_5_batch_processing():
    """Example 5: Process multiple users"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Batch Processing Multiple Users")
    print("=" * 70)
    
    import os
    
    # Find all user data files
    json_files = [f for f in os.listdir('.') if f.endswith('_films_minimal.json')]
    
    if not json_files:
        print("❌ No data files found")
        return
    
    print(f"\n📂 Found {len(json_files)} data files")
    
    # Process each user
    results = {}
    for json_file in json_files[:3]:  # Process first 3
        username = json_file.replace('_films_minimal.json', '')
        print(f"\n🎬 Processing: {username}")
        
        try:
            films_data = load_user_data(username)
            if films_data:
                recommender = MovieRecommender(films_data)
                recommendations = recommender.get_hybrid_recommendations(top_n=3, exclude_rated=True)
                
                top_rec = recommendations.iloc[0] if len(recommendations) > 0 else None
                if top_rec is not None:
                    results[username] = {
                        'top_recommendation': top_rec['title'],
                        'score': top_rec.get('rec_score', 0),
                        'total_films': len(films_data)
                    }
                    print(f"   ✅ Top rec: {top_rec['title']} (score: {top_rec.get('rec_score', 0):.3f})")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Processed: {len(results)} users")
    for user, data in results.items():
        print(f"   {user}: {data['total_films']} films → recommends '{data['top_recommendation']}'")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("MOVIE RECOMMENDER - PROGRAMMING EXAMPLES")
    print("=" * 70)
    
    import os
    
    # Check if test data exists
    if not os.path.exists('test_user_films_minimal.json'):
        print("\n⚠️  No test data found. Creating sample data...")
        # Run test to create sample data
        import test_recommender
        sample_films = test_recommender.create_sample_data()
        import json
        with open('test_user_films_minimal.json', 'w') as f:
            json.dump(sample_films, f)
        print("✅ Sample data created")
    
    try:
        # Run examples
        example_1_simple_usage()
        example_2_detailed_usage()
        example_3_content_based()
        example_4_custom_scoring()
        # example_5_batch_processing()  # Uncomment if you have multiple users
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
