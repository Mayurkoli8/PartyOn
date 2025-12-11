@echo off
setlocal enabledelayedexpansion
title Sexy Audio Streamer

:: Colors for output
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

echo.
echo %CYAN%========================================%RESET%
echo %CYAN%   Sexy Audio Streamer - Setup%RESET%
echo %CYAN%========================================%RESET%
echo.

:: Check if running on Windows
ver | find "Windows" >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR] This script requires Windows.%RESET%
    echo Please use sexy_audio.sh for Linux/macOS:
    echo   chmod +x sexy_audio.sh
    echo   ./sexy_audio.sh
    pause
    exit /b 1
)
echo %GREEN%[OK]%RESET% Windows detected

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
echo %GREEN%[OK]%RESET% Working directory: %SCRIPT_DIR%

:: Check for Python
where python >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR] Python not found in PATH.%RESET%
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%[OK]%RESET% Python %PYTHON_VERSION% found

:: Check/Create virtual environment
set "VENV_DIR=%SCRIPT_DIR%sound"
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo %YELLOW%[INFO]%RESET% Creating virtual environment...
    python -m venv sound
    if errorlevel 1 (
        echo %RED%[ERROR] Failed to create virtual environment.%RESET%
        pause
        exit /b 1
    )
    echo %GREEN%[OK]%RESET% Virtual environment created
)

:: Activate virtual environment
echo %YELLOW%[INFO]%RESET% Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo %RED%[ERROR] Failed to activate virtual environment.%RESET%
    pause
    exit /b 1
)
echo %GREEN%[OK]%RESET% Virtual environment activated

:: Check/Install dependencies
echo %YELLOW%[INFO]%RESET% Checking dependencies...
pip show sounddevice >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%[INFO]%RESET% Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo %RED%[ERROR] Failed to install dependencies.%RESET%
        pause
        exit /b 1
    )
)
echo %GREEN%[OK]%RESET% Dependencies installed

:: Check for required files
if not exist "%SCRIPT_DIR%server.py" (
    echo %RED%[ERROR] server.py not found.%RESET%
    pause
    exit /b 1
)
if not exist "%SCRIPT_DIR%client.html" (
    echo %RED%[ERROR] client.html not found.%RESET%
    pause
    exit /b 1
)
if not exist "%SCRIPT_DIR%src\config.py" (
    echo %RED%[ERROR] src/config.py not found. Project structure incomplete.%RESET%
    pause
    exit /b 1
)
echo %GREEN%[OK]%RESET% Required files present

:: Display network info
echo.
echo %CYAN%========================================%RESET%
echo %CYAN%   Network Information%RESET%
echo %CYAN%========================================%RESET%
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "IP=%%a"
    set "IP=!IP:~1!"
    echo %GREEN%[IP]%RESET% !IP!
)
echo.
echo %YELLOW%Clients can connect at: http://YOUR_IP:5000%RESET%
echo.

:: Start server loop
:loop
echo.
echo %CYAN%========================================%RESET%
echo %CYAN%   Starting Audio Server...%RESET%
echo %CYAN%========================================%RESET%
echo.

python server.py

set EXIT_CODE=%errorlevel%
echo.
if %EXIT_CODE% equ 0 (
    echo %GREEN%[INFO]%RESET% Server stopped gracefully.
    goto end
) else (
    echo %YELLOW%[WARN]%RESET% Server exited with code %EXIT_CODE%
    echo Restarting in 3 seconds... ^(Press Ctrl+C to exit^)
    timeout /t 3 >nul
    goto loop
)

:end
echo.
echo %GREEN%Goodbye!%RESET%
pause
exit /b 0
