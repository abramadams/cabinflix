-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create movies table
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
  vote_average DECIMAL(3,1),
  vote_count INTEGER,
  popularity DECIMAL(10,2),
  trailer_url VARCHAR(500),
  rating VARCHAR(10),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create genres table
CREATE TABLE IF NOT EXISTS genres (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL
);

-- Create movie-genre relationship table
CREATE TABLE IF NOT EXISTS movie_genres (
  movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
  genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
  PRIMARY KEY (movie_id, genre_id)
);

-- Create cast table
CREATE TABLE IF NOT EXISTS cast (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  tmdb_id INTEGER UNIQUE
);

-- Create movie-cast relationship table
CREATE TABLE IF NOT EXISTS movie_cast (
  movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
  cast_id INTEGER REFERENCES cast(id) ON DELETE CASCADE,
  character_name VARCHAR(255),
  order_index INTEGER,
  PRIMARY KEY (movie_id, cast_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_movies_title ON movies USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_movies_release_date ON movies(release_date);
CREATE INDEX IF NOT EXISTS idx_movies_vote_average ON movies(vote_average);
CREATE INDEX IF NOT EXISTS idx_movies_popularity ON movies(popularity);
CREATE INDEX IF NOT EXISTS idx_movies_tmdb_id ON movies(tmdb_id);

CREATE INDEX IF NOT EXISTS idx_movie_genres_movie_id ON movie_genres(movie_id);
CREATE INDEX IF NOT EXISTS idx_movie_genres_genre_id ON movie_genres(genre_id);

CREATE INDEX IF NOT EXISTS idx_movie_cast_movie_id ON movie_cast(movie_id);
CREATE INDEX IF NOT EXISTS idx_movie_cast_cast_id ON movie_cast(cast_id);
CREATE INDEX IF NOT EXISTS idx_movie_cast_order ON movie_cast(order_index);

CREATE INDEX IF NOT EXISTS idx_cast_name ON cast USING gin(to_tsvector('english', name));

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_movies_updated_at BEFORE UPDATE ON movies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some common genres
INSERT INTO genres (name) VALUES 
  ('Action'), ('Adventure'), ('Animation'), ('Comedy'), ('Crime'),
  ('Documentary'), ('Drama'), ('Family'), ('Fantasy'), ('History'),
  ('Horror'), ('Music'), ('Mystery'), ('Romance'), ('Science Fiction'),
  ('TV Movie'), ('Thriller'), ('War'), ('Western')
ON CONFLICT (name) DO NOTHING;
