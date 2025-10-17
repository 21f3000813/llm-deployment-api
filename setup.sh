#!/bin/bash
# Setup script for Linux/Mac

echo "========================================"
echo "LLM Code Deployment System - Setup"
echo "========================================"
echo ""

# Check Node.js
echo "[1/6] Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi
echo "✓ Node.js found"

# Check Python
echo "[2/6] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python from https://python.org/"
    exit 1
fi
echo "✓ Python found"

# Install Node.js dependencies
echo "[3/6] Installing Node.js dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "ERROR: npm install failed"
    exit 1
fi
echo "✓ Node.js dependencies installed"

# Install Python dependencies
echo "[4/6] Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: pip install failed"
    exit 1
fi
echo "✓ Python dependencies installed"

# Install Playwright browsers
echo "[5/6] Installing Playwright browsers..."
python3 -m playwright install chromium
echo "✓ Playwright setup complete"

# Setup environment file
echo "[6/6] Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo ""
    echo "IMPORTANT: Please edit .env file with your credentials:"
    echo "  - STUDENT_EMAIL"
    echo "  - STUDENT_SECRET"
    echo "  - GITHUB_TOKEN"
    echo "  - GITHUB_USERNAME"
    echo "  - OPENAI_API_KEY or ANTHROPIC_API_KEY"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your credentials"
echo "  2. Initialize database: python3 scripts/instructor/init_db.py"
echo "  3. Start student API: npm start"
echo ""
echo "For detailed instructions, see QUICKSTART.md"
echo ""
