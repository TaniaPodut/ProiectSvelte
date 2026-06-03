from __future__ import annotations

import json
import secrets
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func
from sqlmodel import Session, SQLModel, select

from . import auth, database
from .models import (
    Comanda,
    ComandaCreare,
    LoginRequest,
    MesajContact,
    Produs,
    ProdusBase,
    SessionResponse,
    User,
    UserRole,
)

DIR_BAZA = Path(__file__).resolve().parent
FISIER_PRODUSE = DIR_BAZA / "products.json"


def citeste_fisier_json(cale: Path, valoare_implicita: Any | None = None) -> Any:
    if not cale.exists():
        if valoare_implicita is None:
            raise FileNotFoundError(f"Fișierul de date lipsește: {cale}")
        cale.write_text(json.dumps(valoare_implicita, indent=2) + "\n", encoding="utf-8")
        return valoare_implicita
    return json.loads(cale.read_text(encoding="utf-8"))


def populeaza_date_initiale(sesiune: Session) -> None:
    # Populează produse
    if sesiune.exec(select(Produs).limit(1)).first() is None:
        produse_brute = citeste_fisier_json(FISIER_PRODUSE)
        produse = [Produs.model_validate(p) for p in produse_brute]
        sesiune.add_all(produse)
    
    # Populează utilizatori (Admin și Manager)
    if auth.get_user_by_email(sesiune, auth.INITIAL_ADMIN_EMAIL) is None:
        auth.create_user(
            sesiune,
            email=auth.INITIAL_ADMIN_EMAIL,
            display_name="Administrator",
            password=auth.INITIAL_ADMIN_PASSWORD,
            role=UserRole.admin,
        )
    
    if auth.get_user_by_email(sesiune, auth.INITIAL_MANAGER_EMAIL) is None:
        auth.create_user(
            sesiune,
            email=auth.INITIAL_MANAGER_EMAIL,
            display_name="Manager Proiect",
            password=auth.INITIAL_MANAGER_PASSWORD,
            role=UserRole.manager,
        )
    
    sesiune.commit()


@asynccontextmanager
async def durata_de_viata(_: FastAPI):
    SQLModel.metadata.create_all(database.motor)
    with Session(database.motor) as sesiune:
        populeaza_date_initiale(sesiune)
    yield


app = FastAPI(
    title="Webtania API",
    description="API FastAPI pentru gestiunea catalogului de scaune, comenzi și staff.",
    lifespan=durata_de_viata,
)

import traceback
import sys

@app.exception_handler(Exception)
async def debug_exception_handler(request, exc):
    print(f"ERROR: {exc}", file=sys.stderr)
    traceback.print_exc()
    return HTTPException(status_code=500, detail=str(exc))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Public API ---

@app.get("/api/products", response_model=list[Produs])
def obtine_produse(
    category: str | None = Query(default=None),
    sesiune: Session = Depends(database.obtine_sesiune),
):
    interogare = select(Produs).order_by(Produs.id)
    if category:
        interogare = interogare.where(func.lower(Produs.category) == category.strip().lower())
    return list(sesiune.exec(interogare).all())


@app.get("/api/products/{id_produs}", response_model=Produs)
def obtine_produs(id_produs: int, sesiune: Session = Depends(database.obtine_sesiune)):
    produs = sesiune.get(Produs, id_produs)
    if not produs:
        raise HTTPException(status_code=404, detail="Produsul nu a fost găsit.")
    return produs


@app.post("/api/orders", response_model=Comanda, status_code=201)
def creeaza_comanda(cerere: ComandaCreare, sesiune: Session = Depends(database.obtine_sesiune)):
    if sesiune.get(Produs, cerere.produs_id) is None:
        raise HTTPException(status_code=404, detail="Produsul nu există.")
    comanda = Comanda.model_validate(cerere)
    sesiune.add(comanda)
    sesiune.commit()
    sesiune.refresh(comanda)
    return comanda


@app.post("/api/contact", status_code=201)
def trimite_mesaj_contact(mesaj: MesajContact, sesiune: Session = Depends(database.obtine_sesiune)):
    sesiune.add(mesaj)
    sesiune.commit()
    return {"status": "success"}


@app.get("/api/contact", response_model=list[MesajContact])
def obtine_mesaje_contact(
    current_user: Annotated[User, Depends(auth.require_manager_or_admin)],
    sesiune: Session = Depends(database.obtine_sesiune)
):
    return list(sesiune.exec(select(MesajContact).order_by(MesajContact.id.desc())).all())


# --- Auth API ---

