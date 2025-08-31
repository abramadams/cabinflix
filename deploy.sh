#!/bin/bash

echo "🚀 CabinFlix Deployment Script"
echo "================================"

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
git commit -m "Ready for deployment - $(date)"
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ Push failed. Please check your git configuration."
    exit 1
fi

echo "✅ Code pushed to GitHub"

echo ""
echo "🎉 Deployment Steps:"
echo "==================="
echo "1. Go to https://vercel.com"
echo "2. Sign up/Login with GitHub"
echo "3. Click 'New Project'"
echo "4. Import your cabinflix repository"
echo "5. Set up environment variables:"
echo "   - DB_HOST=your-database-host"
echo "   - DB_PORT=5432"
echo "   - DB_NAME=cabinflix"
echo "   - DB_USER=your-db-user"
echo "   - DB_PASSWORD=your-db-password"
echo "6. Deploy!"
echo ""
echo "🌐 Your app will be available at: https://your-project.vercel.app"
echo ""
echo "📚 For database setup, check the README.md file"
