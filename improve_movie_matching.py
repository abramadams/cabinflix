#!/usr/bin/env python3
"""
Improve movie title matching for better TMDB data enrichment
"""

import json
import os
import requests
import time
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImprovedTMDBEnricher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        self.session.params.update({'api_key': api_key})
    
    def clean_title(self, title: str) -> str:
        """Clean title for better matching"""
        # Remove common suffixes and prefixes
        suffixes = [' (film)', ' (movie)', ' (2000)', ' (2010)', ' (2015)', ' (2018)', ' (2019)', ' (2020)', ' (2021)', ' (2022)', ' (2023)']
        prefixes = ['The ', 'A ', 'An ']
        
        cleaned = title.strip()
        
        # Remove suffixes
        for suffix in suffixes:
            if cleaned.lower().endswith(suffix.lower()):
                cleaned = cleaned[:-len(suffix)]
        
        # Remove prefixes for search (but keep original for display)
        search_title = cleaned
        for prefix in prefixes:
            if search_title.startswith(prefix):
                search_title = search_title[len(prefix):]
        
        return search_title.strip()
    
    def search_movie_improved(self, title: str) -> Optional[Dict]:
        """Improved movie search with multiple strategies"""
        original_title = title
        cleaned_title = self.clean_title(title)
        
        # Strategy 1: Search with original title
        result = self.search_movie(original_title)
        if result:
            return result
        
        # Strategy 2: Search with cleaned title
        if cleaned_title != original_title:
            result = self.search_movie(cleaned_title)
            if result:
                return result
        
        # Strategy 3: Search with common variations
        variations = [
            title.replace(" & ", " and "),
            title.replace(" and ", " & "),
            title.replace("'", ""),
            title.replace('"', ""),
            title.replace(":", ""),
            title.replace("!", ""),
            title.replace("?", ""),
        ]
        
        for variation in variations:
            if variation != title:
                result = self.search_movie(variation)
                if result:
                    return result
        
        return None
    
    def search_movie(self, title: str) -> Optional[Dict]:
        """Search for a movie by title"""
        try:
            response = self.session.get(f"{self.base_url}/search/movie", params={
                'query': title,
                'language': 'en-US',
                'page': 1,
                'include_adult': False
            })
            response.raise_for_status()
            
            data = response.json()
            if data['results']:
                # Return the first (most relevant) result
                return data['results'][0]
            
            return None
            
        except Exception as e:
            print(f"Error searching for '{title}': {e}")
            return None
    
    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """Get detailed movie information"""
        try:
            response = self.session.get(f"{self.base_url}/movie/{tmdb_id}", params={
                'append_to_response': 'videos,credits,release_dates',
                'language': 'en-US'
            })
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error getting details for TMDB ID {tmdb_id}: {e}")
            return None

def improve_movie_matching():
    """Improve movie matching and re-enrich data"""
    # Get API key
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key:
        print("❌ Error: TMDB_API_KEY not found in .env file")
        return False
    
    # Load existing movies
    if not os.path.exists('movies.json'):
        print("❌ Error: movies.json not found")
        return False
    
    with open('movies.json', 'r') as f:
        movies = json.load(f)
    
    print(f"📊 Processing {len(movies)} movies...")
    
    enricher = ImprovedTMDBEnricher(api_key)
    enriched_movies = []
    improved_count = 0
    
    for i, movie in enumerate(movies, 1):
        title = movie['title']
        
        # Try to find movie with improved matching
        search_result = enricher.search_movie_improved(title)
        
        if search_result:
            tmdb_id = search_result['id']
            
            # Get detailed information
            details = enricher.get_movie_details(tmdb_id)
            
            if details:
                # Extract rating from release dates
                rating = None
                if 'release_dates' in details and 'results' in details['release_dates']:
                    for country in details['release_dates']['results']:
                        if country['iso_3166_1'] == 'US':
                            for release in country['release_dates']:
                                if release['type'] == 3:  # Theatrical release
                                    rating = release.get('certification')
                                    break
                            break
                
                # Extract trailer URL
                trailer_url = None
                if 'videos' in details and 'results' in details['videos']:
                    for video in details['videos']['results']:
                        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                            trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
                            break
                
                # Extract genres
                genres = []
                if 'genres' in details:
                    genres = [genre['name'] for genre in details['genres']]
                
                enriched_movie = {
                    'title': title,
                    'original_title': details.get('original_title'),
                    'tmdb_id': tmdb_id,
                    'release_date': details.get('release_date'),
                    'runtime': details.get('runtime'),
                    'overview': details.get('overview'),
                    'poster_path': details.get('poster_path'),
                    'backdrop_path': details.get('backdrop_path'),
                    'vote_average': details.get('vote_average'),
                    'vote_count': details.get('vote_count'),
                    'popularity': details.get('popularity'),
                    'trailer_url': trailer_url,
                    'rating': rating,
                    'genres': genres
                }
                
                enriched_movies.append(enriched_movie)
                improved_count += 1
                print(f"✅ {title} -> {details.get('title', 'Unknown')} ({tmdb_id})")
            else:
                # Keep original movie without TMDB data
                enriched_movies.append({
                    'title': title,
                    'original_title': None,
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
                })
                print(f"❌ {title} - No TMDB data found")
        else:
            # Keep original movie without TMDB data
            enriched_movies.append({
                'title': title,
                'original_title': None,
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
            })
            print(f"❌ {title} - No TMDB data found")
        
        # Rate limiting
        if i % 10 == 0:
            print(f"   Progress: {i}/{len(movies)}")
            time.sleep(1)  # Be nice to TMDB API
    
    # Save improved enriched data
    with open('improved_enriched_movies.json', 'w') as f:
        json.dump(enriched_movies, f, indent=2)
    
    print(f"\n🎉 Improved enrichment complete!")
    print(f"📊 Total movies: {len(movies)}")
    print(f"✅ Enriched movies: {improved_count}")
    print(f"❌ Unenriched movies: {len(movies) - improved_count}")
    print(f"📁 Saved to: improved_enriched_movies.json")
    
    return True

if __name__ == "__main__":
    improve_movie_matching()
