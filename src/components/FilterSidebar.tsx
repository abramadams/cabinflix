'use client'

import { useState } from 'react'
import { Filter, X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FilterSidebarProps {
  selectedGenres: string[]
  onGenresChange: (genres: string[]) => void
  selectedRatings: string[]
  onRatingsChange: (ratings: string[]) => void
  yearRange: [number, number]
  onYearRangeChange: (range: [number, number]) => void
}

const availableGenres = [
  'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
  'Documentary', 'Drama', 'Family', 'Fantasy', 'History',
  'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction',
  'Thriller', 'War', 'Western'
]

const availableRatings = [
  'G', 'PG', 'PG-13', 'R', 'NC-17', 'NR'
]

export default function FilterSidebar({
  selectedGenres,
  onGenresChange,
  selectedRatings,
  onRatingsChange,
  yearRange,
  onYearRangeChange
}: FilterSidebarProps) {
  const [localYearRange, setLocalYearRange] = useState(yearRange)

  const handleGenreToggle = (genre: string) => {
    if (selectedGenres.includes(genre)) {
      onGenresChange(selectedGenres.filter(g => g !== genre))
    } else {
      onGenresChange([...selectedGenres, genre])
    }
  }

  const handleRatingToggle = (rating: string) => {
    if (selectedRatings.includes(rating)) {
      onRatingsChange(selectedRatings.filter(r => r !== rating))
    } else {
      onRatingsChange([...selectedRatings, rating])
    }
  }

  const handleYearRangeChange = (index: number, value: number) => {
    const newRange: [number, number] = [...localYearRange] as [number, number]
    newRange[index] = value
    
    // Ensure min <= max
    if (index === 0 && value > newRange[1]) {
      newRange[1] = value
    } else if (index === 1 && value < newRange[0]) {
      newRange[0] = value
    }
    
    setLocalYearRange(newRange)
    onYearRangeChange(newRange)
  }

  const clearFilters = () => {
    onGenresChange([])
    onRatingsChange([])
    const defaultRange: [number, number] = [1900, 2024]
    setLocalYearRange(defaultRange)
    onYearRangeChange(defaultRange)
  }

  const hasActiveFilters = selectedGenres.length > 0 || selectedRatings.length > 0 ||
    yearRange[0] !== 1900 || yearRange[1] !== 2024

  return (
    <div className="bg-card border rounded-lg p-4 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-muted-foreground" />
          <h3 className="font-semibold text-foreground">Filters</h3>
        </div>
        
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Genres */}
      <div>
        <h4 className="font-medium text-sm text-foreground mb-3">Genres</h4>
        <div className="space-y-2">
          {availableGenres.map((genre) => (
            <label key={genre} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedGenres.includes(genre)}
                onChange={() => handleGenreToggle(genre)}
                className="rounded border-input text-primary focus:ring-primary"
              />
              <span className="text-sm text-foreground">{genre}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Ratings */}
      <div>
        <h4 className="font-medium text-sm text-foreground mb-3">Ratings</h4>
        <div className="space-y-2">
          {availableRatings.map((rating) => (
            <label key={rating} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedRatings.includes(rating)}
                onChange={() => handleRatingToggle(rating)}
                className="rounded border-input text-primary focus:ring-primary"
              />
              <span className="text-sm text-foreground">{rating}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Year Range */}
      <div>
        <h4 className="font-medium text-sm text-foreground mb-3">Year Range</h4>
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <input
              type="number"
              value={localYearRange[0]}
              onChange={(e) => handleYearRangeChange(0, parseInt(e.target.value) || 1900)}
              min="1900"
              max="2024"
              className="w-20 px-2 py-1 text-sm border border-input rounded focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <span className="text-sm text-muted-foreground">to</span>
            <input
              type="number"
              value={localYearRange[1]}
              onChange={(e) => handleYearRangeChange(1, parseInt(e.target.value) || 2024)}
              min="1900"
              max="2024"
              className="w-20 px-2 py-1 text-sm border border-input rounded focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          
          {/* Year range slider */}
          <div className="relative">
            <input
              type="range"
              min="1900"
              max="2024"
              value={localYearRange[0]}
              onChange={(e) => handleYearRangeChange(0, parseInt(e.target.value))}
              className="absolute w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer slider"
            />
            <input
              type="range"
              min="1900"
              max="2024"
              value={localYearRange[1]}
              onChange={(e) => handleYearRangeChange(1, parseInt(e.target.value))}
              className="absolute w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer slider"
            />
          </div>
        </div>
      </div>

      {/* Active filters summary */}
      {hasActiveFilters && (
        <div className="pt-4 border-t">
          <h4 className="font-medium text-sm text-foreground mb-2">Active Filters</h4>
          <div className="space-y-2">
            {selectedGenres.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {selectedGenres.map((genre) => (
                  <span
                    key={genre}
                    className="inline-flex items-center px-2 py-1 bg-primary/10 text-primary text-xs rounded"
                  >
                    {genre}
                    <button
                      onClick={() => handleGenreToggle(genre)}
                      className="ml-1 hover:bg-primary/20 rounded"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
            
            {selectedRatings.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {selectedRatings.map((rating) => (
                  <span
                    key={rating}
                    className="inline-flex items-center px-2 py-1 bg-primary/10 text-primary text-xs rounded"
                  >
                    {rating}
                    <button
                      onClick={() => handleRatingToggle(rating)}
                      className="ml-1 hover:bg-primary/20 rounded"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
            
            {(yearRange[0] !== 1900 || yearRange[1] !== 2024) && (
              <div className="text-xs text-muted-foreground">
                Year: {yearRange[0]} - {yearRange[1]}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
