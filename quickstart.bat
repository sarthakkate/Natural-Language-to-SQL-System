@echo off
REM Quick Start Script for NL2SQL System (Windows)
REM This script sets up and runs the entire pipeline

echo.
echo ============================================================
echo   NL2SQL System - Quick Start
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    exit /b 1
)

echo [1/5] Creating virtual environment...
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Virtual environment created and activated
) else (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

echo.
echo [2/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    exit /b 1
)

echo.
echo [3/5] Setting up database...
python setup_database.py
if errorlevel 1 (
    echo ERROR: Failed to create database
    exit /b 1
)

echo.
echo [4/5] Seeding agent memory...
python seed_memory.py
if errorlevel 1 (
    echo ERROR: Failed to seed memory
    exit /b 1
)

echo.
echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo [5/5] Starting API server...
echo.
echo IMPORTANT: Before starting the server, please:
echo   1. Get your Google Gemini API key from: https://aistudio.google.com/apikey
echo   2. Create a .env file with: GOOGLE_API_KEY=your-key-here
echo.
echo   Or copy .env.example to .env and edit it
echo.
echo When ready, press ENTER to start the server on http://localhost:8000
echo.
pause

echo.
echo Starting Uvicorn server...
uvicorn main:app --port 8000 --reload

pause
