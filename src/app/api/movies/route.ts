import { NextRequest, NextResponse } from 'next/server'
import pool from '@/lib/db'

// Force dynamic rendering for this API route
export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const query = searchParams.get('q') || ''
    const genres = searchParams.get('genres')?.split(',') || []
    const ratings = searchParams.get('ratings')?.split(',') || []
    const yearMin = searchParams.get('yearMin') || '1900'
    const yearMax = searchParams.get('yearMax') || '2024'
    const limit = parseInt(searchParams.get('limit') || '1000') // Increased default limit
    const offset = parseInt(searchParams.get('offset') || '0')

    // Build the base WHERE clause for counting
    let countSql = `
      SELECT COUNT(DISTINCT m.id) as total
      FROM movies m
      LEFT JOIN movie_genres mg ON m.id = mg.movie_id
      LEFT JOIN genres g ON mg.genre_id = g.id
      WHERE 1=1
    `
    
    let sql = `
      SELECT 
        m.id,
        m.title,
        m.original_title,
        m.tmdb_id,
        m.release_date,
        m.runtime,
        m.overview,
        m.poster_path,
        m.backdrop_path,
        m.vote_average,
        m.vote_count,
        m.popularity,
        m.trailer_url,
        m.rating,
        ARRAY_AGG(DISTINCT g.name) FILTER (WHERE g.name IS NOT NULL) as genres
      FROM movies m
      LEFT JOIN movie_genres mg ON m.id = mg.movie_id
      LEFT JOIN genres g ON mg.genre_id = g.id
      WHERE 1=1
    `
    
    const params: any[] = []
    let paramIndex = 1

    // Search query
    if (query) {
      const searchCondition = ` AND (
        m.title ILIKE $${paramIndex} OR 
        m.overview ILIKE $${paramIndex}
      )`
      sql += searchCondition
      countSql += searchCondition
      params.push(`%${query}%`)
      paramIndex++
    }

    // Genre filter
    if (genres.length > 0) {
      const genrePlaceholders = genres.map(() => `$${paramIndex++}`).join(',')
      const genreCondition = ` AND g.name IN (${genrePlaceholders})`
      sql += genreCondition
      countSql += genreCondition
      params.push(...genres)
    }

    // Rating filter
    if (ratings.length > 0) {
      const ratingPlaceholders = ratings.map(() => `$${paramIndex++}`).join(',')
      const ratingCondition = ` AND m.rating IN (${ratingPlaceholders})`
      sql += ratingCondition
      countSql += ratingCondition
      params.push(...ratings)
    }

    // Year range filter
    const yearMinCondition = ` AND (m.release_date IS NULL OR EXTRACT(YEAR FROM m.release_date) >= $${paramIndex})`
    sql += yearMinCondition
    countSql += yearMinCondition
    params.push(parseInt(yearMin))
    paramIndex++
    
    const yearMaxCondition = ` AND (m.release_date IS NULL OR EXTRACT(YEAR FROM m.release_date) <= $${paramIndex})`
    sql += yearMaxCondition
    countSql += yearMaxCondition
    params.push(parseInt(yearMax))
    paramIndex++

    // Get total count first
    const countResult = await pool.query(countSql, params)
    const total = parseInt(countResult.rows[0].total)

    // Add ordering and pagination to main query
    sql += `
      GROUP BY m.id, m.title, m.original_title, m.tmdb_id, m.release_date, 
               m.runtime, m.overview, m.poster_path, m.backdrop_path, 
               m.vote_average, m.vote_count, m.popularity, m.trailer_url, m.rating
      ORDER BY 
        CASE WHEN m.tmdb_id IS NOT NULL THEN 0 ELSE 1 END,
        m.popularity DESC NULLS LAST, 
        m.vote_average DESC NULLS LAST,
        m.title ASC
      LIMIT $${paramIndex} OFFSET $${paramIndex + 1}
    `
    params.push(limit, offset)

    const result = await pool.query(sql, params)
    
    const movies = result.rows.map((row: any) => ({
      id: row.id,
      title: row.title,
      original_title: row.original_title,
      tmdb_id: row.tmdb_id,
      release_date: row.release_date,
      runtime: row.runtime,
      overview: row.overview,
      poster_path: row.poster_path,
      backdrop_path: row.backdrop_path,
      vote_average: row.vote_average ? Number(row.vote_average) : null,
      vote_count: row.vote_count ? Number(row.vote_count) : null,
              popularity: row.popularity ? Number(row.popularity) : null,
        trailer_url: row.trailer_url,
        rating: row.rating,
        genres: row.genres || []
    }))

    return NextResponse.json({
      movies,
      total,
      limit,
      offset
    })

  } catch (error) {
    console.error('Database error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch movies' },
      { status: 500 }
    )
  }
}
