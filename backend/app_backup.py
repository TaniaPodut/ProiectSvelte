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
from pydantic import EmailStr
from sqlalchemy import func
from sqlmodel import Field, Session, SQLModel, select

from . import database

# Directorul backend/ și calea către fișierul JSON cu produse
DIR_BAZA = Path(__file__).resolve().parent
FISIER_PRODUSE = DIR_BAZA / "products.json"


# --- Autentificare admin ---

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "webtania2026"

# Tokene active în memorie (se resetează la repornirea serverului)
tokene_valide: set[str] = set()
security = HTTPBearer()


def verifica_admin(
    credentiale: HTTPAuthorizationCredentials = Depends(security),
) -> None:
    # Verifică dacă token-ul din header Authorization: Bearer <token> este valid
    if credentiale.credentials not in tokene_valide:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid sau expirat. Autentifică-te din nou.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# --- Modele de date ---

class ProdusBase(SQLModel):
    # Câmpurile comune folosite atât pentru validare cât și pentru baza de date
    name: str
    category: str
    price: float
    description: str
    image: str
    alt: str
    isFeatured: bool = False


class Produs(ProdusBase, table=True):
    # table=True îi spune SQLModel să creeze un tabel în baza de date
    id: int | None = Field(default=None, primary_key=True)


class ComandaBaza(SQLModel):
    # Câmpurile unei comenzi cu validări Pydantic
    contact_name: str = Field(min_length=1, max_length=100)
    contact_email: EmailStr
    contact_phone: str = Field(min_length=6, max_length=20)
    delivery_address: str = Field(min_length=5, max_length=300)
    produs_id: int
    quantity: int = Field(ge=1, le=10)
    special_requests: str | None = Field(default=None, max_length=500)


class Comanda(ComandaBaza, table=True):
    # Tabelul comenzilor în baza de date
    id: int | None = Field(default=None, primary_key=True)


class ComandaCreare(ComandaBaza):
    # Model folosit doar pentru datele primite din cererea POST (fără id)
    pass


class MesajContact(SQLModel, table=True):
    # Tabel pentru stocarea mesajelor trimise prin formularul de contact
    id: int | None = Field(default=None, primary_key=True)
    nume: str = Field(min_length=1, max_length=100)
    telefon: str = Field(default="", min_length=0, max_length=20)
    email: EmailStr
    mesaj: str = Field(min_length=1, max_length=1000)


class DateAutentificare(SQLModel):
    username: str
    password: str


# --- Funcții ajutătoare ---

def citeste_fisier_json(cale: Path, valoare_implicita: Any | None = None) -> Any:
    # Citește un fișier JSON; dacă nu există, îl creează cu valoarea implicită
    if not cale.exists():
        if valoare_implicita is None:
            raise FileNotFoundError(f"Fișierul de date lipsește: {cale}")

        cale.write_text(json.dumps(valoare_implicita, indent=2) + "\n", encoding="utf-8")
        return valoare_implicita

    return json.loads(cale.read_text(encoding="utf-8"))


def populeaza_produse(sesiune: Session) -> None:
    # Dacă tabelul este gol, importă datele din products.json (seed data)
    produs_existent = sesiune.exec(select(Produs).limit(1)).first()
    if produs_existent is not None:
        return

    produse_brute = citeste_fisier_json(FISIER_PRODUSE)
    produse = [Produs.model_validate(p) for p in produse_brute]
    sesiune.add_all(produse)
    sesiune.commit()


@asynccontextmanager
async def durata_de_viata(_: FastAPI):
    # Se execută la pornirea serverului: creează tabelele și populează produsele
    SQLModel.metadata.create_all(database.motor)

    # Migrare manuală: Adaugă coloana 'telefon' dacă nu există
    with Session(database.motor) as sesiune:
        from sqlalchemy import text
        for nume_tabel in ["mesajcontact", "mesaj_contact"]:
            try:
                sesiune.execute(text(f"ALTER TABLE {nume_tabel} ADD COLUMN telefon TEXT DEFAULT ''"))
                sesiune.commit()
                print(f"Migrare: Coloana 'telefon' a fost adaugata in tabelul {nume_tabel}.")
            except Exception as e:
                sesiune.rollback()
                # Daca eroarea nu este despre coloana existenta, o afisam (optional)
                # print(f"Info migrare {nume_tabel}: {e}")

    with Session(database.motor) as sesiune:
        populeaza_produse(sesiune)

    yield


# --- Aplicația FastAPI ---

app = FastAPI(
    title="Webtania API",
    description="API FastAPI pentru gestionarea produselor și comenzilor Webtania.",
    lifespan=durata_de_viata,
)

# Browserele blochează cererile cross-origin implicit, deci frontend-ul
# are nevoie de o regulă CORS explicită pentru a putea apela API-ul.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoint-uri ---

@app.get("/api/status")
def obtine_status(sesiune: Session = Depends(database.obtine_sesiune)) -> dict[str, Any]:
    # FastAPI serializează automat dicționarele Python în JSON
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
    # Returnează toate produsele, opțional filtrate după categorie
    interogare = select(Produs).order_by(Produs.id)

    if category is None:
        return list(sesiune.exec(interogare).all())

    categorie_normalizata = category.strip().casefold()
    interogare_filtrata = interogare.where(
        func.lower(Produs.category) == categorie_normalizata
    )
    return list(sesiune.exec(interogare_filtrata).all())


