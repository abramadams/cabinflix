# CabinFlix 🎬

A Netflix-style web application to browse your cabin DVD movie collection. Built with Next.js 14, TypeScript, and Tailwind CSS.

## ✨ Features

- **781 Movies**: Your complete movie collection from Excel
- **Smart Search**: Search by title, overview, or genres
- **Advanced Filtering**: Filter by genre, rating (PG, PG-13, R, etc.), and year range
- **Infinite Scroll**: Smooth pagination for performance
- **Movie Details**: Click info button for detailed movie information with inline trailers
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern Netflix-style interface

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

3. **Set up the database**
   ```bash
   # Start PostgreSQL with Docker
   docker compose up -d postgres
   
   # Run the database initialization
   docker compose exec postgres psql -U postgres -d cabinflix -f /docker-entrypoint-initdb.d/init.sql
   ```

4. **Import your movie data**
   ```bash
   # Extract movies from Excel
   python3 extract_movies.py
   
   # Enrich with TMDB data (optional)
   python3 enrich_movies.py
   
   # Import to database
   python3 import_all_movies.py
   ```

5. **Start the development server**
   ```bash
   docker compose up -d
   ```

6. **Open your browser**
   Navigate to [http://localhost:3003](http://localhost:3003)

## 🌐 Deployment

### Option 1: Vercel (Recommended)

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
   DB_HOST=your-database-host
   DB_PORT=5432
   DB_NAME=cabinflix
   DB_USER=your-db-user
   DB_PASSWORD=your-db-password
   ```

4. **Deploy**
   - Vercel will automatically deploy on every push
   - Your app will be available at `https://your-project.vercel.app`

### Option 2: Railway

1. **Connect to Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up/Login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"

2. **Add PostgreSQL**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will provide connection details

3. **Set environment variables**
   Railway will automatically set the database environment variables

4. **Deploy**
   - Railway will automatically deploy your app
   - Your app will be available at the provided URL

## 🗄️ Database Setup

### Local PostgreSQL
```sql
-- Create database
CREATE DATABASE cabinflix;

-- Run the initialization script
\i supabase/init.sql
```

### Cloud Database Options
- **Neon** (Free tier available): [neon.tech](https://neon.tech)
- **Supabase** (Free tier available): [supabase.com](https://supabase.com)
- **Railway** (Free tier available): [railway.app](https://railway.app)

## 📊 Data Structure

The app includes:
- **781 Movies** from your original Excel file
- **397 Enriched Movies** with TMDB data (posters, ratings, genres, trailers)
- **384 Basic Movies** with just titles (placeholder images)
- **19 Genres** for filtering

## 🛠️ Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS, Framer Motion
- **Database**: PostgreSQL
- **Movie Data**: TMDB API
- **Deployment**: Vercel/Railway

## 📝 Environment Variables

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cabinflix
DB_USER=postgres
DB_PASSWORD=postgres

# TMDB API (for data enrichment)
TMDB_API_KEY=your-tmdb-api-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**Enjoy browsing your movie collection! 🎬✨**
# Trigger new deployment
