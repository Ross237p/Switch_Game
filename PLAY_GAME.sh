#!/bin/bash
# Mac/Linux Launcher for Switch Card Game
# Just double-click this file to play!

echo ""
echo "===================================="
echo "    Starting Switch Card Game"
echo "===================================="
echo ""

# Try python3 first, then python
if command -v python3 &> /dev/null
then
    python3 main.py
elif command -v python &> /dev/null
then
    python main.py
else
    echo "ERROR: Python is not installed!"
    echo "Please install Python from https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi
