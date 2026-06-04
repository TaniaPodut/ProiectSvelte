# Webtania - Magazin de Scaune (Pattern Omnifood)

Aplicație web modernă realizată cu SvelteKit, FastAPI și SQLModel, urmând arhitectura proiectului Omnifood-FastAPI.

## Structură Proiect

- `backend/` - API-ul FastAPI și gestiunea bazei de date.
- `frontend_svelte/` - Aplicația modernă SvelteKit.
- `frontend/` - Versiunea legacy (statică).

## Tehnologii

- **Backend:** Python, FastAPI, SQLModel (SQLite).
- **Frontend:** SvelteKit, Vite, CSS modern.
- **Autentificare:** Token-based (Bearer), gestionat în memorie.

## Pornire Proiect

### Backend
```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend_svelte
npm install
npm run dev
```

## Conturi de test

### Admin
- **Utilizator:** `admin`
- **Parola:** `webtania2026`
- **Dashboard:** `/admin`

### Manager
- **Utilizator:** `manager`
- **Parola:** `manager2026`
- **Dashboard:** `/manager`

### Client
- **Utilizator:** `client`
- **Parola:** `client2026`
- **Dashboard:** `/client`
