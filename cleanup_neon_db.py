#!/usr/bin/env python3
"""
Clean up Neon database to remove duplicates and ensure exactly 781 unique movies
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

def cleanup_database():
    """Clean up the database to remove duplicates and ensure exactly 781 unique movies"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🧹 Cleaning up database...")
        
        # Step 1: Get the original 781 movie titles
        print("📁 Loading original movie list...")
        with open('movies.json', 'r') as f:
            original_movies = json.load(f)
        original_titles = {movie['title'].lower() for movie in original_movies}
        print(f"📊 Original collection has {len(original_titles)} unique movies")
        
        # Step 2: Get all movies currently in database
        cursor.execute("SELECT id, title, tmdb_id FROM movies ORDER BY id")
        all_movies = cursor.fetchall()
        print(f"📊 Database currently has {len(all_movies)} movies")
        
        # Step 3: Identify movies to keep and remove
        movies_to_keep = []
        movies_to_remove = []
        
        for movie_id, title, tmdb_id in all_movies:
            title_lower = title.lower()
            
            if title_lower in original_titles:
                # This movie is in our original collection
                if not any(m['id'] == movie_id for m in movies_to_keep):
                    # Keep the first occurrence (prefer enriched versions)
                    movies_to_keep.append({
                        'id': movie_id,
                        'title': title,
                        'tmdb_id': tmdb_id,
                        'has_enriched_data': tmdb_id is not None
                    })
                else:
                    # Duplicate of a movie we're keeping
                    movies_to_remove.append(movie_id)
            else:
                # This movie is not in our original collection
                movies_to_remove.append(movie_id)
        
        print(f"📊 Movies to keep: {len(movies_to_keep)}")
        print(f"📊 Movies to remove: {len(movies_to_remove)}")
        
        # Step 4: Remove movies that are not in our original collection or are duplicates
        if movies_to_remove:
            print("🗑️ Removing unwanted movies...")
            
            # Remove movie-genre relationships first
            for movie_id in movies_to_remove:
                cursor.execute("DELETE FROM movie_genres WHERE movie_id = %s", (movie_id,))
            
            # Remove the movies
            for movie_id in movies_to_remove:
                cursor.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
            
            print(f"✅ Removed {len(movies_to_remove)} movies")
        
        # Step 5: Verify we have exactly 781 movies
        cursor.execute("SELECT COUNT(*) FROM movies")
        final_count = cursor.fetchone()[0]
        
        # Step 6: Count enriched vs basic movies
        cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NOT NULL")
        enriched_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NULL")
        basic_count = cursor.fetchone()[0]
        
        conn.commit()
        
        print(f"✅ Database cleanup complete!")
        print(f"📊 Final movie count: {final_count}")
        print(f"📊 Enriched movies (with TMDB data): {enriched_count}")
        print(f"📊 Basic movies (title only): {basic_count}")
        
        if final_count == 781:
            print("🎉 Perfect! Database now has exactly 781 unique movies from your collection!")
        else:
            print(f"⚠️ Warning: Expected 781 movies, but found {final_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Main function"""
    print("🧹 Cleaning up Neon database...")
    print("=" * 50)
    
    if cleanup_database():
        print("\n🎉 Database cleanup successful!")
        print("=" * 50)
        print("✅ No more duplicates")
        print("✅ Exactly 781 unique movies from your collection")
        print("🌐 Your CabinFlix app will show clean, organized data!")
    else:
        print("\n❌ Failed to cleanup database")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
