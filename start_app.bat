@echo off
setlocal
cd /d "%~dp0"
title FinData Agent Console
echo ========================================================
echo                 FinData Agent Launcher
echo ========================================================
echo.
echo Starting Streamlit server...
echo Please wait for the browser to open.
echo Do not close this window while using the application.
echo.

call uv run streamlit run gui/app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo --------------------------------------------------------
    echo Error: Application exited with code %ERRORLEVEL%
    echo --------------------------------------------------------
    pause
)
