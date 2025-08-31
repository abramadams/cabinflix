export interface Movie {
  id: number
  title: string
  original_title?: string
  tmdb_id?: number
  release_date: string
  runtime?: number
  overview?: string
  poster_path?: string
  backdrop_path?: string
  vote_average?: number
  vote_count?: number
  popularity?: number
  trailer_url?: string
  rating?: string
  genres?: string[]
  cast?: string[]
  created_at?: string
  updated_at?: string
}

export interface Genre {
  id: number
  name: string
}

export interface Cast {
  id: number
  name: string
  tmdb_id?: number
}

export interface MovieCast {
  movie_id: number
  cast_id: number
  character_name?: string
  order_index?: number
}

export interface SearchFilters {
  query: string
  genres: string[]
  yearRange: [number, number]
  minRating?: number
  maxRuntime?: number
}

export interface TMDBMovie {
  id: number
  title: string
  original_title: string
  release_date: string
  runtime: number
  overview: string
  poster_path: string
  backdrop_path: string
  vote_average: number
  vote_count: number
  popularity: number
  genres: Array<{ id: number; name: string }>
}

export interface TMDBMovieCredits {
  cast: Array<{
    id: number
    name: string
    character: string
    order: number
  }>
}

export interface TMDBMovieVideos {
  results: Array<{
    key: string
    site: string
    type: string
    official: boolean
  }>
}
