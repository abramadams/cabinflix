import { Pool } from 'pg'

// Database configuration for both local and production
if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL environment variable is required')
}

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
})

export default pool
