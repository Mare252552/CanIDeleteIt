@echo off
chcp 65001 >nul
title Can I Delete It?

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found.
    echo Install Python 3.10+ and enable "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

python "%~dp0main.py"
