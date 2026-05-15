@REM ============================================================
@REM   Made by Kieranmcm07 on GitHub
@REM   GitHub: https://github.com/Kieranmcm07
@REM ============================================================
@echo off
setlocal
title Restart TimeWarp File
cd /d "%~dp0"

call "%~dp0stop_timewarp.bat" /nopause
echo.
echo Starting TimeWarp Again...
call "%~dp0start_timewarp.bat"
exit /b %ERRORLEVEL%