@app.get("/api/products/{id_produs}", response_model=Produs)
def obtine_produs(
    id_produs: int,
    sesiune: Session = Depends(database.obtine_sesiune),
) -> Produs:
    # Caută produsul după ID; returnează 404 dacă nu există
    produs = sesiune.get(Produs, id_produs)
    if produs is not None:
        return produs

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Produsul nu a fost găsit.",
    )


@app.post(
    "/api/orders",
    response_model=Comanda,
    status_code=status.HTTP_201_CREATED,
)
def creeaza_comanda(
    cerere_comanda: ComandaCreare,
    sesiune: Session = Depends(database.obtine_sesiune),
) -> Comanda:
    # FastAPI validează JSON-ul față de ComandaCreare înainte ca funcția să ruleze.
    if sesiune.get(Produs, cerere_comanda.produs_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produsul comandat nu a fost găsit.",
        )

    comanda = Comanda.model_validate(cerere_comanda)
    sesiune.add(comanda)
    sesiune.commit()
    sesiune.refresh(comanda)
    return comanda


@app.get(
    "/api/orders",
    response_model=list[Comanda],
    dependencies=[Depends(verifica_admin)],
)
def obtine_comenzi(
    sesiune: Session = Depends(database.obtine_sesiune),
) -> list[Comanda]:
    # Returnează comenzile din baza de date pentru panoul de administrare
    return list(sesiune.exec(select(Comanda).order_by(Comanda.id.desc())).all())


@app.post("/api/contact", status_code=status.HTTP_201_CREATED)
def trimite_mesaj_contact(
    mesaj_nou: MesajContact,
    sesiune: Session = Depends(database.obtine_sesiune),
) -> dict[str, str]:
    # Salvează un mesaj de contact în baza de date
    sesiune.add(mesaj_nou)
    sesiune.commit()
    return {"status": "success", "message": "Mesajul a fost salvat."}


@app.post("/api/admin/login")
def admin_login(date: DateAutentificare) -> dict[str, str]:
    # Verifică credențialele și returnează un token de sesiune
    if date.username != ADMIN_USERNAME or date.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nume de utilizator sau parolă incorecte.",
        )
    token = secrets.token_hex(32)
    tokene_valide.add(token)
    return {"token": token}


@app.post("/api/admin/logout")
def admin_logout(
    credentiale: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, str]:
    # Invalidează token-ul curent
    tokene_valide.discard(credentiale.credentials)
    return {"mesaj": "Deconectat cu succes."}


@app.post(
    "/api/products",
    response_model=Produs,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verifica_admin)],
)
def creeaza_produs(
    produs: ProdusBase,
    sesiune: Session = Depends(database.obtine_sesiune),
) -> Produs:
    # Adaugă un produs nou (doar admin)
    produs_nou = Produs.model_validate(produs)
    sesiune.add(produs_nou)
    sesiune.commit()
    sesiune.refresh(produs_nou)
    return produs_nou


@app.put(
    "/api/products/{id_produs}",
    response_model=Produs,
    dependencies=[Depends(verifica_admin)],
)
def actualizeaza_produs(
    id_produs: int,
    date_noi: ProdusBase,
    sesiune: Session = Depends(database.obtine_sesiune),
) -> Produs:
    # Actualizează toate câmpurile unui produs existent (doar admin)
    produs = sesiune.get(Produs, id_produs)
    if produs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produsul nu a fost găsit.",
        )
    date_actualizate = date_noi.model_dump()
    for camp, valoare in date_actualizate.items():
        setattr(produs, camp, valoare)
    sesiune.add(produs)
    sesiune.commit()
    sesiune.refresh(produs)
    return produs


@app.delete(
    "/api/products/{id_produs}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verifica_admin)],
)
def sterge_produs(
    id_produs: int,
    sesiune: Session = Depends(database.obtine_sesiune),
) -> None:
    # Șterge un produs după ID (doar admin)
    produs = sesiune.get(Produs, id_produs)
    if produs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produsul nu a fost găsit.",
        )
    sesiune.delete(produs)
    sesiune.commit()


EXTENSII_PERMISE = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


@app.post("/api/upload", dependencies=[Depends(verifica_admin)])
async def upload_imagine(fisier: UploadFile = File(...)) -> dict[str, str]:
    # Salvează imaginea în directorul static Svelte și returnează numele fișierului
    extensie = Path(fisier.filename or "").suffix.lower()
    if extensie not in EXTENSII_PERMISE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tip de fișier nepermis. Permise: {', '.join(EXTENSII_PERMISE)}",
        )

    nume_fisier = f"{uuid.uuid4().hex}{extensie}"
    DIR_FRONTEND_UPLOAD.mkdir(parents=True, exist_ok=True)
    cale_destinatie = DIR_FRONTEND_UPLOAD / nume_fisier

    with cale_destinatie.open("wb") as buffer:
        shutil.copyfileobj(fisier.file, buffer)

    return {"filename": nume_fisier}


# --- Servire fișiere statice (frontend Svelte) ---

DIR_FRONTEND_SVELTE = DIR_BAZA.parent / "frontend_svelte"
DIR_FRONTEND_BUILD = DIR_FRONTEND_SVELTE / "build"
DIR_FRONTEND_UPLOAD = DIR_FRONTEND_SVELTE / "static"

# Montăm frontend-ul Svelte DUPĂ toate rutele API, astfel încât /api/... să fie
# interceptate mai întâi de FastAPI. Rulează `npm run build` în frontend_svelte
# înainte de pornirea backend-ului pentru servire statică prin FastAPI.
app.mount("/", StaticFiles(directory=DIR_FRONTEND_BUILD, html=True), name="frontend")
