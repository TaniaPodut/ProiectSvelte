from __future__ import annotations

import json
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import EmailStr
from sqlalchemy import func
from sqlmodel import Field, SQLModel, Session, select

import backend.database as database

# Directorul backend/ și calea către fișierul JSON cu produse
DIR_BAZA = Path(__file__).resolve().parent
FISIER_PRODUSE = DIR_BAZA / "products.json"


# --- Admin Authentication ---

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

def citeste_fisier_json(cale: Path, valoare_implicita: Any | None = None) -> Any:
    if not cale.exists():
        if valoare_implicita is None:
            raise FileNotFoundError(f"Fișierul de date lipsește: {cale}")
        cale.write_text(json.dumps(valoare_implicita, indent=2) + "\n", encoding="utf-8")
        return valoare_implicita
    return json.loads(cale.read_text(encoding="utf-8"))


def populeaza_date_initiale(sesiune: Session) -> None:
    if sesiune.exec(select(Produs).limit(1)).first() is None:
        produse_brute = citeste_fisier_json(FISIER_PRODUSE)
        produse = [Produs.model_validate(p) for p in produse_brute]
        sesiune.add_all(produse)
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


# --- Endpoints ---

@app.get("/api/status")
def obtine_status(sesiune: Session = Depends(database.obtine_sesiune)) -> dict[str, Any]:
    return {
        "status": "ok",
        "numar_produse": len(sesiune.exec(select(Produs)).all()),
        "numar_comenzi": len(sesiune.exec(select(Comanda)).all()),
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

@app.post("/api/admin/login")
def admin_login(date: DateAutentificare) -> dict[str, str]:
    if date.username != ADMIN_USERNAME or date.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizator sau parolă incorectă.",
        )
    token = secrets.token_hex(32)
    tokene_valide.add(token)
    return {"token": token}


@app.post("/api/admin/logout")
def admin_logout(credentiale: HTTPAuthorizationCredentials = Depends(security)):
    tokene_valide.discard(credentiale.credentials)
    return {"mesaj": "Deconectat cu succes."}


@app.get("/api/orders", response_model=list[Comanda], dependencies=[Depends(verifica_admin)])
def obtine_comenzi(sesiune: Session = Depends(database.obtine_sesiune)):
    return list(sesiune.exec(select(Comanda).order_by(Comanda.created_at.desc())).all())


@app.get("/api/contact", response_model=list[MesajContact], dependencies=[Depends(verifica_admin)])
def obtine_mesaje_contact(sesiune: Session = Depends(database.obtine_sesiune)):
    return list(sesiune.exec(select(MesajContact).order_by(MesajContact.id.desc())).all())


@app.post("/api/products", response_model=Produs, status_code=201, dependencies=[Depends(verifica_admin)])
def creeaza_produs(produs: ProdusBaza, sesiune: Session = Depends(database.obtine_sesiune)):
    produs_db = Produs.model_validate(produs)
    sesiune.add(produs_db)
    sesiune.commit()
    sesiune.refresh(produs_db)
    return produs_db


@app.put("/api/products/{id_produs}", response_model=Produs, dependencies=[Depends(verifica_admin)])
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


@app.delete("/api/products/{id_produs}", status_code=204, dependencies=[Depends(verifica_admin)])
def sterge_produs(id_produs: int, sesiune: Session = Depends(database.obtine_sesiune)):
    produs = sesiune.get(Produs, id_produs)
    if not produs:
        raise HTTPException(status_code=404, detail="Produs negăsit.")
    sesiune.delete(produs)
    sesiune.commit()
    return Response(status_code=204)


# --- Static Files ---
DIR_FRONTEND = DIR_BAZA.parent / "frontend"
if (DIR_FRONTEND / "index.html").exists():
    app.mount("/", StaticFiles(directory=DIR_FRONTEND, html=True), name="frontend")
