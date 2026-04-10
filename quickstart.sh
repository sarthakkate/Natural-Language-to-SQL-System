#!/bin/bash

# Quick Start Script for NL2SQL System (macOS/Linux)
# This script sets up and runs the entire pipeline

echo ""
echo "============================================================"
echo "  NL2SQL System - Quick Start"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python 3.10+ from python.org"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    echo "Virtual environment created and activated"
else
    source venv/bin/activate
    echo "Virtual environment activated"
fi

echo ""
echo "[2/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[3/5] Setting up database..."
python3 setup_database.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create database"
    exit 1
fi

echo ""
echo "[4/5] Seeding agent memory..."
python3 seed_memory.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to seed memory"
    exit 1
fi

echo ""
echo "============================================================"
echo "  Setup Complete!"
echo "============================================================"
echo ""
echo "[5/5] Starting API server..."
echo ""
echo "IMPORTANT: Before starting the server, please:"
echo "  1. Get your Google Gemini API key from: https://aistudio.google.com/apikey"
echo "  2. Create a .env file with: GOOGLE_API_KEY=your-key-here"
echo ""
echo "  Or copy .env.example to .env and edit it"
echo ""
echo "The server will start on http://localhost:8000"
echo "Press ENTER to continue..."
read

echo ""
echo "Starting Uvicorn server..."
uvicorn main:app --port 8000 --reload
