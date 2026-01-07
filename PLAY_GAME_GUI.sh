#!/bin/bash
# Mac/Linux GUI Launcher for Switch Card Game
# Just double-click this file to play with graphics!

# Try python3 first, then python
if command -v python3 &> /dev/null
then
    python3 main_gui.py
elif command -v python &> /dev/null
then
    python main_gui.py
else
    echo "ERROR: Python is not installed!"
    echo "Please install Python from https://www.python.org/downloads/"
    read -p "Press Enter to exit..."
    exit 1
fi
