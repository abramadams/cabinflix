#!/bin/bash

echo "🚀 CabinFlix Deployment with Database Update"
echo "============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not found. Please initialize git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    exit 1
fi

# Check if we have a remote repository
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ No remote repository found. Please add your GitHub repository:"
    echo "   git remote add origin https://github.com/yourusername/cabinflix.git"
    exit 1
fi

echo "✅ Git repository found"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your database credentials."
    exit 1
fi

echo "✅ Environment file found"

# Export current database data to ensure we have the latest
echo "📊 Exporting current database data..."
python3 -c "
import json
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    # Get all movies with their data
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
            'popularity': row[8],
            'vote_average': row[9],
            'vote_count': row[10]
        })
    
    # Save to file
    with open('current_database_export.json', 'w') as f:
        json.dump(movies, f, indent=2)
    
    print(f'✅ Exported {len(movies)} movies to current_database_export.json')
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM movies')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM movies WHERE tmdb_id IS NOT NULL')
    enriched = cursor.fetchone()[0]
    
    print(f'📊 Database stats: {enriched}/{total} movies enriched ({enriched/total*100:.1f}%)')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Error exporting database: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database export failed."
    exit 1
fi

# Build the project
echo "🔨 Building the project..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please fix the errors and try again."
    exit 1
fi

echo "✅ Build successful"

# Commit and push changes
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Deploy with database update - $(date) - $(python3 -c 'import json; data=json.load(open("current_database_export.json")); print(f"{len(data)} movies, {sum(1 for m in data if m[\"tmdb_id\"])}/{len(data)} enriched")')"
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ Push failed. Please check your git configuration."
    exit 1
fi

echo "✅ Code pushed to GitHub"

echo ""
echo "🎉 Deployment Complete!"
echo "======================"
echo "✅ Database exported to: current_database_export.json"
echo "✅ Code pushed to GitHub"
echo ""
echo "📋 Next Steps for Vercel:"
echo "1. Go to https://vercel.com"
echo "2. Sign up/Login with GitHub"
echo "3. Click 'New Project'"
echo "4. Import your cabinflix repository"
echo "5. Set up environment variables:"
echo "   - DATABASE_URL=your-neon-database-url"
echo "6. Deploy!"
echo ""
echo "🌐 Your app will be available at: https://your-project.vercel.app"
echo ""
echo "📊 Database Status:"
python3 -c "
import json
data = json.load(open('current_database_export.json'))
enriched = sum(1 for m in data if m['tmdb_id'])
print(f'   Total movies: {len(data)}')
print(f'   Enriched movies: {enriched}')
print(f'   Enrichment rate: {enriched/len(data)*100:.1f}%')
"
echo ""
echo "💡 The remote database will use the same data structure as your local database."
echo "   No duplicates will be created during deployment."
