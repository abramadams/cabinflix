#!/usr/bin/env python3
"""
Synchronize remote database with current local database data
"""

import json
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not found in .env file")
    exit(1)

def connect_to_database():
    """Connect to the database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def sync_remote_database():
    """Synchronize remote database with current data"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🔄 Synchronizing remote database...")
        print("=" * 50)
        
        # Check if current_database_export.json exists
        if not os.path.exists('current_database_export.json'):
            print("❌ current_database_export.json not found. Run deploy_with_db_update.sh first.")
            return False
        
        # Load the exported data
        with open('current_database_export.json', 'r') as f:
            exported_movies = json.load(f)
        
        print(f"📊 Loaded {len(exported_movies)} movies from export")
        
        # Get current database state
        cursor.execute("SELECT COUNT(*) FROM movies")
        current_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NOT NULL")
        current_enriched = cursor.fetchone()[0]
        
        print(f"📊 Current database: {current_enriched}/{current_total} movies enriched")
        
        # Check if we need to update
        if len(exported_movies) == current_total:
            print("✅ Database is already synchronized")
            return True
        
        print(f"🔄 Database needs update: {len(exported_movies)} movies in export vs {current_total} in database")
        
        # Clear existing data and re-import
        print("🗑️ Clearing existing data...")
        cursor.execute("DELETE FROM movie_genres")
        cursor.execute("DELETE FROM movies")
        
        # Reset sequence
        cursor.execute("ALTER SEQUENCE movies_id_seq RESTART WITH 1")
        
        print("📥 Importing updated data...")
        
        # Import the exported data
        for movie in exported_movies:
            cursor.execute("""
                INSERT INTO movies (
                    title, tmdb_id, release_date, rating, poster_path, 
                    backdrop_path, overview, popularity, vote_average, vote_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                movie['title'],
                movie['tmdb_id'],
                movie['release_date'],
                movie['rating'],
                movie['poster_path'],
                movie['backdrop_path'],
                movie['overview'],
                movie['popularity'],
                movie['vote_average'],
                movie['vote_count']
            ))
        
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT COUNT(*) FROM movies")
        new_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NOT NULL")
        new_enriched = cursor.fetchone()[0]
        
        print(f"✅ Database synchronized!")
        print(f"📊 New database: {new_enriched}/{new_total} movies enriched ({new_enriched/new_total*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error synchronizing database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    sync_remote_database()
