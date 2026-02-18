#!/bin/bash
# Quick activation script for music theory analysis environment

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_DIR"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install matplotlib numpy
else
    source venv/bin/activate
fi

echo "✓ Environment activated"
echo "  Project: $PROJECT_DIR"
echo "  Python: $(which python3)"
echo ""
echo "Available scripts:"
echo "  python scripts/consonance_analysis.py"
echo "  python scripts/waveform.py"
