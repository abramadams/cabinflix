#!/usr/bin/env python3
"""
Remove unenriched movies that are duplicates of enriched movies
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

def remove_unenriched_duplicates():
    """Remove unenriched movies that are duplicates of enriched movies"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🧹 Removing unenriched duplicates...")
        print("=" * 50)
        
        # Define the duplicates to remove
        duplicates_to_remove = [
            ("Lone Ranger", "Lone Ranger, The"),
            ("Baurne Legacy, The", "Bourne Legacy, The"),
            ("Maze Runner, The", "The Maze Runner")
        ]
        
        removed_count = 0
        
        for unenriched_title, enriched_title in duplicates_to_remove:
            print(f"🔍 Checking: {unenriched_title} vs {enriched_title}")
            
            # Check if the enriched version exists
            cursor.execute("SELECT id, tmdb_id FROM movies WHERE title = %s", (enriched_title,))
            enriched_result = cursor.fetchone()
            
            if enriched_result and enriched_result[1]:  # Has TMDB ID
                # Check if the unenriched version exists
                cursor.execute("SELECT id FROM movies WHERE title = %s AND tmdb_id IS NULL", (unenriched_title,))
                unenriched_result = cursor.fetchone()
                
                if unenriched_result:
                    # Remove the unenriched duplicate
                    cursor.execute("DELETE FROM movies WHERE id = %s", (unenriched_result[0],))
                    removed_count += 1
                    print(f"   ✅ Removed: {unenriched_title} (duplicate of {enriched_title})")
                else:
                    print(f"   ⚠️ {unenriched_title} not found")
            else:
                print(f"   ⚠️ {enriched_title} not found or not enriched")
        
        conn.commit()
        
        print(f"\n📊 Summary:")
        print(f"  Removed {removed_count} unenriched duplicates")
        
        # Show final database status
        cursor.execute("SELECT COUNT(*) FROM movies")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NOT NULL")
        enriched = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM movies WHERE tmdb_id IS NULL")
        unenriched = cursor.fetchone()[0]
        
        print(f"📊 Final database status:")
        print(f"  Total movies: {total}")
        print(f"  Enriched movies: {enriched}")
        print(f"  Unenriched movies: {unenriched}")
        print(f"  Enrichment rate: {enriched/total*100:.1f}%")
        
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
        print(f"❌ Error removing unenriched duplicates: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    remove_unenriched_duplicates()
