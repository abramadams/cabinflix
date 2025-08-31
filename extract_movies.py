import pandas as pd
import json

def extract_movies():
    # Read the Excel file
    xl = pd.ExcelFile('Cabin Movies.xlsx')
    
    # Get all sheet names except 'Index' and 'Numbers'
    sheet_names = [name for name in xl.sheet_names if name not in ['Index', 'Numbers']]
    
    movies = []
    
    for sheet_name in sheet_names:
        try:
            df = pd.read_excel('Cabin Movies.xlsx', sheet_name=sheet_name)
            
            # Get the first column (movie titles)
            if len(df.columns) > 0:
                movie_column = df.columns[0]
                movie_titles = df[movie_column].dropna().tolist()
                
                for title in movie_titles:
                    if isinstance(title, str) and title.strip():
                        # Clean the title
                        clean_title = title.strip()
                        movies.append({
                            'title': clean_title,
                            'sheet': sheet_name
                        })
        except Exception as e:
            print(f"Error processing sheet {sheet_name}: {e}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_movies = []
    for movie in movies:
        if movie['title'] not in seen:
            seen.add(movie['title'])
            unique_movies.append(movie)
    
    print(f"Total unique movies found: {len(unique_movies)}")
    
    # Save to JSON file
    with open('movies.json', 'w') as f:
        json.dump(unique_movies, f, indent=2)
    
    # Print first 20 movies as sample
    print("\nFirst 20 movies:")
    for i, movie in enumerate(unique_movies[:20]):
        print(f"{i+1}. {movie['title']} (Sheet: {movie['sheet']})")
    
    return unique_movies

if __name__ == "__main__":
    movies = extract_movies()
