#!/usr/bin/env python3
"""
Quick start guide for the Movie Recommendation System

This script provides a simple interactive interface for generating recommendations.
"""

import os
import sys

def main():
    print("=" * 70)
    print("LETTERBOXD MOVIE RECOMMENDATION SYSTEM")
    print("Quick Start Guide")
    print("=" * 70)
    
    # Check if data exists
    print("\n📂 Checking for existing data files...")
    
    json_files = [f for f in os.listdir('.') if f.endswith('_films_minimal.json') or f.endswith('_detailed_films.json')]
    
    if not json_files:
        print("\n❌ No data files found!")
        print("\nTo use the recommendation system, you need to:")
        print("1. First run the scraper: python LetterboxdNew.py")
        print("2. Enter your Letterboxd username")
        print("3. Wait for scraping to complete")
        print("4. Then run this script again")
        return
    
    print(f"\n✅ Found {len(json_files)} data file(s):")
    for f in json_files:
        print(f"   - {f}")
    
    # Extract usernames
    usernames = []
    for f in json_files:
        if '_films_minimal.json' in f:
            username = f.replace('_films_minimal.json', '')
            usernames.append(username)
        elif '_detailed_films.json' in f:
            username = f.replace('_detailed_films.json', '')
            if username not in usernames:
                usernames.append(username)
    
    if not usernames:
        print("\n❌ Could not extract usernames from files")
        return
    
    # Select username
    if len(usernames) == 1:
        username = usernames[0]
        print(f"\n📋 Using username: {username}")
    else:
        print(f"\n📋 Multiple users found. Select one:")
        for i, u in enumerate(usernames, 1):
            print(f"   {i}. {u}")
        
        while True:
            try:
                choice = input("\nEnter number: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(usernames):
                    username = usernames[idx]
                    break
                else:
                    print("Invalid choice. Try again.")
            except:
                print("Invalid input. Please enter a number.")
    
    # Ask for number of recommendations
    print("\n🔢 How many recommendations would you like?")
    print("   (Default: 10, Max: 50)")
    
    try:
        top_n = input("Enter number (or press Enter for 10): ").strip()
        top_n = int(top_n) if top_n else 10
        top_n = min(max(1, top_n), 50)  # Clamp between 1 and 50
    except:
        top_n = 10
    
    print(f"\n🎬 Generating {top_n} recommendations for {username}...")
    print("=" * 70)
    
    # Generate recommendations
    try:
        from movie_recommender import generate_recommendations
        recommendations = generate_recommendations(username, top_n)
        
        if recommendations:
            print("\n" + "=" * 70)
            print("✅ SUCCESS!")
            print("=" * 70)
            print(f"\nGenerated {len(recommendations)} recommendations")
            print(f"Saved to: {username}_recommendations.json")
            
            # Offer to view in browser
            view = input("\nWould you like to open the Letterboxd pages? (yes/no): ").strip().lower()
            if view in ['yes', 'y']:
                import webbrowser
                for i, rec in enumerate(recommendations[:5], 1):
                    if rec.get('url'):
                        print(f"\nOpening {i}. {rec['title']}...")
                        webbrowser.open(rec['url'])
                        if i < 5:
                            input("Press Enter for next film...")
        else:
            print("\n❌ Could not generate recommendations")
            print("Make sure you have rated some films in your Letterboxd account")
            
    except ImportError:
        print("\n❌ movie_recommender module not found!")
        print("Make sure you're in the correct directory.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Thank you for using the Movie Recommendation System!")
    print("=" * 70)


if __name__ == "__main__":
    main()
