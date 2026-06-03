@echo off
echo Pornesc terminalele pentru Webtania (Standard)...

:: Porneste Backend
start "Webtania Backend" "C:\Program Files\Git\git-bash.exe" -c "./.venv/Scripts/python.exe -m uvicorn backend.main:app --reload; exec bash"

:: Porneste Frontend
start "Webtania Frontend" "C:\Program Files\Git\git-bash.exe" -c "./.venv/Scripts/python.exe -m http.server 5500 --directory frontend; exec bash"

echo Terminalele au fost deschise!
timeout /t 3
