#!/usr/bin/env python3
"""
Fix obvious title matches and split collections into individual movies
"""

import json
import os
import psycopg2
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not found in .env file")
    exit(1)

if not TMDB_API_KEY:
    print("❌ Error: TMDB_API_KEY not found in .env file")
    exit(1)

def connect_to_database():
    """Connect to the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def search_tmdb_movie(title):
    """Search for a movie on TMDB"""
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'language': 'en-US',
            'page': 1,
            'include_adult': False
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data['results']:
            return data['results'][0]
        return None
    except Exception as e:
        print(f"❌ Error searching TMDB for '{title}': {e}")
        return None

def get_movie_details(tmdb_id):
    """Get detailed movie information from TMDB"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {
            'api_key': TMDB_API_KEY,
            'append_to_response': 'release_dates'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"❌ Error getting movie details for TMDB ID {tmdb_id}: {e}")
        return None

def fix_obvious_matches():
    """Fix obvious title matches and split collections"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🔧 Fixing obvious title matches...")
        print("=" * 60)
        
        # Get all movies without TMDB data
        cursor.execute("""
            SELECT id, title 
            FROM movies 
            WHERE tmdb_id IS NULL 
            ORDER BY title
        """)
        
        unenriched_movies = cursor.fetchall()
        
        # Obvious corrections that should work
        obvious_corrections = {
            "Davinci Cope, The": "The Da Vinci Code",
            "Did You Here About The Morgans": "Did You Hear About the Morgans?",
            "Dumb & Dumber two": "Dumb and Dumber To",
            "Exract": "Extract",
            "Fantastic 4: Rise of the Silver Surfee": "Fantastic Four: Rise of the Silver Surfer",
            "Fast and Furius 6": "Fast & Furious 6",
            "Furry Vengance": "Furry Vengeance",
            "Gabriel Iglesius: Aloha Fluffy": "Gabriel Iglesias: Aloha Fluffy",
            "Ghost of Girlfriends Past": "Ghosts of Girlfriends Past",
            "Good Sheperd, The": "The Good Shepherd",
            "Hallpass": "Hall Pass",
            "Hansel & Gertel Witch Hunters": "Hansel & Gretel: Witch Hunters",
            "Harald & Kumar; Go to Whitecastle": "Harold & Kumar Go to White Castle",
            "Haunting in Coonneticut": "The Haunting in Connecticut",
            "Hunger Games; Mocking Jay pt 1": "The Hunger Games: Mockingjay - Part 1",
            "Incredible Boy Wonderstone": "The Incredible Burt Wonderstone",
            "Inkeepers, The": "The Innkeepers",
            "Mi Vida Luca": "Mi Vida Loca",
            "Mysterous Skin": "Mysterious Skin",
            "Pandrum": "Pandorum",
            "Pirates of the Caribbean; On Stranger Tieds": "Pirates of the Caribbean: On Stranger Tides",
            "Rise of the Palnet of the Apes": "Rise of the Planet of the Apes",
            "Silent HIll; Revalation": "Silent Hill: Revelation",
            "Skool for Scoundrels": "School for Scoundrels",
            "Srawberry Shortcake": "Strawberry Shortcake",
            "Very Harold & Kumar X-Mas, A": "A Very Harold & Kumar Christmas",
            "Wihtout a Paddle": "Without a Paddle",
            "Harry Potter & The Deathly Hallows pt 1": "Harry Potter and the Deathly Hallows: Part 1",
            "Harry Potter & The Deathly Hallows pt 2": "Harry Potter and the Deathly Hallows: Part 2",
            "Iceman, The": "The Iceman",
            "Lone Ranger": "The Lone Ranger",
            "Maze Runner, The": "The Maze Runner",
            "Single Man's Club, The": "The Single Man's Club",
            "Twilight; Breaking Dawn pt 1": "The Twilight Saga: Breaking Dawn - Part 1"
        }
        
        # Collections to split into individual movies
        collections_to_split = {
            "Candy Man 1,2,3": [
                "Candyman",
                "Candyman: Farewell to the Flesh", 
                "Candyman: Day of the Dead"
            ],
            "Cheech & Chong 2": [
                "Cheech & Chong's Next Movie",
                "Cheech & Chong's Nice Dreams"
            ]
        }
        
        fixed_count = 0
        split_count = 0
        
        for movie_id, title in unenriched_movies:
            # Check for obvious corrections
            if title in obvious_corrections:
                corrected_title = obvious_corrections[title]
                print(f"🔧 Fixing: {title} → {corrected_title}")
                
                # Search TMDB for the corrected title
                tmdb_result = search_tmdb_movie(corrected_title)
                if tmdb_result:
                    tmdb_id = tmdb_result['id']
                    
                    # Check if this TMDB ID already exists
                    cursor.execute("SELECT id FROM movies WHERE tmdb_id = %s", (tmdb_id,))
                    existing = cursor.fetchone()
                    if existing:
                        print(f"   ⚠️ TMDB ID {tmdb_id} already exists, skipping")
                        continue
                    
                    # Get detailed movie info
                    details = get_movie_details(tmdb_id)
                    if details:
                        # Extract rating from US release
                        rating = None
                        if 'release_dates' in details and 'results' in details['release_dates']:
                            for country in details['release_dates']['results']:
                                if country['iso_3166_1'] == 'US':
                                    for release in country['release_dates']:
                                        if release['type'] == 3:  # Theatrical release
                                            rating = release.get('certification')
                                            break
                                    break
                        
                        # Update the movie in database
                        cursor.execute("""
                            UPDATE movies 
                            SET tmdb_id = %s, 
                                title = %s,
                                release_date = %s,
                                rating = %s,
                                poster_path = %s,
                                backdrop_path = %s,
                                overview = %s,
                                popularity = %s,
                                vote_average = %s,
                                vote_count = %s
                            WHERE id = %s
                        """, (
                            tmdb_id,
                            corrected_title,
                            details.get('release_date'),
                            rating,
                            details.get('poster_path'),
                            details.get('backdrop_path'),
                            details.get('overview'),
                            details.get('popularity', 0),
                            details.get('vote_average', 0),
                            details.get('vote_count', 0),
                            movie_id
                        ))
                        
                        print(f"   ✅ Updated with TMDB data (ID: {tmdb_id})")
                        fixed_count += 1
                    else:
                        print(f"   ❌ Could not get details for TMDB ID {tmdb_id}")
                else:
                    print(f"   ❌ No TMDB match found for '{corrected_title}'")
            
            # Check for collections to split
            elif title in collections_to_split:
                individual_titles = collections_to_split[title]
                print(f"📦 Splitting collection: {title}")
                
                # Delete the original collection entry
                cursor.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
                
                # Add individual movies
                for i, individual_title in enumerate(individual_titles):
                    print(f"   📝 Adding: {individual_title}")
                    
                    # Search TMDB for individual title
                    tmdb_result = search_tmdb_movie(individual_title)
                    if tmdb_result:
                        tmdb_id = tmdb_result['id']
                        
                        # Check if this TMDB ID already exists
                        cursor.execute("SELECT id FROM movies WHERE tmdb_id = %s", (tmdb_id,))
                        existing = cursor.fetchone()
                        if existing:
                            print(f"      ⚠️ TMDB ID {tmdb_id} already exists, skipping")
                            continue
                        
                        details = get_movie_details(tmdb_id)
                        
                        if details:
                            # Extract rating
                            rating = None
                            if 'release_dates' in details and 'results' in details['release_dates']:
                                for country in details['release_dates']['results']:
                                    if country['iso_3166_1'] == 'US':
                                        for release in country['release_dates']:
                                            if release['type'] == 3:
                                                rating = release.get('certification')
                                                break
                                        break
                            
                            # Insert new movie
                            cursor.execute("""
                                INSERT INTO movies (
                                    title, tmdb_id, release_date, rating, poster_path, 
                                    backdrop_path, overview, popularity, vote_average, vote_count
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                individual_title,
                                tmdb_id,
                                details.get('release_date'),
                                rating,
                                details.get('poster_path'),
                                details.get('backdrop_path'),
                                details.get('overview'),
                                details.get('popularity', 0),
                                details.get('vote_average', 0),
                                details.get('vote_count', 0)
                            ))
                            
                            print(f"      ✅ Added with TMDB data (ID: {tmdb_id})")
                            split_count += 1
                        else:
                            print(f"      ❌ Could not get details for TMDB ID {tmdb_id}")
                    else:
                        print(f"      ❌ No TMDB match found for '{individual_title}'")
        
        conn.commit()
        
        print(f"\n📊 Summary:")
        print(f"  Fixed obvious matches: {fixed_count}")
        print(f"  Split collections: {split_count}")
        
        # Show remaining unmatched movies
        cursor.execute("""
            SELECT title 
            FROM movies 
            WHERE tmdb_id IS NULL 
            ORDER BY title
        """)
        
        remaining = cursor.fetchall()
        print(f"\n❓ Remaining unmatched movies ({len(remaining)}):")
        print("-" * 40)
        
        for i, (title,) in enumerate(remaining, 1):
            print(f"{i:2d}. {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing matches: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_obvious_matches()
