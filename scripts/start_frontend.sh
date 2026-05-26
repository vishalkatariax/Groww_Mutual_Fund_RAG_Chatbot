#!/bin/bash
# Phase 6 Frontend Setup Script
# This script installs dependencies and starts the development server

set -e

echo "================================"
echo "  MF FAQ Assistant - Frontend"
echo "  Phase 6 Setup & Launch"
echo "================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo ""
    echo "Please install Node.js (v18 or higher):"
    echo "  - macOS: brew install node"
    echo "  - Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    echo "  - Windows: Download from https://nodejs.org/"
    echo ""
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version must be 18 or higher (current: $(node -v))"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

echo ""
echo "✅ Dependencies installed successfully!"
echo ""
echo "================================"
echo "  Starting Development Server"
echo "================================"
echo ""
echo "🚀 Frontend will be available at: http://localhost:3000"
echo "📡 Backend API expected at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start development server
npm run dev
