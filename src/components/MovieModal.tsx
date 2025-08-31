'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'
import { X, Star, Clock, Play, ExternalLink } from 'lucide-react'
import { Movie } from '@/types/movie'
import { cn } from '@/lib/utils'

interface MovieModalProps {
  movie: Movie | null
  isOpen: boolean
  onClose: () => void
}

export default function MovieModal({ movie, isOpen, onClose }: MovieModalProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  // Reset video state when modal opens/closes
  useEffect(() => {
    if (!isOpen) {
      setIsPlaying(false)
    }
  }, [isOpen])

  // Close modal on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!movie || !isOpen) return null

  const posterUrl = movie.poster_path 
    ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : '/placeholder-poster.jpg'

  const backdropUrl = movie.backdrop_path 
    ? `https://image.tmdb.org/t/p/original${movie.backdrop_path}`
    : posterUrl

  const formatRuntime = (minutes?: number) => {
    if (!minutes) return ''
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}h ${mins}m`
  }

  const formatYear = (dateString: string) => {
    return new Date(dateString).getFullYear()
  }

  // Convert YouTube watch URL to embed URL
  const getEmbedUrl = (url: string) => {
    if (!url) return null
    const videoId = url.match(/[?&]v=([^&]+)/)?.[1]
    return videoId ? `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0` : null
  }

  const embedUrl = getEmbedUrl(movie.trailer_url || '')

  const handlePlayTrailer = () => {
    setIsPlaying(true)
  }

  const handleCloseTrailer = () => {
    setIsPlaying(false)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-hidden rounded-lg bg-background shadow-2xl">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 bg-black/50 text-white rounded-full hover:bg-black/70 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Trailer Section */}
        {isPlaying && embedUrl && (
          <div className="relative w-full h-96 md:h-[500px]">
            <button
              onClick={handleCloseTrailer}
              className="absolute top-4 right-4 z-10 p-2 bg-black/50 text-white rounded-full hover:bg-black/70 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
            <iframe
              src={embedUrl}
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>
        )}

        {/* Hero section with backdrop */}
        {!isPlaying && (
          <div className="relative h-64 md:h-80">
            <Image
              src={backdropUrl}
              alt={movie.title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, 80vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent" />
            
            {/* Hero content */}
            <div className="absolute bottom-0 left-0 right-0 p-6">
              <div className="flex items-end gap-4">
                {/* Poster */}
                <div className="relative w-24 h-36 md:w-32 md:h-48 flex-shrink-0">
                  <Image
                    src={posterUrl}
                    alt={movie.title}
                    fill
                    className="object-cover rounded"
                    sizes="(max-width: 768px) 96px, 128px"
                  />
                </div>
                
                {/* Title and actions */}
                <div className="flex-1 min-w-0">
                  <h2 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
                    {movie.title}
                  </h2>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground mb-4">
                    <span>{formatYear(movie.release_date)}</span>
                    {movie.runtime && (
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {formatRuntime(movie.runtime)}
                      </div>
                    )}
                    {movie.vote_average && (
                      <div className="flex items-center">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400 mr-1" />
                        {Number(movie.vote_average).toFixed(1)}
                      </div>
                    )}
                  </div>
                  
                  {/* Action buttons */}
                  <div className="flex gap-3">
                    {embedUrl && (
                      <button
                        onClick={handlePlayTrailer}
                        className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
                      >
                        <Play className="h-4 w-4" />
                        Watch Trailer
                      </button>
                    )}
                    {movie.tmdb_id && (
                      <a
                        href={`https://www.themoviedb.org/movie/${movie.tmdb_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 px-4 py-2 bg-secondary text-secondary-foreground rounded hover:bg-secondary/80 transition-colors"
                      >
                        <ExternalLink className="h-4 w-4" />
                        More Info
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Content */}
        {!isPlaying && (
          <div className="p-6">
            {/* Genres */}
            {movie.genres && movie.genres.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {movie.genres.map((genre) => (
                  <span
                    key={genre}
                    className="px-3 py-1 bg-secondary text-secondary-foreground text-sm rounded-full"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            )}

            {/* Overview */}
            {movie.overview && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-foreground mb-2">Overview</h3>
                <p className="text-muted-foreground leading-relaxed">
                  {movie.overview}
                </p>
              </div>
            )}

            {/* Additional details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-foreground">Release Date:</span>
                <span className="text-muted-foreground ml-2">
                  {new Date(movie.release_date).toLocaleDateString()}
                </span>
              </div>
              {movie.runtime && (
                <div>
                  <span className="font-medium text-foreground">Runtime:</span>
                  <span className="text-muted-foreground ml-2">
                    {formatRuntime(movie.runtime)}
                  </span>
                </div>
              )}
                          {movie.vote_average && (
              <div>
                <span className="font-medium text-foreground">Rating:</span>
                <span className="text-muted-foreground ml-2">
                  {Number(movie.vote_average).toFixed(1)}/10
                </span>
              </div>
            )}
            {movie.rating && (
              <div>
                <span className="font-medium text-foreground">MPAA Rating:</span>
                <span className="text-muted-foreground ml-2">
                  {movie.rating}
                </span>
              </div>
            )}
              {movie.vote_count && (
                <div>
                  <span className="font-medium text-foreground">Votes:</span>
                  <span className="text-muted-foreground ml-2">
                    {movie.vote_count.toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
