#!/usr/bin/env python3
"""
Quick setup script for TMDB-powered recommendations
"""

from tmdb_integration import setup_tmdb, TMDBClient, fetch_tmdb_movies

def main():
    print("=" * 70)
    print("MOVIE RECOMMENDATION SYSTEM - TMDB SETUP")
    print("=" * 70)
    print("\nThis will enable recommendations for movies you HAVEN'T watched yet!")
    print("\nWithout TMDB, recommendations only work from your watched films.")
    print("With TMDB, you get recommendations from 1000s of unwatched films.")
    
    # Check if already configured
    client = TMDBClient()
    if client.api_key and client.test_connection():
        print("\n✅ TMDB is already configured!")
        print(f"   API key found and working.")
        
        test = input("\nWould you like to test fetching movies? (yes/no): ").strip().lower()
        if test in ['yes', 'y']:
            print("\n🔍 Fetching 20 popular movies as a test...")
            movies = fetch_tmdb_movies(client, count=20)
            if movies:
                print(f"\n✅ Successfully fetched {len(movies)} movies!")
                print("\nSample:")
                for i, movie in enumerate(movies[:5], 1):
                    print(f"  {i}. {movie['title']} ({movie.get('release_date')}) - ⭐ {movie.get('average_rating')}/5")
            else:
                print("\n❌ Failed to fetch movies. Check your API key.")
        
        print("\n✅ Setup complete! You can now use:")
        print("   python movie_recommender.py username")
        return
    
    # Setup new API key
    print("\n" + "=" * 70)
    client = setup_tmdb()
    
    if client:
        print("\n✅ TMDB setup successful!")
        print("\nYou can now generate recommendations with:")
        print("   python movie_recommender.py username")
        print("\nThe system will automatically:")
        print("   • Fetch 500+ movies from TMDB")
        print("   • Filter out movies you've already watched")
        print("   • Recommend top 10 unwatched films based on your taste")
    else:
        print("\n⚠️  TMDB setup was not completed.")
        print("You can still use the recommendation system, but it will only")
        print("recommend from your already-watched films (which isn't very useful).")
        print("\nYou can run this setup again anytime: python setup_tmdb_recommendations.py")


if __name__ == "__main__":
    main()
