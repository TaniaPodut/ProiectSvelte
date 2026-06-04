from __future__ import annotations

import json
import secrets
import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, status, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy import func
from sqlmodel import Field, SQLModel, Session, select

import backend.database as database

# --- Configuration ---
SECRET_KEY = "webtania_secret_key_super_secret_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 ore

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Directorul backend/ și calea către fișierul JSON cu produse
DIR_BAZA = Path(__file__).resolve().parent
FISIER_PRODUSE = DIR_BAZA / "products.json"


# --- Admin Authentication (Legacy/Placeholder) ---
# We will keep these for now but move to DB based auth
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "webtania2026"


# Token-uri active în memorie (se resetează la repornirea serverului)
tokene_valide: set[str] = set()
security = HTTPBearer()


def verifica_admin(
    credentiale: HTTPAuthorizationCredentials = Depends(security),
) -> None:
    # Verifică dacă token-ul din header-ul Authorization: Bearer <token> este valid
    if credentiale.credentials not in tokene_valide:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid sau expirat. Autentifică-te din nou.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Data Models ---

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    display_name: str
    hashed_password: str
    role: str = Field(default="client")  # 'admin', 'manager', 'client'
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class ProdusBaza(SQLModel):
    name: str
    category: str
    price: float
    description: str
    image: str
    alt: str
    isFeatured: bool = False


