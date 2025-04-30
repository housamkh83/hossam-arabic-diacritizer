@echo off
chcp 65001
title Hossam Fadl Kaddour

cls
echo ================================================
echo   Arabic Advanced Diacritization Program
echo   Programmer: Hossam Fadl Kaddour
echo ================================================
echo.

:: Check for Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed on your system
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b
    )
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Check pip installation
if not exist "venv\Scripts\pip.exe" (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b
)

echo [INFO] Installing requirements...
:: Install required libraries
pip install -q gradio
pip install -q pyarabic
pip install -q numpy

:: Create output directory if it doesn't exist
if not exist "outputs" mkdir outputs

:: Automatically launch browser after 5 seconds
echo.
echo [INFO] Waiting for server startup...
timeout /t 5 /nobreak > nul
start http://localhost:7865

:: Launch application
echo.
echo [INFO] Starting Arabic Diacritization Program...
echo.
python app.py

:: Error handling
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] An error occurred while running the application
    echo Please verify all required files are present
    pause
)

:: Deactivate virtual environment
deactivate