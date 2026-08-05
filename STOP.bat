@echo off
title OncoAI - Stopping...
color 0C

echo.
echo  Stopping OncoAI servers...
echo.

taskkill /f /fi "WINDOWTITLE eq OncoAI Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq OncoAI Frontend*" >nul 2>&1

echo  [Done] All servers stopped.
echo.
timeout /t 2 /nobreak >nul
