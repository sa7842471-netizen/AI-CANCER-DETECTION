@echo off
title OncoAI - AI Cancer Detection System
color 0B

echo.
echo  =====================================================
echo   OncoAI - AI-Powered Multi-Cancer Detection System
echo  =====================================================
echo.

:: ── Check Python is available ────────────────────────────────────────────────
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [ERROR] Python not found in PATH.
        echo  Install from https://www.python.org/downloads/
        echo  and tick "Add Python to PATH" during setup.
        pause
        exit /b 1
    )
    set PYTHON=py
) else (
    set PYTHON=python
)
echo  Python: %PYTHON%
echo.

:: ── Kill anything already using port 5000 or 5500 ────────────────────────────
echo  [0/4] Clearing ports 5000 and 5500...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    if not "%%a"=="0" taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5500 " ^| findstr "LISTENING"') do (
    if not "%%a"=="0" taskkill /PID %%a /F >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo  Ports cleared.
echo.

:: ── Install dependencies ──────────────────────────────────────────────────────
echo  [1/4] Verifying Python packages...
%PYTHON% -m pip install -q -r "%~dp0backend\requirements.txt"
echo.

:: ── Start Flask backend ───────────────────────────────────────────────────────
echo  [2/4] Starting Flask Backend on port 5000...
start "OncoAI Backend" cmd /k "cd /d %~dp0backend && %PYTHON% app.py"

echo  Waiting for backend to load (EfficientNet download may take a moment)...
timeout /t 12 /nobreak >nul

:: ── Start frontend HTTP server ────────────────────────────────────────────────
echo  [3/4] Starting Frontend on port 5500...
start "OncoAI Frontend" cmd /k "cd /d %~dp0 && %PYTHON% -m http.server 5500"

timeout /t 3 /nobreak >nul

:: ── Open browser ──────────────────────────────────────────────────────────────
echo  [4/4] Opening browser...
start http://localhost:5500

echo.
echo  =====================================================
echo   System is running!
echo   Frontend : http://localhost:5500
echo   Backend  : http://localhost:5000
echo   Health   : http://localhost:5000/api/health
echo  =====================================================
echo.
echo  Two server windows are open. Close them to stop.
echo  Press any key to close this launcher...
pause >nul
