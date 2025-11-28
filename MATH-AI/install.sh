#!/bin/bash

# Math Animation AI - Fluidity Improvements Installation Script
# This script automates the installation of UX improvements

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Math Animation AI - Installing Fluidity Improvements   ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Please run this script from the MATH-AI directory${NC}"
    exit 1
fi

cd frontend

# Backup original files
echo -e "${YELLOW}📦 Creating backups of original files...${NC}"
mkdir -p .backups

if [ -f "src/App.jsx" ]; then
    cp src/App.jsx .backups/App_original.jsx
    echo -e "${GREEN}✓ Backed up App.jsx${NC}"
fi

if [ -f "src/components/ChatInterface.jsx" ]; then
    cp src/components/ChatInterface.jsx .backups/ChatInterface_original.jsx
    echo -e "${GREEN}✓ Backed up ChatInterface.jsx${NC}"
fi

if [ -f "src/components/VideoPlayer.jsx" ]; then
    cp src/components/VideoPlayer.jsx .backups/VideoPlayer_original.jsx
    echo -e "${GREEN}✓ Backed up VideoPlayer.jsx${NC}"
fi

echo ""

# Install dependencies
echo -e "${YELLOW}📦 Installing new dependencies...${NC}"
npm install framer-motion@^10.16.16
echo -e "${GREEN}✓ Framer Motion installed${NC}"
echo ""

# Copy new files
echo -e "${YELLOW}🔧 Installing improved components...${NC}"

# Note: This script assumes the improved files are in the parent directory
# Adjust paths as needed based on where you place the improved files

if [ -f "../App_improved.jsx" ]; then
    cp ../App_improved.jsx src/App.jsx
    echo -e "${GREEN}✓ Updated App.jsx${NC}"
else
    echo -e "${RED}⚠ Warning: App_improved.jsx not found${NC}"
fi

if [ -f "../ChatInterface_improved.jsx" ]; then
    cp ../ChatInterface_improved.jsx src/components/ChatInterface.jsx
    echo -e "${GREEN}✓ Updated ChatInterface.jsx${NC}"
else
    echo -e "${RED}⚠ Warning: ChatInterface_improved.jsx not found${NC}"
fi

if [ -f "../VideoPlayer_improved.jsx" ]; then
    cp ../VideoPlayer_improved.jsx src/components/VideoPlayer.jsx
    echo -e "${GREEN}✓ Updated VideoPlayer.jsx${NC}"
else
    echo -e "${RED}⚠ Warning: VideoPlayer_improved.jsx not found${NC}"
fi

echo ""

# Update imports in main.jsx if needed
echo -e "${YELLOW}🔧 Checking main.jsx...${NC}"
if grep -q "ChatInterface_improved" src/main.jsx 2>/dev/null; then
    sed -i 's/ChatInterface_improved/ChatInterface/g' src/main.jsx
    echo -e "${GREEN}✓ Updated imports in main.jsx${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}What's New:${NC}"
echo "  • Drag & drop anywhere on screen"
echo "  • Inline camera capture (no modals)"
echo "  • Smart error recovery with retry buttons"
echo "  • Smooth animations throughout"
echo "  • Better loading states"
echo "  • Improved video player controls"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Restart the development server:"
echo "     ${BLUE}npm run dev${NC}"
echo ""
echo "  2. Test the new features:"
echo "     - Drag an image anywhere"
echo "     - Try camera capture"
echo "     - Test error recovery"
echo ""
echo -e "${YELLOW}To restore original files:${NC}"
echo "  cp .backups/App_original.jsx src/App.jsx"
echo "  cp .backups/ChatInterface_original.jsx src/components/ChatInterface.jsx"
echo "  cp .backups/VideoPlayer_original.jsx src/components/VideoPlayer.jsx"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"