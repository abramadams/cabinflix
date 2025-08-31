#!/usr/bin/env python3
"""
Check for movies with 1969 release dates and investigate the issue
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

def check_1969_movies():
    """Check for movies with 1969 release dates"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check for movies with 1969 release dates
        cursor.execute("""
            SELECT id, title, release_date, tmdb_id 
            FROM movies 
            WHERE EXTRACT(YEAR FROM release_date) = 1969
            ORDER BY title
        """)
        
        movies_1969 = cursor.fetchall()
        print(f"📊 Found {len(movies_1969)} movies with 1969 release dates:")
        
        for movie_id, title, release_date, tmdb_id in movies_1969:
            has_tmdb = "✅" if tmdb_id else "❌"
            print(f"  {has_tmdb} {title} (ID: {movie_id}, TMDB: {tmdb_id}, Date: {release_date})")
        
        # Check for movies with NULL release dates
        cursor.execute("""
            SELECT COUNT(*) 
            FROM movies 
            WHERE release_date IS NULL
        """)
        
        null_count = cursor.fetchone()[0]
        print(f"\n📊 Movies with NULL release dates: {null_count}")
        
        # Check for movies with empty strings or invalid dates
        cursor.execute("""
            SELECT id, title, release_date, tmdb_id 
            FROM movies 
            WHERE release_date IS NOT NULL 
            AND EXTRACT(YEAR FROM release_date) < 1900
            ORDER BY release_date
        """)
        
        invalid_dates = cursor.fetchall()
        print(f"\n📊 Movies with invalid dates (< 1900): {len(invalid_dates)}")
        
        for movie_id, title, release_date, tmdb_id in invalid_dates:
            has_tmdb = "✅" if tmdb_id else "❌"
            print(f"  {has_tmdb} {title} (ID: {movie_id}, TMDB: {tmdb_id}, Date: {release_date})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking movies: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_1969_movies()
