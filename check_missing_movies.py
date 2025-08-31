#!/usr/bin/env python3
"""
Check which movies are missing from the database
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
    """Connect to the Neon database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def check_missing_movies():
    """Check which movies are missing from the database"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get original movie list
        with open('movies.json', 'r') as f:
            original_movies = json.load(f)
        original_titles = {movie['title'].lower() for movie in original_movies}
        print(f"📊 Original movies: {len(original_titles)}")
        
        # Get movies in database
        cursor.execute("SELECT title FROM movies")
        db_movies = cursor.fetchall()
        db_titles = {row[0].lower() for row in db_movies}
        print(f"📊 Database movies: {len(db_titles)}")
        
        # Find missing movies
        missing_movies = original_titles - db_titles
        print(f"📊 Missing movies: {len(missing_movies)}")
        
        if missing_movies:
            print("\n🔍 Missing movies:")
            for title in sorted(missing_movies):
                print(f"  - {title}")
        
        # Find extra movies in database
        extra_movies = db_titles - original_titles
        if extra_movies:
            print(f"\n📊 Extra movies in database: {len(extra_movies)}")
            for title in sorted(extra_movies):
                print(f"  - {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking movies: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    check_missing_movies()
