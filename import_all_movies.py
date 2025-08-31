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

def import_all_movies_to_database():
    """Import ALL movies from original list, including those without TMDB data"""
    
    # Load original movies
    print("Loading original movies from movies.json...")
    with open('movies.json', 'r') as f:
        original_movies = json.load(f)
    
    # Load enriched movies (if available)
    enriched_movies = {}
    if os.path.exists('enriched_movies.json'):
        print("Loading enriched movies from enriched_movies.json...")
        with open('enriched_movies.json', 'r') as f:
            enriched_data = json.load(f)
            for movie in enriched_data:
                enriched_movies[movie['title']] = movie
    
    print(f"Found {len(original_movies)} original movies")
    print(f"Found {len(enriched_movies)} enriched movies")
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Clear existing data
        print("Clearing existing movie data...")
        cursor.execute("DELETE FROM movie_genres")
        cursor.execute("DELETE FROM movies")
        
        # Reset sequences
        cursor.execute("ALTER SEQUENCE movies_id_seq RESTART WITH 1")
        
        # Import ALL movies
        print("Importing all movies...")
        imported_count = 0
        enriched_count = 0
        basic_count = 0
        
        for i, original_movie in enumerate(original_movies, 1):
            if i % 50 == 0:
                print(f"Processed {i}/{len(original_movies)} movies...")
            
            title = original_movie['title']
            
            # Check if we have enriched data for this movie
            if title in enriched_movies:
                movie = enriched_movies[title]
                enriched_count += 1
            else:
                # Create basic movie entry without TMDB data
                movie = {
                    'title': title,
                    'original_title': title,
                    'tmdb_id': None,
                    'release_date': None,
                    'runtime': None,
                    'overview': None,
                    'poster_path': None,
                    'backdrop_path': None,
                    'vote_average': None,
                    'vote_count': None,
                    'popularity': None,
                    'trailer_url': None,
                    'rating': None,
                    'genres': []
                }
                basic_count += 1
            
            # Insert movie data
            cursor.execute("""
                INSERT INTO movies (
                    title, original_title, tmdb_id, release_date, runtime, overview,
                    poster_path, backdrop_path, vote_average, vote_count, popularity, trailer_url, rating
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
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
            
            # Insert genres (only for enriched movies)
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
        print(f"- Enriched movies: {enriched_count}")
        print(f"- Basic movies: {basic_count}")
        
        # Print some statistics
        cursor.execute("SELECT COUNT(*) FROM movies")
        movie_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM genres")
        genre_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NOT NULL")
        movies_with_tmdb = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NULL")
        movies_without_tmdb = cursor.fetchone()[0]
        
        print(f"\nDatabase Statistics:")
        print(f"- Total Movies: {movie_count}")
        print(f"- Movies with TMDB data: {movies_with_tmdb}")
        print(f"- Movies without TMDB data: {movies_without_tmdb}")
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
    success = import_all_movies_to_database()
    if success:
        print("\n✅ All movies import completed successfully!")
    else:
        print("\n❌ Movie import failed!")
