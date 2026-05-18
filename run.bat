@REM ============================================================
@REM   Made by Kieranmcm07 on GitHub
@REM   GitHub: https://github.com/Kieranmcm07
@REM ============================================================
@echo off
title DateForge Timestamp Console
color 0A
mode con: cols=120 lines=32
cls
cd /d "%~dp0"

where py >nul 2>&1
if %errorlevel%==0 (
    py -3 launcher.py
) else (
    python launcher.py
)
