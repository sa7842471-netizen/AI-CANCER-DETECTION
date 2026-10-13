@echo off
setlocal EnableDelayedExpansion
title OncoAI ^| AI Multi-Cancer Detection ^| Phase-2 Setup Wizard
color 0A

:: ════════════════════════════════════════════════════════════════════
::  OncoAI — AI-Powered Multi-Cancer Detection System
::  Batch 2026-27 ^| Odd Semester ^| 7th Sem ^| B.Tech CSE (AI & ML)
::  Phase-2 Final Review
:: ════════════════════════════════════════════════════════════════════

echo.
echo  +=============================================================+
echo  ^|   OncoAI - AI Multi-Cancer Detection System                 ^|
echo  ^|   Batch: 2026-27  ^|  7th Sem  ^|  Phase-2 Final Review      ^|
echo  +=============================================================+
echo.

:: ── STEP 0: Check Python ─────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  [ERROR] Python is NOT installed or not in PATH.
    echo  Please install Python 3.11+ from https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo  [OK] %PY_VER% detected.

:: ── STEP 1: Navigate to backend ──────────────────────────────────────
cd /d "%~dp0backend"

:: ── STEP 2: Auto-create .env from .env.example if missing ────────────
if not exist .env (
    echo.
    echo  [SETUP] First run detected — creating .env from template...
    copy .env.example .env >nul
    echo  [SETUP] .env created at: %CD%\.env
    echo.

    :: Auto-inject pre-generated secure tokens into .env
    echo  [SETUP] Injecting pre-generated secure tokens...

    :: JWT Secret Key (64-char hex)
    set JWT=fb64faf8955fbd35fb363acfb61082344d3b634bb6da41dd37ed903e4c3517f2
    powershell -Command "(Get-Content .env) -replace 'your_jwt_secret_key_here_min_32_chars', '!JWT!' | Set-Content .env"

    :: AES-256 Encryption Key (64-char hex = 32 bytes)
    set AES=431f1d95410ec3101202d313c16bf21c895843235223c1697f9b7e27a1c03706
    powershell -Command "(Get-Content .env) -replace 'your_32_byte_hex_encryption_key_here', '!AES!' | Set-Content .env"

    echo  [OK] JWT_SECRET_KEY and AES_ENCRYPTION_KEY auto-set.
    echo.
    color 0E
    echo  +=============================================================+
    echo  ^|  ACTION REQUIRED: Add your FREE API keys to:               ^|
    echo  ^|  backend\.env                                               ^|
    echo  ^|                                                             ^|
    echo  ^|  1. HF_TOKEN  → https://huggingface.co/settings/tokens     ^|
    echo  ^|     (Click "New token" → Read access → Copy)               ^|
    echo  ^|                                                             ^|
    echo  ^|  2. GROQ_API_KEY → https://console.groq.com/keys           ^|
    echo  ^|     (Click "Create API Key" → Copy)                        ^|
    echo  ^|                                                             ^|
    echo  ^|  Both are 100%% FREE with no credit card required.          ^|
    echo  +=============================================================+
    echo.
    color 0A

    :: Open token pages automatically in browser
    echo  [INFO] Opening token pages in your browser...
    timeout /t 1 /nobreak >nul
    start "" "https://huggingface.co/settings/tokens"
    timeout /t 1 /nobreak >nul
    start "" "https://console.groq.com/keys"
    echo.

    :: Open the .env file in Notepad for editing
    echo  [INFO] Opening backend\.env in Notepad for you to paste keys...
    timeout /t 2 /nobreak >nul
    start notepad.exe .env

    echo.
    echo  Paste your HF_TOKEN and GROQ_API_KEY into Notepad, save the file,
    echo  then press any key here to continue launching the server.
    echo.
    pause
)

:: ── STEP 3: Check if keys are set ────────────────────────────────────
echo.
echo  [INFO] Verifying API key configuration...
findstr /C:"hf_your_huggingface_token_here" .env >nul 2>&1
if not errorlevel 1 (
    color 0E
    echo  [WARN] HF_TOKEN not set in .env — image models will use fallback/demo mode.
    color 0A
) else (
    echo  [OK] HF_TOKEN is configured.
)

findstr /C:"gsk_your_groq_api_key_here" .env >nul 2>&1
if not errorlevel 1 (
    color 0E
    echo  [WARN] GROQ_API_KEY not set in .env — symptom checker and chatbot will be unavailable.
    color 0A
) else (
    echo  [OK] GROQ_API_KEY is configured.
)

