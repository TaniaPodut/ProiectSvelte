@echo off
echo Pornesc terminalele pentru Webtania (Svelte)...

:: Porneste Backend
start "Webtania Backend" "C:\Program Files\Git\git-bash.exe" -c "./.venv/Scripts/python.exe -m uvicorn backend.main:app --reload; exec bash"

:: Porneste Frontend Svelte
start "Webtania Svelte" "C:\Program Files\Git\git-bash.exe" -c "cd frontend_svelte && npm run dev -- --port 5173; exec bash"

echo Terminalele au fost deschise!
timeout /t 3
