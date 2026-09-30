#!/bin/bash
# Flashcard Studio — launcher

cd "$(dirname "$0")"

echo "Checking dependencies..."
python3 -c "import tkinter, reportlab, PIL, openpyxl" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Installing needed packages (first run only)..."
    sudo apt install -y python3-tk python3-reportlab python3-pil python3-openpyxl fonts-dejavu
fi

echo "Starting Flashcard Studio..."
python3 flashcard_studio.py
