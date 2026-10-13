@echo off
title OncoAI — AI Multi-Cancer Detection System | Phase-2
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║       OncoAI — AI-Powered Multi-Cancer Detection System      ║
echo  ║       Batch 2026-27 ^| 7th Semester ^| Phase-2 Final Review   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM ── Check Python ──────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

REM ── Navigate to backend ────────────────────────────────────────────
cd /d "%~dp0backend"

REM ── Check .env exists ──────────────────────────────────────────────
if not exist .env (
    echo [SETUP] .env not found. Copying from .env.example...
    copy .env.example .env
    echo [SETUP] Please edit backend\.env with your API keys before continuing.
    echo         Required: HF_TOKEN, GROQ_API_KEY, JWT_SECRET_KEY
    pause
)

REM ── Check dependencies ─────────────────────────────────────────────
echo [INFO] Checking Python dependencies...
python -c "import flask, torch, groq" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM ── Create required directories ────────────────────────────────────
if not exist models mkdir models
if not exist data   mkdir data
if not exist logs   mkdir logs

echo.
echo  Modules Status:
python -c "import security;     print('  [OK] security.py      (JWT, AES-256, OTP)')" 2>nul || echo   [--] security.py      (run: pip install PyJWT cryptography bcrypt pyotp)
python -c "import dicom_handler;print('  [OK] dicom_handler.py (DICOM support)')"      2>nul || echo   [--] dicom_handler.py (run: pip install pydicom)
python -c "import lime;         print('  [OK] lime_explainer.py(LIME XAI)')"           2>nul || echo   [--] lime_explainer.py(run: pip install lime scikit-image)
python -c "import reportlab;    print('  [OK] report_generator (PDF reports)')"        2>nul || echo   [--] report_generator  (run: pip install reportlab)
python -c "import tensorflow;   print('  [OK] ids_module.py    (AI-IDS TF)')"          2>nul || echo   [--] ids_module.py    (run: pip install tensorflow)

echo.
echo  ══════════════════════════════════════════════════
echo  Starting Flask Backend on http://localhost:5000
echo  ══════════════════════════════════════════════════
echo.

REM ── Start Flask backend in a new window ───────────────────────────
start "OncoAI Backend" cmd /k "title OncoAI Backend ^| Port 5000 && python app.py"

REM ── Wait for backend to start ─────────────────────────────────────
timeout /t 4 /nobreak >nul

REM ── Open frontend in browser ──────────────────────────────────────
cd /d "%~dp0"
echo  Opening frontend at http://localhost:5000
start "" "http://localhost:5000"

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║  OncoAI is running!                                          ║
echo  ║                                                              ║
echo  ║  Frontend : http://localhost:5000  (served by Flask)         ║
echo  ║  API Base : http://localhost:5000/api/                       ║
echo  ║  Health   : http://localhost:5000/api/health                 ║
echo  ║                                                              ║
echo  ║  Default credentials:                                        ║
echo  ║    Admin/Specialist  →  admin   / admin123                   ║
echo  ║    Patient           →  patient / patient123                 ║
echo  ║                                                              ║
echo  ║  Press STOP.bat to shut down all services.                   ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.
pause
