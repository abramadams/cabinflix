'use client'

import { useState, useEffect, useRef } from 'react'
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
  'Action', 'Adventure', 'Animation', 'Comedy',
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
  const [yearInputs, setYearInputs] = useState<[string, string]>(['', ''])
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  // Update local state when props change
  useEffect(() => {
    setLocalYearRange(yearRange)
    setYearInputs([yearRange[0].toString(), yearRange[1].toString()])
  }, [yearRange])

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

  const handleYearInputChange = (index: number, value: string) => {
    const newInputs: [string, string] = [...yearInputs] as [string, string]
    newInputs[index] = value
    setYearInputs(newInputs)

    // Parse the value
    const numValue = parseInt(value)
    if (!isNaN(numValue) && numValue >= 1900 && numValue <= 2024) {
      const newRange: [number, number] = [...localYearRange] as [number, number]
      newRange[index] = numValue
      
      // Ensure min <= max
      if (index === 0 && numValue > newRange[1]) {
        newRange[1] = numValue
        newInputs[1] = numValue.toString()
        setYearInputs(newInputs)
      } else if (index === 1 && numValue < newRange[0]) {
        newRange[0] = numValue
        newInputs[0] = numValue.toString()
        setYearInputs(newInputs)
      }
      
      setLocalYearRange(newRange)
      
      // Debounce the API call to prevent excessive reloads
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
      debounceRef.current = setTimeout(() => {
        onYearRangeChange(newRange)
      }, 500)
    }
  }

  const handleYearInputBlur = (index: number) => {
    const value = yearInputs[index]
    const numValue = parseInt(value)
    
    if (isNaN(numValue) || numValue < 1900 || numValue > 2024) {
      // Reset to valid value
      const newInputs: [string, string] = [...yearInputs] as [string, string]
      newInputs[index] = localYearRange[index].toString()
      setYearInputs(newInputs)
    }
  }

  const handleYearSliderChange = (index: number, value: number) => {
    const newRange: [number, number] = [...localYearRange] as [number, number]
    newRange[index] = value
    
    // Ensure min <= max
    if (index === 0 && value > newRange[1]) {
      newRange[1] = value
    } else if (index === 1 && value < newRange[0]) {
      newRange[0] = value
    }
    
    setLocalYearRange(newRange)
    setYearInputs([newRange[0].toString(), newRange[1].toString()])
    
    // Debounce the API call
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }
    debounceRef.current = setTimeout(() => {
      onYearRangeChange(newRange)
    }, 300)
  }

  const clearFilters = () => {
    onGenresChange([])
    onRatingsChange([])
    const defaultRange: [number, number] = [1900, 2024]
    setLocalYearRange(defaultRange)
    setYearInputs(['1900', '2024'])
    onYearRangeChange(defaultRange)
  }

  const hasActiveFilters = selectedGenres.length > 0 || selectedRatings.length > 0 ||
    yearRange[0] !== 1900 || yearRange[1] !== 2024

  return (
    <div className="bg-card border rounded-lg p-4 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-lg text-foreground">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Genres */}
      <div>
        <h4 className="font-medium text-sm text-foreground mb-3">Genres</h4>
        <div className="grid grid-cols-2 gap-2">
          {availableGenres.map((genre) => (
            <label key={genre} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedGenres.includes(genre)}
                onChange={() => handleGenreToggle(genre)}
                className="rounded border-input"
              />
              <span className="text-sm text-foreground">{genre}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Ratings */}
      <div>
        <h4 className="font-medium text-sm text-foreground mb-3">Ratings</h4>
        <div className="grid grid-cols-2 gap-2">
          {availableRatings.map((rating) => (
            <label key={rating} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedRatings.includes(rating)}
                onChange={() => handleRatingToggle(rating)}
                className="rounded border-input"
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
              type="text"
              value={yearInputs[0]}
              onChange={(e) => handleYearInputChange(0, e.target.value)}
              onBlur={() => handleYearInputBlur(0)}
              placeholder="1900"
              className="w-20 px-2 py-1 text-sm border border-input rounded focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground"
            />
            <span className="text-sm text-muted-foreground">to</span>
            <input
              type="text"
              value={yearInputs[1]}
              onChange={(e) => handleYearInputChange(1, e.target.value)}
              onBlur={() => handleYearInputBlur(1)}
              placeholder="2024"
              className="w-20 px-2 py-1 text-sm border border-input rounded focus:outline-none focus:ring-2 focus:ring-ring bg-background text-foreground"
            />
          </div>
          
          {/* Simple dual range slider */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>1900</span>
              <span>2024</span>
            </div>
            <div className="relative h-6 flex items-center">
              <div className="absolute w-full h-2 bg-muted rounded-lg"></div>
              <div 
                className="absolute h-2 bg-primary rounded-lg"
                style={{
                  left: `${((localYearRange[0] - 1900) / (2024 - 1900)) * 100}%`,
                  width: `${((localYearRange[1] - localYearRange[0]) / (2024 - 1900)) * 100}%`
                }}
              ></div>
              
              {/* Start handle */}
              <div 
                className="absolute w-4 h-4 bg-primary rounded-full border-2 border-background shadow-md cursor-pointer z-20 hover:scale-110 transition-transform"
                style={{
                  left: `${((localYearRange[0] - 1900) / (2024 - 1900)) * 100}%`,
                  transform: 'translateX(-50%)'
                }}
              ></div>
              
              {/* End handle */}
              <div 
                className="absolute w-4 h-4 bg-primary rounded-full border-2 border-background shadow-md cursor-pointer z-20 hover:scale-110 transition-transform"
                style={{
                  left: `${((localYearRange[1] - 1900) / (2024 - 1900)) * 100}%`,
                  transform: 'translateX(-50%)'
                }}
              ></div>
              
              {/* Clickable track */}
              <div 
                className="absolute w-full h-6 cursor-pointer z-10"
                onClick={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect()
                  const percent = (e.clientX - rect.left) / rect.width
                  const value = Math.round(1900 + percent * (2024 - 1900))
                  
                  // Determine which handle to move based on which is closer
                  const distanceToStart = Math.abs(value - localYearRange[0])
                  const distanceToEnd = Math.abs(value - localYearRange[1])
                  
                  if (distanceToStart < distanceToEnd) {
                    if (value <= localYearRange[1]) {
                      handleYearSliderChange(0, value)
                    }
                  } else {
                    if (value >= localYearRange[0]) {
                      handleYearSliderChange(1, value)
                    }
                  }
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Active filters summary */}
      {hasActiveFilters && (
        <div className="pt-4 border-t border-border">
          <h4 className="font-medium text-sm text-foreground mb-2">Active Filters</h4>
          <div className="space-y-2">
            {selectedGenres.length > 0 && (
              <div className="text-sm text-muted-foreground">
                Genres: {selectedGenres.join(', ')}
              </div>
            )}
            {selectedRatings.length > 0 && (
              <div className="text-sm text-muted-foreground">
                Ratings: {selectedRatings.join(', ')}
              </div>
            )}
            {(yearRange[0] !== 1900 || yearRange[1] !== 2024) && (
              <div className="text-sm text-muted-foreground">
                Years: {yearRange[0]} - {yearRange[1]}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
