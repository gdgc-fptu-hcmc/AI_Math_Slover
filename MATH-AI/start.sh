#!/bin/bash

# Math Animation AI - Startup Script
# This script starts both backend and frontend servers

set -e

echo "🎓 Math Animation AI - Starting..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Please run this script from the MATH-AI directory${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠️  Port $1 is already in use${NC}"
        return 1
    fi
    return 0
}

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
    cp backend/.env.example backend/.env
    echo -e "${RED}❌ Please edit backend/.env with your API keys before running${NC}"
    echo ""
    echo "Required keys:"
    echo "  - GOOGLE_API_KEY"
    echo "  - OPENAI_API_KEY (or ANTHROPIC_API_KEY)"
    echo ""
    exit 1
fi

# Check ports
echo "📡 Checking ports..."
check_port 8000 || {
    echo -e "${RED}Backend port 8000 is in use. Stop the process or change PORT in .env${NC}"
    exit 1
}
check_port 3000 || {
    echo -e "${RED}Frontend port 3000 is in use. Stop the process or change port in vite.config.js${NC}"
    exit 1
}

echo -e "${GREEN}✅ Ports available${NC}"
echo ""

# Check if backend venv exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating...${NC}"
    cd backend
    python3 -m venv venv
    cd ..
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Check if backend dependencies are installed
if [ ! -f "backend/venv/bin/activate" ] && [ ! -f "backend/venv/Scripts/activate" ]; then
    echo -e "${RED}❌ Virtual environment activation script not found${NC}"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not installed. Installing...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    echo ""
fi

# Create temp directory if not exists
mkdir -p backend/temp

echo -e "${BLUE}🚀 Starting Backend Server...${NC}"
echo ""

# Start backend in background
cd backend
if [ -f "venv/Scripts/activate" ]; then
    # Windows Git Bash
    source venv/Scripts/activate
else
    # Unix-like systems
    source venv/bin/activate
fi

python -m app.main > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
echo "   Log: backend.log"
echo "   URL: http://localhost:8000"
echo ""

# Wait for backend to start
echo "⏳ Waiting for backend to be ready..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start. Check backend.log for errors${NC}"
    exit 1
fi

# Try to connect to backend
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Backend not responding. Check backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

echo ""
echo -e "${BLUE}🎨 Starting Frontend Server...${NC}"
echo ""

# Start frontend in background
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "   Log: frontend.log"
echo "   URL: http://localhost:3000"
echo ""

# Wait for frontend to start
echo "⏳ Waiting for frontend to be ready..."
sleep 5

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Frontend failed to start. Check frontend.log for errors${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  🎉  Math Animation AI is running!                           ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  📱 Frontend: ${BLUE}http://localhost:3000${GREEN}                          ║${NC}"
echo -e "${GREEN}║  🔧 Backend:  ${BLUE}http://localhost:8000${GREEN}                          ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║  Press Ctrl+C to stop all servers                            ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "💡 Tips:"
echo "   - Upload an image with math problems"
echo "   - Use camera to capture math from paper"
echo "   - Type math equations directly"
echo ""
echo "📝 Logs:"
echo "   - Backend:  tail -f backend.log"
echo "   - Frontend: tail -f frontend.log"
echo ""

# Save PIDs to file
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping servers...${NC}"

    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✅ Backend stopped${NC}"
        rm .backend.pid
    fi

    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null && echo -e "${GREEN}✅ Frontend stopped${NC}"
        rm .frontend.pid
    fi

    # Kill any remaining processes on those ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null

    echo -e "${GREEN}👋 Goodbye!${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Keep script running and show logs
echo "📊 Showing live logs (Ctrl+C to stop):"
echo ""

tail -f backend.log frontend.log 2>/dev/null
