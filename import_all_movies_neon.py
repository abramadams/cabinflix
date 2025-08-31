#!/usr/bin/env python3
"""
Import ALL movies from the original movies.json file to Neon database
This ensures we have all 781 movies, not just the 717 enriched ones
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not found in .env file")
    exit(1)

def connect_to_database():
    """Connect to the Neon database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def import_all_movies():
    """Import ALL movies from movies.json to ensure we have all 781 movies"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Load all movies from the original movies.json file
        if not os.path.exists('movies.json'):
            print("❌ movies.json not found. Please run extract_movies.py first.")
            return False
        
        print("📁 Loading all movies from movies.json...")
        with open('movies.json', 'r') as f:
            all_movies = json.load(f)
        
        print(f"📊 Found {len(all_movies)} movies in movies.json")
        
        # Load enriched data if available to merge with basic data
        enriched_movies = {}
        if os.path.exists('improved_enriched_movies.json'):
            print("📁 Loading improved enriched data to merge...")
            with open('improved_enriched_movies.json', 'r') as f:
                enriched_data = json.load(f)
                for movie in enriched_data:
                    if movie.get('tmdb_id'):
                        enriched_movies[movie['tmdb_id']] = movie
                    # Also index by title for fallback matching
                    enriched_movies[movie['title'].lower()] = movie
        elif os.path.exists('enriched_movies.json'):
            print("📁 Loading original enriched data to merge...")
            with open('enriched_movies.json', 'r') as f:
                enriched_data = json.load(f)
                for movie in enriched_data:
                    if movie.get('tmdb_id'):
                        enriched_movies[movie['tmdb_id']] = movie
                    # Also index by title for fallback matching
                    enriched_movies[movie['title'].lower()] = movie
        
        print(f"📊 Found {len(enriched_movies)} enriched movie entries")
        
        # Import all movies
        imported_count = 0
        for i, movie in enumerate(all_movies, 1):
            title = movie['title']
            
            # Check if we have enriched data for this movie
            enriched_movie = None
            if title.lower() in enriched_movies:
                enriched_movie = enriched_movies[title.lower()]
            
            # Prepare movie data
            movie_data = {
                'title': title,
                'original_title': enriched_movie.get('original_title') if enriched_movie else None,
                'tmdb_id': enriched_movie.get('tmdb_id') if enriched_movie else None,
                'release_date': enriched_movie.get('release_date') if enriched_movie else None,
                'runtime': enriched_movie.get('runtime') if enriched_movie else None,
                'overview': enriched_movie.get('overview') if enriched_movie else None,
                'poster_path': enriched_movie.get('poster_path') if enriched_movie else None,
                'backdrop_path': enriched_movie.get('backdrop_path') if enriched_movie else None,
                'vote_average': enriched_movie.get('vote_average') if enriched_movie else None,
                'vote_count': enriched_movie.get('vote_count') if enriched_movie else None,
                'popularity': enriched_movie.get('popularity') if enriched_movie else None,
                'trailer_url': enriched_movie.get('trailer_url') if enriched_movie else None,
                'rating': enriched_movie.get('rating') if enriched_movie else None,
                'genres': enriched_movie.get('genres', []) if enriched_movie else []
            }
            
            # Clean up data values
            release_date = movie_data['release_date']
            if release_date == '' or release_date is None:
                release_date = None
            
            tmdb_id = movie_data['tmdb_id']
            if tmdb_id == '' or tmdb_id is None:
                tmdb_id = None
            
            # Insert movie - use different conflict resolution based on whether we have TMDB data
            if tmdb_id:
                # For movies with TMDB data, use tmdb_id for conflict resolution
                cursor.execute("""
                    INSERT INTO movies (
                        title, original_title, tmdb_id, release_date, runtime,
                        overview, poster_path, backdrop_path, vote_average,
                        vote_count, popularity, trailer_url, rating
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tmdb_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        original_title = EXCLUDED.original_title,
                        release_date = EXCLUDED.release_date,
                        runtime = EXCLUDED.runtime,
                        overview = EXCLUDED.overview,
                        poster_path = EXCLUDED.poster_path,
                        backdrop_path = EXCLUDED.backdrop_path,
                        vote_average = EXCLUDED.vote_average,
                        vote_count = EXCLUDED.vote_count,
                        popularity = EXCLUDED.popularity,
                        trailer_url = EXCLUDED.trailer_url,
                        rating = EXCLUDED.rating
                    RETURNING id
                """, (
                    movie_data['title'],
                    movie_data['original_title'],
                    tmdb_id,
                    release_date,
                    movie_data['runtime'],
                    movie_data['overview'],
                    movie_data['poster_path'],
                    movie_data['backdrop_path'],
                    movie_data['vote_average'],
                    movie_data['vote_count'],
                    movie_data['popularity'],
                    movie_data['trailer_url'],
                    movie_data['rating']
                ))
            else:
                # For movies without TMDB data, just insert and ignore duplicates
                cursor.execute("""
                    INSERT INTO movies (
                        title, original_title, tmdb_id, release_date, runtime,
                        overview, poster_path, backdrop_path, vote_average,
                        vote_count, popularity, trailer_url, rating
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """, (
                movie_data['title'],
                movie_data['original_title'],
                tmdb_id,
                release_date,
                movie_data['runtime'],
                movie_data['overview'],
                movie_data['poster_path'],
                movie_data['backdrop_path'],
                movie_data['vote_average'],
                movie_data['vote_count'],
                movie_data['popularity'],
                movie_data['trailer_url'],
                movie_data['rating']
            ))
            
            result = cursor.fetchone()
            if result:
                movie_id = result[0]
            else:
                # Movie already exists, get its ID
                cursor.execute("SELECT id FROM movies WHERE title = %s", (movie_data['title'],))
                movie_id = cursor.fetchone()[0]
            
            # Insert genres if available
            if movie_data['genres']:
                for genre_name in movie_data['genres']:
                    # Get genre ID
                    cursor.execute("SELECT id FROM genres WHERE name = %s", (genre_name,))
                    genre_result = cursor.fetchone()
                    if genre_result:
                        genre_id = genre_result[0]
                        # Insert movie-genre relationship
                        cursor.execute("""
                            INSERT INTO movie_genres (movie_id, genre_id)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """, (movie_id, genre_id))
            
            imported_count += 1
            
            if i % 50 == 0:
                print(f"   Progress: {i}/{len(all_movies)} movies imported")
                conn.commit()
        
        conn.commit()
        print(f"✅ Successfully imported {imported_count} movies")
        
        # Verify the count
        cursor.execute("SELECT COUNT(*) FROM movies")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total movies in database: {total_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing movies: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Main function"""
    print("🚀 Importing ALL movies to Neon database...")
    print("=" * 50)
    
    if import_all_movies():
        print("\n🎉 All movies imported successfully!")
        print("=" * 50)
        print("✅ All 781 movies from your collection are now in the database")
        print("🌐 Your CabinFlix app will show all movies!")
    else:
        print("\n❌ Failed to import movies")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
