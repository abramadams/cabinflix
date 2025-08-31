import json
import psycopg2
import os
from typing import List, Dict

def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="cabinflix",
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def clean_value(value):
    """Clean and validate values for database insertion"""
    if value == "" or value is None:
        return None
    return value

def import_movies_to_database(movies_file: str = "enriched_movies.json"):
    """Import enriched movies into PostgreSQL database"""
    
    # Load enriched movies
    print(f"Loading movies from {movies_file}...")
    with open(movies_file, 'r') as f:
        movies = json.load(f)
    
    print(f"Found {len(movies)} movies to import")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing movie data...")
        cursor.execute("DELETE FROM movie_genres")
        cursor.execute("DELETE FROM movies")
        
        # Reset sequences
        cursor.execute("ALTER SEQUENCE movies_id_seq RESTART WITH 1")
        
        # Import movies
        print("Importing movies...")
        imported_count = 0
        for i, movie in enumerate(movies, 1):
            if i % 50 == 0:
                print(f"Processed {i}/{len(movies)} movies...")
            
            # Clean and validate values
            release_date = clean_value(movie.get('release_date'))
            runtime = clean_value(movie.get('runtime'))
            vote_average = clean_value(movie.get('vote_average'))
            vote_count = clean_value(movie.get('vote_count'))
            popularity = clean_value(movie.get('popularity'))
            
            # Insert movie data
            cursor.execute("""
                INSERT INTO movies (
                    title, original_title, tmdb_id, release_date, runtime, overview,
                    poster_path, backdrop_path, vote_average, vote_count, popularity, trailer_url, rating
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (tmdb_id) DO UPDATE SET
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
                clean_value(movie.get('title')),
                clean_value(movie.get('original_title')),
                clean_value(movie.get('tmdb_id')),
                clean_value(movie.get('release_date')),
                clean_value(movie.get('runtime')),
                clean_value(movie.get('overview')),
                clean_value(movie.get('poster_path')),
                clean_value(movie.get('backdrop_path')),
                clean_value(movie.get('vote_average')),
                clean_value(movie.get('vote_count')),
                clean_value(movie.get('popularity')),
                clean_value(movie.get('trailer_url')),
                clean_value(movie.get('rating'))
            ))
            
            movie_id = cursor.fetchone()[0]
            imported_count += 1
            
            # Insert genres
            if movie.get('genres'):
                for genre_name in movie['genres']:
                    # Get or create genre
                    cursor.execute("SELECT id FROM genres WHERE name = %s", (genre_name,))
                    result = cursor.fetchone()
                    
                    if result:
                        genre_id = result[0]
                    else:
                        cursor.execute("INSERT INTO genres (name) VALUES (%s) RETURNING id", (genre_name,))
                        genre_id = cursor.fetchone()[0]
                    
                    # Link movie to genre
                    cursor.execute("""
                        INSERT INTO movie_genres (movie_id, genre_id)
                        VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, (movie_id, genre_id))
        
        # Commit changes
        conn.commit()
        print(f"Successfully imported {imported_count} movies!")
        
        # Print some statistics
        cursor.execute("SELECT COUNT(*) FROM movies")
        movie_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM genres")
        genre_count = cursor.fetchone()[0]
        
        print(f"\nDatabase Statistics:")
        print(f"- Movies: {movie_count}")
        print(f"- Genres: {genre_count}")
        
        return True
        
    except Exception as e:
        print(f"Error importing movies: {e}")
        conn.rollback()
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    success = import_movies_to_database()
    if success:
        print("\n✅ Movie import completed successfully!")
    else:
        print("\n❌ Movie import failed!")
