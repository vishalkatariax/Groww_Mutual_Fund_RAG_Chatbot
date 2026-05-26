#!/bin/bash
###############################################################################
# MF FAQ Assistant - Development Startup Script
# 
# Starts both backend (FastAPI) and frontend (React + Vite) servers
# with hot-reload enabled for development.
#
# Usage:
#   ./scripts/start_dev.sh              # Start both servers
#   ./scripts/start_dev.sh --backend    # Start only backend
#   ./scripts/start_dev.sh --frontend   # Start only frontend
#   ./scripts/start_dev.sh --help       # Show help
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
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Functions
print_header() {
    echo -e "${BLUE}"
    echo "================================================================================"
    echo "  MF FAQ Assistant - Development Server"
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

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_status "Python 3 found: $(python3 --version)"
}

check_node() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed"
        exit 1
    fi
    print_status "Node.js found: $(node --version)"
}

check_dependencies() {
    # Check Python dependencies
    if [ ! -d "$PROJECT_ROOT/venv" ] && [ ! -d "$PROJECT_ROOT/.venv" ]; then
        print_warning "No virtual environment found. Using system Python packages."
    fi
    
    # Check if uvicorn is installed
    if ! python3 -c "import uvicorn" 2>/dev/null; then
        print_error "uvicorn not installed. Run: pip install -r requirements.txt"
        exit 1
    fi
    
    # Check if frontend dependencies are installed
    if [ ! -d "$PROJECT_ROOT/app/frontend/node_modules" ]; then
        print_warning "Frontend dependencies not installed. Installing now..."
        cd "$PROJECT_ROOT/app/frontend"
        npm install
        print_status "Frontend dependencies installed"
        cd "$PROJECT_ROOT"
    fi
}

check_port() {
    local port=$1
    if lsof -ti:$port > /dev/null 2>&1; then
        print_warning "Port $port is already in use"
        return 1
    fi
    return 0
}

start_backend() {
    print_status "Starting backend server on port $BACKEND_PORT..."
    print_status "API Documentation: http://localhost:$BACKEND_PORT/docs"
    
    cd "$PROJECT_ROOT"
    python3 -m uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $BACKEND_PORT \
        --reload \
        --log-level info &
    
    BACKEND_PID=$!
    print_status "Backend started (PID: $BACKEND_PID)"
}

start_frontend() {
    # Find available port
    local port=$FRONTEND_PORT
    while lsof -ti:$port > /dev/null 2>&1; do
        port=$((port + 1))
    done
    
    print_status "Starting frontend server on port $port..."
    print_status "Frontend URL: http://localhost:$port"
    
    cd "$PROJECT_ROOT/app/frontend"
    PORT=$port npm run dev &
    
    FRONTEND_PID=$!
    print_status "Frontend started (PID: $FRONTEND_PID)"
}

cleanup() {
    echo ""
    print_warning "Shutting down servers..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_status "Backend stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_status "Frontend stopped"
    fi
    
    print_status "All servers stopped"
    exit 0
}

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --backend     Start only the backend server"
    echo "  --frontend    Start only the frontend server"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start both servers"
    echo "  $0 --backend          # Start only backend"
    echo "  $0 --frontend         # Start only frontend"
    echo ""
}

# Trap SIGINT and SIGTERM for cleanup
trap cleanup SIGINT SIGTERM

# Main
print_header

# Parse arguments
MODE="both"
if [ "$1" == "--backend" ]; then
    MODE="backend"
elif [ "$1" == "--frontend" ]; then
    MODE="frontend"
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
    exit 0
fi

# Check dependencies
echo -e "${BLUE}Checking dependencies...${NC}"
check_python
check_node
check_dependencies
echo ""

# Start servers
echo -e "${BLUE}Starting servers...${NC}"

if [ "$MODE" == "both" ] || [ "$MODE" == "backend" ]; then
    start_backend
fi

if [ "$MODE" == "both" ] || [ "$MODE" == "frontend" ]; then
    start_frontend
fi

echo ""
echo -e "${GREEN}================================================================================${NC}"
echo -e "${GREEN}  Development servers are running!${NC}"
echo -e "${GREEN}================================================================================${NC}"

if [ "$MODE" == "both" ] || [ "$MODE" == "backend" ]; then
    echo -e "  Backend:  ${BLUE}http://localhost:$BACKEND_PORT${NC}"
    echo -e "  API Docs: ${BLUE}http://localhost:$BACKEND_PORT/docs${NC}"
fi

if [ "$MODE" == "both" ] || [ "$MODE" == "frontend" ]; then
    echo -e "  Frontend: ${BLUE}http://localhost:$FRONTEND_PORT${NC} (or next available port)"
fi

echo -e "${GREEN}================================================================================${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Wait for background processes
wait