@app.post("/api/auth/login", response_model=SessionResponse)
def login(request: LoginRequest, session: Session = Depends(database.obtine_sesiune)):
    user = auth.get_user_by_email(session, request.email)
    if user is None or not auth.verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail=auth.INVALID_CREDENTIALS_DETAIL)
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Contul este inactiv.")

    user_session = auth.create_user_session(session, user)
    return SessionResponse(
        session_token=user_session.token,
        user=auth.build_user_response(user)
    )


@app.post("/api/auth/logout")
def logout(
    user_session: Annotated[auth.UserSession, Depends(auth.get_current_user_session)],
    session: Session = Depends(database.obtine_sesiune)
):
    auth.revoke_user_session(session, user_session)
    return {"detail": "Deconectat cu succes."}


@app.get("/api/auth/me", response_model=auth.StaffUserRead)
def get_me(current_user: Annotated[User, Depends(auth.get_current_user)]):
    return auth.build_user_response(current_user)


# --- Protected API (Manager/Admin) ---

@app.get("/api/orders", response_model=list[Comanda])
def obtine_comenzi(
    current_user: Annotated[User, Depends(auth.require_manager_or_admin)],
    sesiune: Session = Depends(database.obtine_sesiune)
):
    return list(sesiune.exec(select(Comanda).order_by(Comanda.created_at.desc())).all())


# --- Protected API (Admin Only) ---

@app.post("/api/products", response_model=Produs, status_code=201)
def creeaza_produs(
    produs: ProdusBase,
    current_user: Annotated[User, Depends(auth.require_admin)],
    sesiune: Session = Depends(database.obtine_sesiune)
):
    produs_db = Produs.model_validate(produs)
    sesiune.add(produs_db)
    sesiune.commit()
    sesiune.refresh(produs_db)
    return produs_db


@app.put("/api/products/{id_produs}", response_model=Produs)
def actualizeaza_produs(
    id_produs: int,
    date_noi: ProdusBase,
    current_user: Annotated[User, Depends(auth.require_admin)],
    sesiune: Session = Depends(database.obtine_sesiune)
):
    produs = sesiune.get(Produs, id_produs)
    if not produs:
        raise HTTPException(status_code=404, detail="Produs negăsit.")
    for camp, valoare in date_noi.model_dump().items():
        setattr(produs, camp, valoare)
    sesiune.add(produs)
    sesiune.commit()
    sesiune.refresh(produs)
    return produs


@app.delete("/api/products/{id_produs}", status_code=204)
def sterge_produs(
    id_produs: int,
    current_user: Annotated[User, Depends(auth.require_admin)],
    sesiune: Session = Depends(database.obtine_sesiune)
):
    produs = sesiune.get(Produs, id_produs)
    if not produs:
        raise HTTPException(status_code=404, detail="Produs negăsit.")
    sesiune.delete(produs)
    sesiune.commit()


@app.get("/api/users", response_model=list[auth.StaffUserRead])
def get_all_users(
    current_user: Annotated[User, Depends(auth.require_admin)],
    session: Session = Depends(database.obtine_sesiune)
):
    return [auth.build_user_response(u) for u in session.exec(select(User)).all()]


EXTENSII_PERMISE = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
DIR_FRONTEND_SVELTE = DIR_BAZA.parent / "frontend_svelte"
DIR_FRONTEND_BUILD = DIR_FRONTEND_SVELTE / "build"
DIR_FRONTEND_UPLOAD = DIR_FRONTEND_SVELTE / "static"

@app.post("/api/upload")
async def upload_imagine(
    fisier: UploadFile = File(...),
    current_user: Annotated[User, Depends(auth.require_admin)] = None
):
    extensie = Path(fisier.filename or "").suffix.lower()
    if extensie not in EXTENSII_PERMISE:
        raise HTTPException(status_code=400, detail="Tip fișier nepermis.")
    nume_fisier = f"{uuid.uuid4().hex}{extensie}"
    DIR_FRONTEND_UPLOAD.mkdir(parents=True, exist_ok=True)
    cale = DIR_FRONTEND_UPLOAD / nume_fisier
    with cale.open("wb") as buffer:
        shutil.copyfileobj(fisier.file, buffer)
    return {"filename": nume_fisier}


# Servire Frontend
if DIR_FRONTEND_BUILD.exists():
    app.mount("/", StaticFiles(directory=DIR_FRONTEND_BUILD, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {"mesaj": "Frontend-ul nu este construit. Rulează 'npm run build' în frontend_svelte."}
