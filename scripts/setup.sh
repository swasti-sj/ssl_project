#!/bin/bash
# setup.sh - automates project setup, testing, and deployment

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo "========================================="
echo "  Campus Event Management - Setup Script"
echo "========================================="

# check python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed."
    exit 1
fi

echo "[1/5] Creating virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "  -> Virtual environment created."
else
    echo "  -> Virtual environment already exists."
fi

echo "[2/5] Installing dependencies..."
source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate" 2>/dev/null
pip install -r "$PROJECT_DIR/requirements.txt" --quiet
echo "  -> Dependencies installed."

echo "[3/5] Initializing database..."
cd "$PROJECT_DIR"
python3 -c "
import database as db
db.init_db()
db.seed_data()
print('  -> Database initialized with seed data.')
"

echo "[4/5] Running tests..."
python3 -m pytest tests/ -v --tb=short 2>&1 || {
    echo "[WARNING] Some tests failed. Check output above."
}

echo "[5/5] Running profiling..."
python3 profiling/profile_app.py 2>&1 || {
    echo "[WARNING] Profiling encountered issues."
}

echo ""
echo "========================================="
echo "  Setup complete!"
echo "  Run the app:  python3 app.py"
echo "  Open browser: http://localhost:5000"
echo "========================================="
