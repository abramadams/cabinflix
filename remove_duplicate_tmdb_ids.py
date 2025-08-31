#!/usr/bin/env python3
"""
Remove movies where the TMDB ID already exists elsewhere in the database
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

def remove_duplicate_tmdb_ids():
    """Remove movies where TMDB ID already exists"""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🧹 Removing duplicate TMDB IDs...")
        print("=" * 50)
        
        # First, let's see what we have
        cursor.execute("""
            SELECT title, tmdb_id 
            FROM movies 
            WHERE tmdb_id IS NOT NULL 
            ORDER BY tmdb_id, title
        """)
        
        movies_with_tmdb = cursor.fetchall()
        
        # Group by TMDB ID to find duplicates
        tmdb_groups = {}
        for title, tmdb_id in movies_with_tmdb:
            if tmdb_id not in tmdb_groups:
                tmdb_groups[tmdb_id] = []
            tmdb_groups[tmdb_id].append(title)
        
        # Find duplicates
        duplicates_to_remove = []
        for tmdb_id, titles in tmdb_groups.items():
            if len(titles) > 1:
                print(f"📝 TMDB ID {tmdb_id} has {len(titles)} movies:")
                for i, title in enumerate(titles):
                    print(f"   {i+1}. {title}")
                
                # Keep the first one (usually the most accurate), remove the rest
                for title in titles[1:]:
                    duplicates_to_remove.append((title, tmdb_id))
        
        if not duplicates_to_remove:
            print("✅ No duplicate TMDB IDs found!")
            return True
        
        print(f"\n🗑️ Found {len(duplicates_to_remove)} duplicates to remove:")
        for title, tmdb_id in duplicates_to_remove:
            print(f"   - {title} (TMDB ID: {tmdb_id})")
        
        # Remove the duplicates
        removed_count = 0
        for title, tmdb_id in duplicates_to_remove:
            cursor.execute("DELETE FROM movies WHERE title = %s AND tmdb_id = %s", (title, tmdb_id))
            removed_count += 1
            print(f"   ✅ Removed: {title}")
        
        conn.commit()
        
        print(f"\n📊 Summary:")
        print(f"  Removed {removed_count} duplicate movies")
        
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
        print(f"❌ Error removing duplicates: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    remove_duplicate_tmdb_ids()
