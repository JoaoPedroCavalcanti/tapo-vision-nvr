@echo off
:: Navigate to project directory
cd /d "%~dp0"

:: Activate virtual environment
call .venv\Scripts\activate

:: Start the NVR engine in background mode
start pythonw monitor.py

exit