@echo off
chcp 65001 >nul
title Can I Delete It? - Setup

echo Installing required Python package...
python -m pip install -r "%~dp0requirements.txt"

echo.
echo Done.
echo You can now run:
echo   canidelete
echo.
pause
