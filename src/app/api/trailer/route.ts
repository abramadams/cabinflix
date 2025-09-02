import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const tmdbId = searchParams.get('tmdbId')

    if (!tmdbId) {
      return NextResponse.json(
        { error: 'TMDB ID is required' },
        { status: 400 }
      )
    }

    const tmdbApiKey = process.env.TMDB_API_KEY
    if (!tmdbApiKey) {
      return NextResponse.json(
        { error: 'TMDB API key not configured' },
        { status: 500 }
      )
    }

    // Fetch movie videos from TMDB
    const response = await fetch(
      `https://api.themoviedb.org/3/movie/${tmdbId}/videos?api_key=${tmdbApiKey}&language=en-US`
    )

    if (!response.ok) {
      throw new Error(`TMDB API responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    // Find the first official trailer (preferably from YouTube)
    let trailerUrl = null
    
    if (data.results && data.results.length > 0) {
      // First try to find an official trailer from YouTube
      const officialTrailer = data.results.find(
        (video: any) => 
          video.site === 'YouTube' && 
          video.type === 'Trailer' && 
          video.official === true
      )
      
      if (officialTrailer) {
        trailerUrl = `https://www.youtube.com/watch?v=${officialTrailer.key}`
      } else {
        // Fallback to any trailer from YouTube
        const anyTrailer = data.results.find(
          (video: any) => 
            video.site === 'YouTube' && 
            video.type === 'Trailer'
        )
        
        if (anyTrailer) {
          trailerUrl = `https://www.youtube.com/watch?v=${anyTrailer.key}`
        }
      }
    }

    return NextResponse.json({
      trailerUrl,
      found: !!trailerUrl
    })

  } catch (error) {
    console.error('Error fetching trailer:', error)
    return NextResponse.json(
      { error: 'Failed to fetch trailer' },
      { status: 500 }
    )
  }
}