class Produs(ProdusBaza, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ComandaBaza(SQLModel):
    contact_name: str = Field(min_length=1, max_length=100)
    contact_email: EmailStr
    contact_phone: str = Field(min_length=6, max_length=20)
    delivery_address: str = Field(min_length=5, max_length=300)
    produs_id: int
    quantity: int = Field(ge=1, le=10)
    special_requests: str | None = Field(default=None, max_length=500)


class Comanda(ComandaBaza, table=True):
    id: int | None = Field(default=None, primary_key=True)
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class ComandaCreare(ComandaBaza):
    pass


class MesajContact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nume: str = Field(min_length=1, max_length=100)
    telefon: str = Field(default="", max_length=20)
    email: EmailStr
    mesaj: str = Field(min_length=1, max_length=1000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


class DateAutentificare(SQLModel):
    username: str
    password: str


# --- Helper Functions ---

def obtine_hash_parola(parola: str) -> str:
    return pwd_context.hash(parola)


def verifica_parola(parola_simpla: str, parola_hash: str) -> bool:
    return pwd_context.verify(parola_simpla, parola_hash)


def creeaza_token_acces(date: dict, expire_delta: timedelta | None = None) -> str:
    date_copie = date.copy()
    if expire_delta:
        expira = datetime.now(timezone.utc) + expire_delta
    else:
        expira = datetime.now(timezone.utc) + timedelta(minutes=15)
    date_copie.update({"exp": expira})
    return jwt.encode(date_copie, SECRET_KEY, algorithm=ALGORITHM)


def obtine_utilizator_curent(
    credentiale: HTTPAuthorizationCredentials = Depends(security),
    sesiune: Session = Depends(database.obtine_sesiune)
) -> User:
    token = credentiale.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalid.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid sau expirat.")
    
    utilizator = sesiune.exec(select(User).where(User.username == username)).first()
    if utilizator is None:
        raise HTTPException(status_code=401, detail="Utilizator negăsit.")
    return utilizator


def verifica_rol(roluri_permise: list[str]):
    def verificare(utilizator: User = Depends(obtine_utilizator_curent)):
        if utilizator.role not in roluri_permise:
            raise HTTPException(
                status_code=403,
                detail=f"Acces interzis. Roluri permise: {', '.join(roluri_permise)}"
            )
        return utilizator
    return verificare


def populeaza_date_initiale(sesiune: Session) -> None:
    # Populează produse
    if sesiune.exec(select(Produs).limit(1)).first() is None:
        produse_brute = citeste_fisier_json(FISIER_PRODUSE)
        produse = [Produs.model_validate(p) for p in produse_brute]
        sesiune.add_all(produse)
        sesiune.commit()
    
    # Populează utilizator admin implicit
    if sesiune.exec(select(User).where(User.username == "admin")).first() is None:
        admin = User(
            username="admin",
            display_name="Administrator",
            hashed_password=obtine_hash_parola("webtania2026"),
            role="admin"
        )
        sesiune.add(admin)
    
    # Populează utilizator manager implicit
    if sesiune.exec(select(User).where(User.username == "manager")).first() is None:
        manager = User(
            username="manager",
            display_name="Manager Proiect",
            hashed_password=obtine_hash_parola("manager2026"),
            role="manager"
        )
        sesiune.add(manager)

    # Populează utilizator client implicit
    if sesiune.exec(select(User).where(User.username == "client")).first() is None:
        client = User(
            username="client",
            display_name="Client Test",
            hashed_password=obtine_hash_parola("client2026"),
            role="client"
        )
        sesiune.add(client)

    sesiune.commit()


@asynccontextmanager
async def durata_de_viata(_: FastAPI):
    SQLModel.metadata.create_all(database.motor)
    with Session(database.motor) as sesiune:
        populeaza_date_initiale(sesiune)
    yield


# --- FastAPI Application ---

app = FastAPI(
    title="Webtania API",
    description="API FastAPI pentru gestiunea catalogului de scaune și comenzi.",
    lifespan=durata_de_viata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Authentication & User Endpoints ---

@app.post("/api/admin/login")
@app.post("/api/auth/login")
def login(date: DateAutentificare, sesiune: Session = Depends(database.obtine_sesiune)) -> dict[str, str]:
    utilizator = sesiune.exec(select(User).where(User.username == date.username)).first()
    if not utilizator or not verifica_parola(date.password, utilizator.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizator sau parolă incorectă.",
        )
    
    token = creeaza_token_acces(date={"sub": utilizator.username, "role": utilizator.role})
    return {"token": token, "role": utilizator.role, "display_name": utilizator.display_name}


@app.post("/api/auth/register", status_code=201)
def inregistrare(user: User, sesiune: Session = Depends(database.obtine_sesiune)):
    # Verifică dacă există deja
    existent = sesiune.exec(select(User).where(User.username == user.username)).first()
    if existent:
        raise HTTPException(status_code=400, detail="Acest utilizator există deja.")
    
    # Doar adminul poate crea alți admini sau manageri prin acest endpoint (opțional)
    # Aici forțăm rolul de 'client' pentru înregistrări publice
    parola_simpla = user.hashed_password # Pydantic va valida obiectul înainte
    user.hashed_password = obtine_hash_parola(parola_simpla)
    user.role = "client"
    
    sesiune.add(user)
    sesiune.commit()
    sesiune.refresh(user)
    return {"mesaj": "Cont creat cu succes.", "username": user.username}


@app.get("/api/auth/me")
def obtine_profil(utilizator: User = Depends(obtine_utilizator_curent)):
    return utilizator


# --- Endpoints ---

@app.get("/api/status")
def obtine_status(sesiune: Session = Depends(database.obtine_sesiune)) -> dict[str, Any]:
    return {
        "status": "ok",
        "numar_produse": len(sesiune.exec(select(Produs)).all()),
        "numar_comenzi": len(sesiune.exec(select(Comanda)).all()),
        "numar_utilizatori": len(sesiune.exec(select(User)).all()),
    }


@app.get("/api/products", response_model=list[Produs])
def obtine_produse(
    category: str | None = Query(default=None),
    sesiune: Session = Depends(database.obtine_sesiune),
) -> list[Produs]:
    interogare = select(Produs).order_by(Produs.id)
    if category:
        interogare = interogare.where(func.lower(Produs.category) == category.strip().lower())
    return list(sesiune.exec(interogare).all())


@app.get("/api/products/{id_produs}", response_model=Produs)
def obtine_produs(id_produs: int, sesiune: Session = Depends(database.obtine_sesiune)) -> Produs:
    produs = sesiune.get(Produs, id_produs)
    if not produs:
        raise HTTPException(status_code=404, detail="Produsul nu a fost găsit.")
    return produs


@app.post("/api/orders", response_model=Comanda, status_code=201)
def creeaza_comanda(cerere: ComandaCreare, sesiune: Session = Depends(database.obtine_sesiune)) -> Comanda:
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


# --- Admin API ---

@app.get("/api/orders", response_model=list[Comanda], dependencies=[Depends(verifica_rol(["admin", "manager"]))])
def obtine_comenzi(sesiune: Session = Depends(database.obtine_sesiune)):
    return list(sesiune.exec(select(Comanda).order_by(Comanda.created_at.desc())).all())


@app.get("/api/contact", response_model=list[MesajContact], dependencies=[Depends(verifica_rol(["admin", "manager"]))])
def obtine_mesaje_contact(sesiune: Session = Depends(database.obtine_sesiune)):
    return list(sesiune.exec(select(MesajContact).order_by(MesajContact.id.desc())).all())


@app.post("/api/products", response_model=Produs, status_code=201, dependencies=[Depends(verifica_rol(["admin"]))])
def creeaza_produs(produs: ProdusBaza, sesiune: Session = Depends(database.obtine_sesiune)):
    produs_db = Produs.model_validate(produs)
    sesiune.add(produs_db)
    sesiune.commit()
    sesiune.refresh(produs_db)
    return produs_db


@app.put("/api/products/{id_produs}", response_model=Produs, dependencies=[Depends(verifica_rol(["admin"]))])
def actualizeaza_produs(id_produs: int, date_noi: ProdusBaza, sesiune: Session = Depends(database.obtine_sesiune)):
    produs = sesiune.get(Produs, id_produs)
    if not produs:
        raise HTTPException(status_code=404, detail="Produs negăsit.")
    for camp, valoare in date_noi.model_dump().items():
        setattr(produs, camp, valoare)
    sesiune.add(produs)
    sesiune.commit()
    sesiune.refresh(produs)
    return produs


@app.delete("/api/products/{id_produs}", status_code=204, dependencies=[Depends(verifica_rol(["admin"]))])
def sterge_produs(id_produs: int, sesiune: Session = Depends(database.obtine_sesiune)):
    produs = sesiune.get(Produs, id_produs)
    if not produs:
        raise HTTPException(status_code=404, detail="Produs negăsit.")
    sesiune.delete(produs)
    sesiune.commit()
    return Response(status_code=204)


@app.post("/api/upload", dependencies=[Depends(verifica_rol(["admin", "manager"]))])
def upload_imagine(fisier: UploadFile = File(...)):
    if not fisier.filename:
        raise HTTPException(status_code=400, detail="Nu s-a trimis niciun fișier.")
    
    nume_fisier = fisier.filename
    DIR_FRONTEND_SVELTE_STATIC = DIR_BAZA.parent / "frontend_svelte" / "static"
    DIR_FRONTEND = DIR_BAZA.parent / "frontend"
    
    cale_salvare_1 = DIR_FRONTEND / nume_fisier
    cale_salvare_2 = DIR_FRONTEND_SVELTE_STATIC / nume_fisier
    
    with open(cale_salvare_1, "wb") as buffer:
        shutil.copyfileobj(fisier.file, buffer)
        
    if DIR_FRONTEND_SVELTE_STATIC.exists():
        shutil.copy(cale_salvare_1, cale_salvare_2)
        
    return {"filename": nume_fisier}


# --- Static Files ---
DIR_FRONTEND = DIR_BAZA.parent / "frontend"
if (DIR_FRONTEND / "index.html").exists():
    app.mount("/", StaticFiles(directory=DIR_FRONTEND, html=True), name="frontend")
