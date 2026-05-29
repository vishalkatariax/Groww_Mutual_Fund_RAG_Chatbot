#!/bin/bash
###############################################################################
# MF FAQ Assistant - Manual Data Refresh Script
# 
# This script manually refreshes the mutual fund corpus data by:
# 1. Running the full data ingestion pipeline (Phase 1.1)
# 2. Running chunking and embedding (Phase 1.2)
# 3. Optionally committing and pushing changes to GitHub
#
# Usage:
#   ./scripts/refresh_data.sh              # Refresh data locally
#   ./scripts/refresh_data.sh --push       # Refresh and push to GitHub
#   ./scripts/refresh_data.sh --help       # Show help
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "================================================================================"
    echo "  MF FAQ Assistant - Manual Data Refresh"
    echo "================================================================================"
    echo -e "${NC}"
}

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --push        Push changes to GitHub after refresh"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Refresh data locally only"
    echo "  $0 --push             # Refresh data and push to GitHub"
    echo ""
    echo "Prerequisites:"
    echo "  - Python 3.11+ with dependencies installed"
    echo "  - GROQ_API_KEY or OPENAI_API_KEY in .env file"
    echo "  - Git configured for pushing changes"
    echo ""
}

check_dependencies() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! python3 -c "import chromadb" 2>/dev/null; then
        print_error "Required Python packages not installed. Run: pip install -r requirements.txt"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        print_error ".env file not found. Copy .env.example to .env and configure API keys."
        exit 1
    fi
    
    print_status "Dependencies check passed"
}

refresh_data() {
    print_status "Starting data refresh pipeline..."
    
    cd "$PROJECT_ROOT"
    
    # Run the complete Phase 1 pipeline
    python3 scripts/run_phase_1_complete.py
    
    print_status "Data refresh completed successfully!"
}

push_to_github() {
    print_status "Checking for changes..."
    
    cd "$PROJECT_ROOT"
    
    # Configure git user if not set
    if [ -z "$(git config user.name)" ]; then
        git config user.name "Data Refresh Script"
        git config user.email "noreply@localhost"
    fi
    
    # Check for changes
    if git diff --quiet data/; then
        print_warning "No changes detected in data directory"
        return 0
    fi
    
    # Add, commit and push
    git add data/
    git commit -m "🔄 Manual data refresh $(date '+%Y-%m-%d %H:%M')"
    
    print_status "Pushing changes to GitHub..."
    git push origin main
    
    print_status "Changes pushed successfully!"
}

# Main
print_header

# Parse arguments
PUSH_TO_GITHUB=false
if [ "$1" == "--push" ]; then
    PUSH_TO_GITHUB=true
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
check_dependencies
echo ""

# Refresh data
echo -e "${BLUE}Running data refresh pipeline...${NC}"
refresh_data
echo ""

# Push to GitHub if requested
if [ "$PUSH_TO_GITHUB" = true ]; then
    echo -e "${BLUE}Pushing changes to GitHub...${NC}"
    push_to_github
    echo ""
fi

echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}  Data refresh completed successfully!${NC}"
echo -e "${GREEN}================================================================================${NC}"
echo ""
echo "  Data files updated:"
echo "  - data/raw/ingested_documents.json"
echo "  - data/processed/chunks.json"
echo "  - data/chroma_db/ (vector store)"
echo ""