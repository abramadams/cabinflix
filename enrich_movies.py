import json
import requests
import time
import os
from typing import List, Dict, Optional
from extract_movies import extract_movies

class TMDBEnricher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.session = requests.Session()
        self.session.params.update({'api_key': api_key})
    
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
                return data['results'][0]  # Return the first (most relevant) result
            return None
        except Exception as e:
            print(f"Error searching for '{title}': {e}")
            return None
    
    def get_movie_details(self, tmdb_id: int) -> Optional[Dict]:
        """Get detailed movie information including credits, videos, and release dates"""
        try:
            # Get movie details
            response = self.session.get(f"{self.base_url}/movie/{tmdb_id}", params={
                'language': 'en-US',
                'append_to_response': 'credits,videos,release_dates'
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting details for TMDB ID {tmdb_id}: {e}")
            return None
    
    def get_trailer_url(self, videos_data: Dict) -> Optional[str]:
        """Extract trailer URL from videos data"""
        if not videos_data or 'results' not in videos_data:
            return None
        
        # Look for official trailers first, then any trailer
        for video in videos_data['results']:
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                if video.get('official', False):
                    return f"https://www.youtube.com/watch?v={video['key']}"
        
        # If no official trailer, get the first trailer
        for video in videos_data['results']:
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                return f"https://www.youtube.com/watch?v={video['key']}"
        
        return None

def enrich_movies_from_excel(api_key: str, output_file: str = "enriched_movies.json"):
    """Enrich movies from Excel file with TMDB data"""
    
    # Extract movies from Excel
    print("Extracting movies from Excel file...")
    movies = extract_movies()
    
    # Initialize TMDB enricher
    enricher = TMDBEnricher(api_key)
    
    enriched_movies = []
    total_movies = len(movies)
    
    print(f"Found {total_movies} movies. Starting enrichment...")
    
    for i, movie in enumerate(movies, 1):
        print(f"Processing {i}/{total_movies}: {movie['title']}")
        
        # Search for movie in TMDB
        search_result = enricher.search_movie(movie['title'])
        
        if search_result:
            # Get detailed information
            details = enricher.get_movie_details(search_result['id'])
            
            if details:
                # Extract genres
                genres = [genre['name'] for genre in details.get('genres', [])]
                
                # Extract cast (top 5)
                cast = []
                if 'credits' in details and 'cast' in details['credits']:
                    cast = [person['name'] for person in details['credits']['cast'][:5]]
                
                # Get trailer URL
                trailer_url = enricher.get_trailer_url(details.get('videos', {}))
                
                # Get rating (US certification)
                rating = None
                if 'release_dates' in details and 'results' in details['release_dates']:
                    for release in details['release_dates']['results']:
                        if release['iso_3166_1'] == 'US':
                            for cert in release['release_dates']:
                                if cert['type'] == 3:  # Type 3 is theatrical release
                                    rating = cert['certification']
                                    break
                            if rating:
                                break
                
                enriched_movie = {
                    'id': i,
                    'title': details['title'],
                    'original_title': details.get('original_title'),
                    'tmdb_id': details['id'],
                    'release_date': details.get('release_date', ''),
                    'runtime': details.get('runtime'),
                    'overview': details.get('overview'),
                    'poster_path': details.get('poster_path'),
                    'backdrop_path': details.get('backdrop_path'),
                    'vote_average': details.get('vote_average'),
                    'vote_count': details.get('vote_count'),
                    'popularity': details.get('popularity'),
                    'trailer_url': trailer_url,
                    'rating': rating,
                    'genres': genres,
                    'cast': cast,
                    'sheet': movie['sheet']  # Keep original sheet info
                }
                
                enriched_movies.append(enriched_movie)
                print(f"  ✓ Enriched: {enriched_movie['title']} ({enriched_movie['release_date'][:4]})")
            else:
                print(f"  ✗ Could not get details for: {movie['title']}")
        else:
            print(f"  ✗ Not found in TMDB: {movie['title']}")
        
        # Rate limiting - be nice to TMDB API
        time.sleep(0.25)  # 4 requests per second max
    
    # Save enriched data
    with open(output_file, 'w') as f:
        json.dump(enriched_movies, f, indent=2)
    
    print(f"\nEnrichment complete! Saved {len(enriched_movies)} enriched movies to {output_file}")
    print(f"Success rate: {len(enriched_movies)}/{total_movies} ({len(enriched_movies)/total_movies*100:.1f}%)")
    
    return enriched_movies

if __name__ == "__main__":
    # Get API key from environment or prompt user
    api_key = os.getenv('TMDB_API_KEY')
    
    if not api_key:
        api_key = input("Enter your TMDB API key: ").strip()
    
    if not api_key:
        print("Error: TMDB API key is required")
        exit(1)
    
    # Run enrichment
    enriched_movies = enrich_movies_from_excel(api_key)
