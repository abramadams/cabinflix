'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Star, Clock, Info } from 'lucide-react'
import { Movie } from '@/types/movie'
import { cn } from '@/lib/utils'

interface MovieCardProps {
  movie: Movie
  onGenreClick?: (genre: string) => void
  onInfoClick?: (movie: Movie) => void
  priority?: boolean
}

export default function MovieCard({ movie, onGenreClick, onInfoClick, priority }: MovieCardProps) {
  const [isHovered, setIsHovered] = useState(false)
  const [imageError, setImageError] = useState(false)

  const posterUrl = movie.poster_path 
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : '/placeholder-poster.jpg'

  const formatRuntime = (minutes?: number) => {
    if (!minutes) return ''
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}h ${mins}m`
  }

  const formatYear = (dateString: string) => {
    return new Date(dateString).getFullYear()
  }

  const handleGenreClick = (genre: string, e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onGenreClick?.(genre)
  }

  return (
    <div
      className="movie-card group cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Poster */}
      <div className="relative aspect-[2/3] overflow-hidden rounded-t-lg">
        {!imageError ? (
          <Image
            src={posterUrl}
            alt={movie.title}
            fill
            priority={priority}
            className="object-cover transition-transform duration-300 group-hover:scale-110"
            onError={() => setImageError(true)}
            sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, (max-width: 1024px) 25vw, (max-width: 1280px) 20vw, 16vw"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-muted">
            <div className="text-center">
              <div className="text-4xl mb-2">🎬</div>
              <div className="text-xs text-muted-foreground">No Image</div>
            </div>
          </div>
        )}

        {/* Overlay on hover */}
        <div
          className={cn(
            "absolute inset-0 bg-black/60 flex items-center justify-center transition-opacity duration-300",
            isHovered ? "opacity-100" : "opacity-0"
          )}
        >
          <div className="flex space-x-4">
            <button 
              className="p-3 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                onInfoClick?.(movie)
              }}
            >
              <Info className="h-6 w-6 text-white" />
            </button>
          </div>
        </div>

        {/* Rating badge */}
        {movie.vote_average && (
          <div className="absolute top-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-xs flex items-center">
            <Star className="h-3 w-3 fill-yellow-400 text-yellow-400 mr-1" />
            {Number(movie.vote_average).toFixed(1)}
          </div>
        )}

        {/* Rating badge (PG, PG-13, R, etc.) */}
        {movie.rating && (
          <div className="absolute top-2 left-2 bg-black/70 text-white px-2 py-1 rounded text-xs font-semibold">
            {movie.rating}
          </div>
        )}
      </div>

      {/* Movie info */}
      <div className="p-3">
        <h3 className="font-semibold text-sm text-foreground line-clamp-2 mb-1">
          {movie.title}
        </h3>
        
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{formatYear(movie.release_date)}</span>
          {movie.runtime && (
            <div className="flex items-center">
              <Clock className="h-3 w-3 mr-1" />
              {formatRuntime(movie.runtime)}
            </div>
          )}
        </div>

        {/* Genres */}
        {movie.genres && movie.genres.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {movie.genres.slice(0, 2).map((genre) => (
              <button
                key={genre}
                onClick={(e) => handleGenreClick(genre, e)}
                className="px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded hover:bg-primary hover:text-primary-foreground transition-colors cursor-pointer"
              >
                {genre}
              </button>
            ))}
            {movie.genres.length > 2 && (
              <span className="px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded">
                +{movie.genres.length - 2}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
