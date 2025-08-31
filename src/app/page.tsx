'use client'

import { useState, useCallback, useEffect } from 'react'
import { Film, X, ArrowUp } from 'lucide-react'
import SearchBar from '@/components/SearchBar'
import FilterSidebar from '@/components/FilterSidebar'
import MovieGrid from '@/components/MovieGrid'
import MovieModal from '@/components/MovieModal'
import { Movie } from '@/types/movie'

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGenres, setSelectedGenres] = useState<string[]>([])
  const [selectedRatings, setSelectedRatings] = useState<string[]>([])
  const [yearRange, setYearRange] = useState<[number, number]>([1900, 2024])
  const [showFilters, setShowFilters] = useState(false)
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [showScrollToTop, setShowScrollToTop] = useState(false)

  // Memoize the search handler to prevent re-renders
  const handleSearchChange = useCallback((value: string) => {
    setSearchQuery(value)
  }, [])

  // Memoize the genre change handler
  const handleGenresChange = useCallback((genres: string[]) => {
    setSelectedGenres(genres)
  }, [])

  // Memoize the rating change handler
  const handleRatingsChange = useCallback((ratings: string[]) => {
    setSelectedRatings(ratings)
  }, [])

  // Memoize the year range change handler
  const handleYearRangeChange = useCallback((range: [number, number]) => {
    setYearRange(range)
  }, [])

  // Memoize the filter toggle handler
  const handleFilterToggle = useCallback(() => {
    setShowFilters((prev: boolean) => !prev)
  }, [])

  // Handle genre clicks from movie cards
  const handleGenreClick = useCallback((genre: string) => {
    setSelectedGenres((prev) => {
      // If genre is already selected, remove it (toggle behavior)
      if (prev.includes(genre)) {
        return prev.filter(g => g !== genre)
      }
      // Otherwise add it to the selected genres
      return [...prev, genre]
    })
  }, [])

  // Handle info button clicks from movie cards
  const handleInfoClick = useCallback((movie: Movie) => {
    setSelectedMovie(movie)
    setIsModalOpen(true)
  }, [])

  // Handle modal close
  const handleModalClose = useCallback(() => {
    setIsModalOpen(false)
    setSelectedMovie(null)
  }, [])

  // Handle title click to reset all filters
  const handleTitleClick = useCallback(() => {
    setSearchQuery('')
    setSelectedGenres([])
    setSelectedRatings([])
    setYearRange([1900, 2024])
    setShowFilters(false)
  }, [])

  // Handle scroll to top
  const handleScrollToTop = useCallback(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  // Track scroll position
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      setShowScrollToTop(scrollTop > 300) // Show after scrolling 300px
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center space-x-2 flex-shrink-0">
              <Film className="h-6 w-6 md:h-8 md:w-8 text-primary" />
              <h1 
                className="text-xl md:text-2xl font-bold text-foreground cursor-pointer hover:text-primary transition-colors"
                onClick={handleTitleClick}
              >
                CabinFlix
              </h1>
            </div>
            
            <div className="flex items-center space-x-2 md:space-x-4 flex-1 min-w-0">
              <SearchBar 
                value={searchQuery}
                onChange={handleSearchChange}
                placeholder="Search movies or genres..."
                className="flex-1 min-w-0"
              />
              
              <button
                onClick={handleFilterToggle}
                className="btn-secondary text-sm px-3 py-2 md:px-4 md:py-2 flex-shrink-0"
              >
                Filters
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Filter Tags */}
        {(selectedGenres.length > 0 || selectedRatings.length > 0 || searchQuery || yearRange[0] !== 1900 || yearRange[1] !== 2024) && (
          <div className="mb-6">
            <div className="flex flex-wrap gap-2 items-center">
              <span className="text-sm font-medium text-muted-foreground">Active filters:</span>
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="px-3 py-1 bg-primary/10 text-primary text-sm rounded-full hover:bg-primary/20 transition-colors flex items-center gap-1"
                >
                  Search: "{searchQuery}"
                  <X className="h-3 w-3" />
                </button>
              )}
              {selectedGenres.map((genre) => (
                <button
                  key={genre}
                  onClick={() => setSelectedGenres(prev => prev.filter(g => g !== genre))}
                  className="px-3 py-1 bg-secondary text-secondary-foreground text-sm rounded-full hover:bg-secondary/80 transition-colors flex items-center gap-1"
                >
                  {genre}
                  <X className="h-3 w-3" />
                </button>
              ))}
              {selectedRatings.map((rating) => (
                <button
                  key={rating}
                  onClick={() => setSelectedRatings(prev => prev.filter(r => r !== rating))}
                  className="px-3 py-1 bg-secondary text-secondary-foreground text-sm rounded-full hover:bg-secondary/80 transition-colors flex items-center gap-1"
                >
                  {rating}
                  <X className="h-3 w-3" />
                </button>
              ))}
              {(yearRange[0] !== 1900 || yearRange[1] !== 2024) && (
                <button
                  onClick={() => setYearRange([1900, 2024])}
                  className="px-3 py-1 bg-secondary text-secondary-foreground text-sm rounded-full hover:bg-secondary/80 transition-colors flex items-center gap-1"
                >
                  {yearRange[0]} - {yearRange[1]}
                  <X className="h-3 w-3" />
                </button>
              )}
              <button
                onClick={handleTitleClick}
                className="px-3 py-1 bg-destructive/10 text-destructive text-sm rounded-full hover:bg-destructive/20 transition-colors flex items-center gap-1"
              >
                Clear All
                <X className="h-3 w-3" />
              </button>
            </div>
          </div>
        )}

        {/* Mobile: Filters stack above content */}
        <div className="block md:hidden">
          {showFilters && (
            <div className="mb-6">
              <FilterSidebar
                selectedGenres={selectedGenres}
                onGenresChange={handleGenresChange}
                selectedRatings={selectedRatings}
                onRatingsChange={handleRatingsChange}
                yearRange={yearRange}
                onYearRangeChange={handleYearRangeChange}
              />
            </div>
          )}
        </div>

        {/* Desktop: Sidebar layout */}
        <div className="hidden md:flex gap-8">
          {/* Sidebar */}
          {showFilters && (
            <aside className="w-64 flex-shrink-0">
              <FilterSidebar
                selectedGenres={selectedGenres}
                onGenresChange={handleGenresChange}
                selectedRatings={selectedRatings}
                onRatingsChange={handleRatingsChange}
                yearRange={yearRange}
                onYearRangeChange={handleYearRangeChange}
              />
            </aside>
          )}

          {/* Main Content */}
          <main className="flex-1">
            <MovieGrid 
              searchQuery={searchQuery}
              selectedGenres={selectedGenres}
              selectedRatings={selectedRatings}
              yearRange={yearRange}
              onGenreClick={handleGenreClick}
              onInfoClick={handleInfoClick}
            />
          </main>
        </div>

        {/* Mobile: Main content without sidebar */}
        <div className="block md:hidden">
          <main>
            <MovieGrid 
              searchQuery={searchQuery}
              selectedGenres={selectedGenres}
              selectedRatings={selectedRatings}
              yearRange={yearRange}
              onGenreClick={handleGenreClick}
              onInfoClick={handleInfoClick}
            />
          </main>
        </div>
      </div>

      {/* Scroll to Top Button */}
      {showScrollToTop && (
        <button
          onClick={handleScrollToTop}
          className="fixed bottom-6 right-6 z-40 p-3 bg-primary text-primary-foreground rounded-full shadow-lg hover:bg-primary/90 transition-all duration-300 hover:scale-110"
          aria-label="Scroll to top"
        >
          <ArrowUp className="h-5 w-5" />
        </button>
      )}

      {/* Movie Modal */}
      <MovieModal
        movie={selectedMovie}
        isOpen={isModalOpen}
        onClose={handleModalClose}
      />
    </div>
  )
}
