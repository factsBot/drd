@echo off
setlocal enabledelayedexpansion

:: Set workspace directory
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

:: Ensure digests folder exists
if not exist "%PROJECT_DIR%drd-inbox-raw" (
    mkdir "%PROJECT_DIR%drd-inbox-raw"
)

:: Log file path
set "LOG_FILE=%PROJECT_DIR%drd-inbox-raw\run.log"
echo === Start News Digest Run: %date% %time% === >> "%LOG_FILE%"

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in the PATH. >> "%LOG_FILE%"
    echo Python is required to run this workflow. Please install Python.
    exit /b 1
)

:: 2. Setup Virtual Environment
if not exist "%PROJECT_DIR%.venv" (
    echo Creating virtual environment... >> "%LOG_FILE%"
    python -m venv .venv >> "%LOG_FILE%" 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment. >> "%LOG_FILE%"
        exit /b 1
    )
)

:: 3. Activate Virtual Environment
call "%PROJECT_DIR%.venv\Scripts\activate.bat" >> "%LOG_FILE%" 2>&1

:: 4. Install/Upgrade Dependencies
if exist "%PROJECT_DIR%.venv\installed.tag" (
    echo [FAST PATH] Skipping dependency check because installed.tag is present. >> "%LOG_FILE%"
) else (
    echo Checking/Installing dependencies... >> "%LOG_FILE%"
    python -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
    pip install -r "%PROJECT_DIR%requirements.txt" >> "%LOG_FILE%" 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Dependency installation failed. >> "%LOG_FILE%"
        exit /b 1
    )
    echo Tagging dependencies as installed. > "%PROJECT_DIR%.venv\installed.tag"
)

:: 5. Execute Digest Script
echo Executing digest.py %* ... >> "%LOG_FILE%"
python "%PROJECT_DIR%digest.py" %* >> "%LOG_FILE%" 2>&1

if !errorlevel! neq 0 (
    echo [ERROR] digest.py execution failed. Check run.log for details. >> "%LOG_FILE%"
    echo [ERROR] execution failed.
    exit /b 1
)

echo [SUCCESS] Daily digest successfully compiled at %time% >> "%LOG_FILE%"
echo Digest updated successfully.
exit /b 0
