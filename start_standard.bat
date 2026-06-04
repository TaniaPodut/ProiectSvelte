@echo off
echo Pornesc Webtania (Standard)...

:: Porneste Backend (care serveste si frontend-ul)
start "Webtania Backend" "C:\Program Files\Git\git-bash.exe" -c "./.venv/Scripts/python.exe -m uvicorn backend.main:app --reload; exec bash"

echo.
echo ========================================================
echo Serverul se porneste! 
echo Deschide in browser: http://127.0.0.1:8000/
echo ========================================================
echo.
timeout /t 3