:: ── STEP 4: Create required directories ──────────────────────────────
if not exist models mkdir models >nul 2>&1
if not exist data   mkdir data   >nul 2>&1
if not exist logs   mkdir logs   >nul 2>&1

:: ── STEP 5: Install / verify dependencies ────────────────────────────
echo.
echo  [INFO] Checking core Python dependencies...
python -c "import flask, torch, groq" >nul 2>&1
if errorlevel 1 (
    echo  [SETUP] Core dependencies missing. Installing from requirements.txt...
    echo  [INFO]  This may take 5-10 minutes on first run.
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo  [ERROR] Failed to install dependencies. Check pip and internet connection.
        pause
        exit /b 1
    )
    echo.
    echo  [OK] All dependencies installed.
) else (
    echo  [OK] Core dependencies already installed.
)

:: ── STEP 6: Module availability check ────────────────────────────────
echo.
echo  ── Module Status ──────────────────────────────────────────────
python -c "import security"       >nul 2>&1 && echo  [OK] security.py        JWT / AES-256-GCM / bcrypt / OTP     || echo  [--] security.py        (pip install PyJWT cryptography bcrypt pyotp)
python -c "import pydicom"        >nul 2>&1 && echo  [OK] dicom_handler.py   DICOM image support                   || echo  [--] dicom_handler.py   (pip install pydicom)
python -c "import lime"           >nul 2>&1 && echo  [OK] lime_explainer.py  LIME superpixel XAI                   || echo  [--] lime_explainer.py  (pip install lime scikit-image)
python -c "import reportlab"      >nul 2>&1 && echo  [OK] report_generator   PDF clinical report                   || echo  [--] report_generator   (pip install reportlab)
python -c "import tensorflow"     >nul 2>&1 && echo  [OK] ids_module.py      AI-IDS TensorFlow (NSL-KDD)           || echo  [--] ids_module.py      (pip install tensorflow)
python -c "import transformers"   >nul 2>&1 && echo  [OK] BERT Transformers  Symptom NLP classifier                || echo  [--] BERT Transformers  (pip install transformers)
python -c "import scapy"          >nul 2>&1 && echo  [OK] Scapy              Live network packet capture            || echo  [--] Scapy              (pip install scapy)
echo  ────────────────────────────────────────────────────────────────

:: ── STEP 7: Start Flask backend ──────────────────────────────────────
echo.
echo  [LAUNCH] Starting Flask backend on http://localhost:5000 ...
echo.

start "OncoAI Backend - Port 5000" cmd /k "title OncoAI Backend ^| Port 5000 ^| Phase-2 && color 0B && echo. && echo  OncoAI Backend starting... && echo. && python app.py"

:: Wait for Flask to boot
echo  [INFO] Waiting for server to start...
timeout /t 5 /nobreak >nul

:: ── STEP 8: Open browser ─────────────────────────────────────────────
cd /d "%~dp0"
start "" "http://localhost:5000"

:: ── STEP 9: Show status ───────────────────────────────────────────────
echo.
echo  +=============================================================+
echo  ^|                                                             ^|
echo  ^|   OncoAI is now RUNNING!                                    ^|
echo  ^|                                                             ^|
echo  ^|   App        : http://localhost:5000                        ^|
echo  ^|   API Health : http://localhost:5000/api/health             ^|
echo  ^|   API Models : http://localhost:5000/api/models             ^|
echo  ^|                                                             ^|
echo  ^|   DEFAULT CREDENTIALS:                                      ^|
echo  ^|     Admin / Specialist : admin    / admin123                ^|
echo  ^|     Patient            : patient  / patient123              ^|
echo  ^|                                                             ^|
echo  ^|   SECURITY TOKENS (auto-generated, in backend\.env):       ^|
echo  ^|     JWT_SECRET_KEY    - 64-char hex (30-min session)        ^|
echo  ^|     AES_ENCRYPTION_KEY - 64-char hex (256-bit encryption)   ^|
echo  ^|                                                             ^|
echo  ^|   Run STOP.bat to shut down the server.                     ^|
echo  ^|                                                             ^|
echo  +=============================================================+
echo.
echo  Press any key to close this setup window (server keeps running).
pause >nul
