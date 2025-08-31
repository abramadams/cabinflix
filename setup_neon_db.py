#!/usr/bin/env python3
import psycopg2
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ Error: DATABASE_URL not found in .env file")
    exit(1)

def connect_to_database():
    """Connect to Neon PostgreSQL database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def setup_database_schema():
    """Set up the database schema"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create genres table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS genres (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create movies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                original_title VARCHAR(255),
                tmdb_id INTEGER UNIQUE,
                release_date DATE,
                runtime INTEGER,
                overview TEXT,
                poster_path VARCHAR(500),
                backdrop_path VARCHAR(500),
                vote_average NUMERIC(3,1),
                vote_count INTEGER,
                popularity NUMERIC(10,2),
                trailer_url VARCHAR(500),
                rating VARCHAR(10),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create movie_genres junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie_genres (
                movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
                genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
                PRIMARY KEY (movie_id, genre_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_title ON movies USING gin(to_tsvector('english', title))")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_tmdb_id ON movies(tmdb_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_popularity ON movies(popularity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_release_date ON movies(release_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_movies_vote_average ON movies(vote_average)")
        
        # Create updated_at trigger function
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        # Create triggers
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_movies_updated_at ON movies;
            CREATE TRIGGER update_movies_updated_at 
                BEFORE UPDATE ON movies 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS update_genres_updated_at ON genres;
            CREATE TRIGGER update_genres_updated_at 
                BEFORE UPDATE ON genres 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
        """)
        
        conn.commit()
        print("✅ Database schema created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def insert_genres():
    """Insert default genres"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Default genres
        genres = [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary',
            'Drama', 'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery',
            'Romance', 'Science Fiction', 'TV Movie', 'Thriller', 'War', 'Western'
        ]
        
        for genre in genres:
            cursor.execute("""
                INSERT INTO genres (name) 
                VALUES (%s) 
                ON CONFLICT (name) DO NOTHING
            """, (genre,))
        
        conn.commit()
        print(f"✅ Inserted {len(genres)} genres")
        return True
        
    except Exception as e:
        print(f"❌ Error inserting genres: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def import_movies():
    """Import movies from the local database or JSON files"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if we have enriched movies data
        if os.path.exists('enriched_movies.json'):
            print("📁 Found enriched_movies.json, importing enriched data...")
            with open('enriched_movies.json', 'r') as f:
                movies_data = json.load(f)
        elif os.path.exists('movies.json'):
            print("📁 Found movies.json, importing basic data...")
            with open('movies.json', 'r') as f:
                movies_data = [{'title': movie['title']} for movie in json.load(f)]
        else:
            print("❌ No movie data files found. Please run extract_movies.py first.")
            return False
        
        print(f"📊 Importing {len(movies_data)} movies...")
        
        for i, movie in enumerate(movies_data, 1):
            # Insert movie
            # Clean up data values
            release_date = movie.get('release_date')
            if release_date == '' or release_date is None:
                release_date = None
            
            tmdb_id = movie.get('tmdb_id')
            if tmdb_id == '' or tmdb_id is None:
                tmdb_id = None
            
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
                movie.get('title'),
                movie.get('original_title'),
                tmdb_id,
                release_date,
                movie.get('runtime'),
                movie.get('overview'),
                movie.get('poster_path'),
                movie.get('backdrop_path'),
                movie.get('vote_average'),
                movie.get('vote_count'),
                movie.get('popularity'),
                movie.get('trailer_url'),
                movie.get('rating')
            ))
            
            movie_id = cursor.fetchone()[0]
            
            # Insert genres if available
            if movie.get('genres'):
                for genre_name in movie['genres']:
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
            
            if i % 50 == 0:
                print(f"   Progress: {i}/{len(movies_data)} movies imported")
                conn.commit()
        
        conn.commit()
        print(f"✅ Successfully imported {len(movies_data)} movies")
        return True
        
    except Exception as e:
        print(f"❌ Error importing movies: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Main setup function"""
    print("🚀 Setting up Neon database for CabinFlix...")
    print("=" * 50)
    
    # Step 1: Set up schema
    print("\n1️⃣ Setting up database schema...")
    if not setup_database_schema():
        print("❌ Failed to set up schema")
        return
    
    # Step 2: Insert genres
    print("\n2️⃣ Inserting genres...")
    if not insert_genres():
        print("❌ Failed to insert genres")
        return
    
    # Step 3: Import movies
    print("\n3️⃣ Importing movies...")
    if not import_movies():
        print("❌ Failed to import movies")
        return
    
    print("\n🎉 Database setup complete!")
    print("=" * 50)
    print("✅ Schema created")
    print("✅ Genres inserted")
    print("✅ Movies imported")
    print("\n🌐 Your CabinFlix app is ready for deployment!")

if __name__ == "__main__":
    main()
