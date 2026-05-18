@REM ============================================================
@REM   Made by Kieranmcm07 on GitHub
@REM   GitHub: https://github.com/Kieranmcm07
@REM ============================================================
@echo off
title DateForge
cd /d "%~dp0"

where py >nul 2>&1
if %errorlevel%==0 (
    py -3 launcher.py
) else (
    python launcher.py
)
