@REM ============================================================
@REM   Made by Kieranmcm07 on GitHub
@REM   GitHub: https://github.com/Kieranmcm07
@REM ============================================================
@echo off
setlocal
title Stop TimeWarp File
color 0C
cls

set "PAUSE_ON_EXIT=1"
if /I "%~1"=="/nopause" set "PAUSE_ON_EXIT=0"

echo.
echo      _____ _                __        __                  ____  _                 _ 
echo     ^|_   _(_)_ __ ___   ___ \ \      / /_ _ _ __ _ __    / ___^|^| ^| ___  ___  ___^| ^|
echo       ^| ^| ^| ^| '_ ` _ \ / _ \ \ \ /\ / / _` ^| '__^| '_ \   \___ \^| ^|/ _ \/ __^|/ _ \ ^|
echo       ^| ^| ^| ^| ^| ^| ^| ^| ^|  __/  \ V  V / (_^| ^| ^|  ^| ^|_) ^|   ___) ^| ^| (_) \__ \  __/_^|
echo       ^|_^| ^|_^|_^| ^|_^| ^|_^|\___^|   \_/\_/ \__,_^|_^|  ^| .__/   ^|____/^|_^|\___/^|___/\___(_)
echo                                                 ^|_^|                                  
echo.
echo     TimeWarp File does not stay running in the background.
echo     Close the launcher window, or press Ctrl+C in the active terminal.
echo.

if "%PAUSE_ON_EXIT%"=="1" pause
