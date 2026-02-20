#!/usr/bin/env bash
echo "=== Price List Lookup ==="

# Kill any existing server on port 5000
lsof -ti:5000 | xargs kill -9 2>/dev/null

# Create venv if it doesn't exist
if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "Starting server at http://localhost:5000"
echo "Press Ctrl+C to stop."
echo ""

# Open browser then start server
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:5000 &
else
    xdg-open http://localhost:5000 2>/dev/null &
fi

python app.py
