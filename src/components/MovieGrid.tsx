'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { Film } from 'lucide-react'
import MovieCard from '@/components/MovieCard'
import { Movie } from '@/types/movie'

interface MovieGridProps {
  searchQuery: string
  selectedGenres: string[]
  selectedRatings: string[]
  yearRange: [number, number]
  onGenreClick?: (genre: string) => void
  onInfoClick?: (movie: Movie) => void
}

const ITEMS_PER_PAGE = 24 // 4 rows of 6 cards on desktop

export default function MovieGrid({ searchQuery, selectedGenres, selectedRatings, yearRange, onGenreClick, onInfoClick }: MovieGridProps) {
  const [movies, setMovies] = useState<Movie[]>([])
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [currentPage, setCurrentPage] = useState(0)
  const [total, setTotal] = useState(0)
  const observerRef = useRef<IntersectionObserver | null>(null)
  const loadingRef = useRef<HTMLDivElement>(null)
  const fetchMoviesRef = useRef<typeof fetchMovies | null>(null)

  // Reset pagination when filters change
  useEffect(() => {
    setMovies([])
    setCurrentPage(0)
    setHasMore(true)
    setTotal(0)
  }, [searchQuery, selectedGenres, selectedRatings, yearRange])

  const fetchMovies = useCallback(async (page: number, append: boolean = false) => {
    try {
      const isInitialLoad = page === 0
      if (isInitialLoad) {
        setLoading(true)
      } else {
        setLoadingMore(true)
      }
      
      const params = new URLSearchParams()
      if (searchQuery) params.append('q', searchQuery)
      if (selectedGenres.length > 0) params.append('genres', selectedGenres.join(','))
      if (selectedRatings.length > 0) params.append('ratings', selectedRatings.join(','))
      params.append('yearMin', yearRange[0].toString())
      params.append('yearMax', yearRange[1].toString())
      params.append('limit', ITEMS_PER_PAGE.toString())
      params.append('offset', (page * ITEMS_PER_PAGE).toString())

      const response = await fetch(`/api/movies?${params.toString()}`)
      if (!response.ok) {
        throw new Error('Failed to fetch movies')
      }
      
      const data = await response.json()
      
      if (append) {
        setMovies((prev: Movie[]) => {
          // Filter out any movies that already exist to prevent duplicates
          const existingIds = new Set(prev.map((m: Movie) => m.id))
          const newMovies = data.movies.filter((movie: Movie) => !existingIds.has(movie.id))
          return [...prev, ...newMovies]
        })
      } else {
        setMovies(data.movies)
      }
      
      setTotal(data.total)
      setHasMore(data.movies.length === ITEMS_PER_PAGE)
      setCurrentPage(page)
    } catch (error) {
      console.error('Error fetching movies:', error)
      if (!append) {
        setMovies([])
      }
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }, [searchQuery, selectedGenres, selectedRatings, yearRange])

  // Store the current fetchMovies function in a ref
  useEffect(() => {
    fetchMoviesRef.current = fetchMovies
  }, [fetchMovies])

  // Initial load
  useEffect(() => {
    fetchMovies(0)
  }, [fetchMovies])

  // Simple scroll-based infinite scroll
  useEffect(() => {
    const handleScroll = () => {
      if (loadingMore || !hasMore) return
      
      const scrollTop = window.scrollY
      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight
      
      // Load more when user is near the bottom (within 200px)
      if (scrollTop + windowHeight >= documentHeight - 200) {
        console.log('Scroll detected - loading more movies, page:', currentPage + 1)
        fetchMoviesRef.current?.(currentPage + 1, true)
      }
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [hasMore, loadingMore, currentPage])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div>
      {/* Results Header */}
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-foreground">
          {searchQuery || selectedGenres.length > 0 ? 'Search Results' : 'All Movies'}
        </h2>
        <p className="text-muted-foreground">
          {total} movie{total !== 1 ? 's' : ''} found
        </p>
      </div>

      {/* Movie Grid */}
      {movies.length > 0 ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
            {movies.map((movie, index) => (
              <MovieCard 
                key={movie.id} 
                movie={movie} 
                onGenreClick={onGenreClick}
                onInfoClick={onInfoClick}
                priority={index < 6} // Priority for first 6 images (above the fold)
              />
            ))}
          </div>

          {/* Loading indicator for infinite scroll */}
          {hasMore && (
            <div ref={loadingRef} className="flex justify-center py-8">
              {loadingMore ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                  <span className="text-muted-foreground">Loading more movies...</span>
                </div>
              ) : (
                <div className="h-8" /> // Invisible element for intersection observer
              )}
            </div>
          )}

          {/* End of results */}
          {!hasMore && movies.length > 0 && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">
                You've reached the end of the results
              </p>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-12">
          <Film className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-lg font-medium text-foreground mb-2">No movies found</h3>
          <p className="text-muted-foreground">
            Try adjusting your search terms or filters
          </p>
        </div>
      )}
    </div>
  )
}
