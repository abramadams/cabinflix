# CabinFlix 🎬

A Netflix-style web application to browse your cabin DVD movie collection. Built with Next.js 14, TypeScript, and Tailwind CSS.

## ✨ Features

- **775 Movies**: Your complete movie collection with 99.4% enrichment rate
- **Smart Search**: Search by title, overview, or genres
- **Advanced Filtering**: Filter by genre, rating (PG, PG-13, R, etc.), and year range
- **Infinite Scroll**: Smooth pagination for performance
- **Movie Details**: Click info button for detailed movie information with inline trailers
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern Netflix-style interface
- **Debounced Year Filter**: Smooth year range selection without page reloads

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd cabinflix
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env with your actual values
   # - DATABASE_URL: Your Neon/PostgreSQL connection string
   # - TMDB_API_KEY: Your TMDB API key (optional, for data enrichment)
   ```

4. **Set up the database**
   ```bash
   # For Neon database (recommended)
   python3 setup_neon_db.py
   
   # For local PostgreSQL with Docker
   docker compose up -d postgres
   ```

5. **Import your movie data**
   ```bash
   # Import movies to your database
   python3 import_all_movies_neon.py
   ```

6. **Start the development server**
   ```bash
   npm run dev
   ```

7. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🌐 Deployment

### Vercel Deployment (Recommended)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Sign up/Login with GitHub
   - Click "New Project"
   - Import your GitHub repository

3. **Set up environment variables**
   In your Vercel project settings, add:
   ```
   DATABASE_URL=your-neon-database-connection-string
   TMDB_API_KEY=your-tmdb-api-key
   ```

4. **Deploy**
   - Vercel will automatically deploy on every push
   - Your app will be available at `https://your-project.vercel.app`

### Database Sync Process

When you need to update the remote database with local changes:

```bash
# Export current local database state
python3 -c "
import json
import psycopg2
from decimal import Decimal
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

cursor.execute('''
    SELECT id, title, tmdb_id, release_date, rating, poster_path,
           backdrop_path, overview, popularity, vote_average, vote_count
    FROM movies
    ORDER BY title
''')

movies = []
for row in cursor.fetchall():
    movies.append({
        'id': row[0],
        'title': row[1],
        'tmdb_id': row[2],
        'release_date': str(row[3]) if row[3] else None,
        'rating': row[4],
        'poster_path': row[5],
        'backdrop_path': row[6],
        'overview': row[7],
        'popularity': float(row[8]) if row[8] else None,
        'vote_average': float(row[9]) if row[9] else None,
        'vote_count': int(row[10]) if row[10] else None
    })

with open('current_database_export.json', 'w') as f:
    json.dump(movies, f, indent=2)

print(f'✅ Exported {len(movies)} movies')
conn.close()
"

# Sync to remote database
python3 sync_remote_database.py
```

## 🗄️ Database Setup

### Neon Database (Recommended)
1. **Create account** at [neon.tech](https://neon.tech)
2. **Create new project**
3. **Get connection string** from dashboard
4. **Update .env** with your connection string
5. **Run setup script**: `python3 setup_neon_db.py`

### Local PostgreSQL
```bash
# Start with Docker
docker compose up -d postgres

# Or install PostgreSQL locally
# Then run: python3 setup_neon_db.py
```

## 📊 Data Structure

The app includes:
- **775 Movies** total
- **770 Enriched Movies** with TMDB data (99.4% enrichment rate)
- **5 Basic Movies** with just titles (placeholder images)
- **18 Genres** for filtering
- **6 Rating Categories** (G, PG, PG-13, R, NC-17, NR)

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, Framer Motion
- **Database**: PostgreSQL (Neon)
- **Movie Data**: TMDB API
- **Deployment**: Vercel

## 📝 Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# TMDB API Configuration (optional)
TMDB_API_KEY=your-tmdb-api-key-here
TMDB_BASE_URL=https://api.themoviedb.org/3

# Supabase Configuration (if using Supabase)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
```

## 🔧 Available Scripts

### Database Management
- `setup_neon_db.py` - Initialize database schema
- `import_all_movies_neon.py` - Import movies to Neon database
- `sync_remote_database.py` - Sync local data to remote database
- `import_all_movies.py` - Legacy import script (backup)

### Development
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server

## 🎯 Current Status

- ✅ **99.4% Data Enrichment** - 770/775 movies have TMDB data
- ✅ **Clean Codebase** - Removed 20+ temporary scripts
- ✅ **Optimized UI** - Fixed year filter with debouncing
- ✅ **Production Ready** - Deployed on Vercel with Neon database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Enjoy browsing your movie collection! 🎬✨**
