const URL_API = "/api";

// Elemente DOM
const ecranLogin    = document.querySelector("#ecran-login");
const panouAdmin    = document.querySelector("#panou-admin");
const formLogin     = document.querySelector("#formular-login");
const eroareLogin   = document.querySelector("#eroare-login");
const formAdauga    = document.querySelector("#formular-adauga");
const mesajAdauga   = document.querySelector("#mesaj-adauga");
const mesajStergere = document.querySelector("#mesaj-stergere");
const corpTabel     = document.querySelector("#corp-tabel");
const btnLogout     = document.querySelector("#btn-logout");
const btnReincarca  = document.querySelector("#btn-reincarca");
const modalOverlay  = document.querySelector("#modal-overlay");
const formEdit      = document.querySelector("#formular-edit");
const mesajEdit     = document.querySelector("#mesaj-edit");

///////////////////////////////////////////////////////////
// Gestionare token

function salveazaToken(token) {
  localStorage.setItem("webtania_admin_token", token);
}

function obtineToken() {
  return localStorage.getItem("webtania_admin_token");
}

function stergeToken() {
  localStorage.removeItem("webtania_admin_token");
}

function headersAutorizare() {
  return {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${obtineToken()}`,
  };
}

///////////////////////////////////////////////////////////
// Afișare ecran corect

function arataPanou() {
  ecranLogin.classList.add("ascuns");
  panouAdmin.classList.remove("ascuns");
  incarcaProduse();
}

function arataLogin() {
  panouAdmin.classList.add("ascuns");
  ecranLogin.classList.remove("ascuns");
}

if (obtineToken()) {
  arataPanou();
}

///////////////////////////////////////////////////////////
// Preview imagine la selectare fișier

document.querySelector("#image-file").addEventListener("change", function () {
  const previzualizare = document.querySelector("#previzualizare-imagine");
  const fisier = this.files[0];
  if (!fisier) return;

  previzualizare.src = URL.createObjectURL(fisier);
  previzualizare.classList.remove("ascuns");
});

document.querySelector("#edit-image-file").addEventListener("change", function () {
  const previzualizare = document.querySelector("#edit-previzualizare-imagine");
  const fisier = this.files[0];
  if (!fisier) return;

  previzualizare.src = URL.createObjectURL(fisier);
});

///////////////////////////////////////////////////////////
// Upload imagine (returnează filename)

async function uploadImagine(inputFisier) {
  const fisier = inputFisier.files[0];
  if (!fisier) return null;

  const formData = new FormData();
  formData.append("fisier", fisier);

  const raspuns = await fetch(`${URL_API}/upload`, {
    method: "POST",
    headers: { "Authorization": `Bearer ${obtineToken()}` },
    body: formData,
  });

  if (!raspuns.ok) {
    const err = await raspuns.json();
    throw new Error(err.detail ?? "Eroare la încărcarea imaginii.");
  }

  const { filename } = await raspuns.json();
  return filename;
}

///////////////////////////////////////////////////////////
// Login

formLogin.addEventListener("submit", async function (e) {
  e.preventDefault();
  eroareLogin.textContent = "";

  const date = new FormData(formLogin);
  try {
    const raspuns = await fetch(`${URL_API}/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: date.get("username"),
        password: date.get("password"),
      }),
    });

    if (raspuns.ok) {
      const { token } = await raspuns.json();
      salveazaToken(token);
      arataPanou();
    } else {
      const eroare = await raspuns.json();
      eroareLogin.textContent = eroare.detail ?? "Credențiale incorecte.";
    }
  } catch {
    eroareLogin.textContent = "Nu s-a putut contacta serverul.";
  }
});

///////////////////////////////////////////////////////////
// Logout

btnLogout.addEventListener("click", async function () {
  try {
    await fetch(`${URL_API}/admin/logout`, {
      method: "POST",
      headers: headersAutorizare(),
    });
  } catch { /* ignorăm erori de rețea la logout */ }

  stergeToken();
  arataLogin();
});

///////////////////////////////////////////////////////////
// Încarcă tabelul cu produse

async function incarcaProduse() {
  corpTabel.innerHTML = `<tr><td colspan="7" class="tabel-stare">Se încarcă...</td></tr>`;

  try {
    const raspuns = await fetch(`${URL_API}/products`);
    const produse = await raspuns.json();

    if (produse.length === 0) {
      corpTabel.innerHTML = `<tr><td colspan="7" class="tabel-stare">Niciun produs în baza de date.</td></tr>`;
      return;
    }

    corpTabel.innerHTML = produse.map(p => `
      <tr>
        <td>${p.id}</td>
        <td><img class="tabel-img" src="${p.image}" alt="${p.alt}" loading="lazy" /></td>
        <td>${p.name}</td>
        <td>${p.category}</td>
        <td>${p.price.toFixed(2)} lei</td>
        <td><span class="badge ${p.isFeatured ? "badge--da" : "badge--nu"}">${p.isFeatured ? "Da" : "Nu"}</span></td>
        <td>
          <button class="btn-edit" data-id="${p.id}">Editează</button>
          <button class="btn-sterge" data-id="${p.id}" data-nume="${p.name}">Șterge</button>
        </td>
      </tr>
    `).join("");

    corpTabel.querySelectorAll(".btn-sterge").forEach(btn => {
      btn.addEventListener("click", () => stergeProdus(btn.dataset.id, btn.dataset.nume));
    });

    corpTabel.querySelectorAll(".btn-edit").forEach(btn => {
      const produs = produse.find(p => p.id === Number(btn.dataset.id));
      btn.addEventListener("click", () => deschideModal(produs));
    });

  } catch {
    corpTabel.innerHTML = `<tr><td colspan="7" class="tabel-stare">Eroare la încărcarea produselor.</td></tr>`;
  }
}

btnReincarca.addEventListener("click", incarcaProduse);

///////////////////////////////////////////////////////////
// Adaugă produs nou

formAdauga.addEventListener("submit", async function (e) {
  e.preventDefault();
  mesajAdauga.textContent = "";
  mesajAdauga.className = "mesaj";

  const date = new FormData(formAdauga);
  const inputFisier = document.querySelector("#image-file");

  try {
    // Dacă s-a selectat un fișier, îl urcăm primul
    let numeFisier = String(date.get("image")).trim();
    if (inputFisier.files[0]) {
      mesajAdauga.textContent = "Se încarcă imaginea...";
      numeFisier = await uploadImagine(inputFisier);
    }

    if (!numeFisier) {
      mesajAdauga.textContent = "Selectează o imagine.";
      mesajAdauga.className = "mesaj mesaj--eroare";
      return;
    }

    const payload = {
      name:        String(date.get("name")).trim(),
      category:    String(date.get("category")),
      price:       Number(date.get("price")),
      description: String(date.get("description")).trim(),
      image:       numeFisier,
      alt:         String(date.get("alt")).trim(),
      isFeatured:  date.get("isFeatured") === "on",
    };

    const raspuns = await fetch(`${URL_API}/products`, {
      method: "POST",
      headers: headersAutorizare(),
      body: JSON.stringify(payload),
    });

    if (raspuns.status === 201) {
      const produs = await raspuns.json();
      mesajAdauga.textContent = `✓ "${produs.name}" adăugat cu succes (ID: ${produs.id})`;
      mesajAdauga.className = "mesaj mesaj--succes";
      formAdauga.reset();
      document.querySelector("#previzualizare-imagine").classList.add("ascuns");
      incarcaProduse();
    } else if (raspuns.status === 401) {
      mesajAdauga.textContent = "Sesiune expirată. Reconectează-te.";
      mesajAdauga.className = "mesaj mesaj--eroare";
      stergeToken();
      arataLogin();
    } else {
      mesajAdauga.textContent = "Nu s-a putut adăuga produsul. Verifică datele.";
      mesajAdauga.className = "mesaj mesaj--eroare";
    }
  } catch (err) {
    mesajAdauga.textContent = err.message || "Eroare de conexiune cu serverul.";
    mesajAdauga.className = "mesaj mesaj--eroare";
  }
});

///////////////////////////////////////////////////////////
// Modal Editare

function deschideModal(produs) {
  document.querySelector("#edit-id").value          = produs.id;
  document.querySelector("#edit-name").value        = produs.name;
  document.querySelector("#edit-category").value    = produs.category;
  document.querySelector("#edit-price").value       = produs.price;
  document.querySelector("#edit-description").value = produs.description;
  document.querySelector("#edit-image").value       = produs.image;
  document.querySelector("#edit-alt").value         = produs.alt;
  document.querySelector("#edit-isFeatured").checked = produs.isFeatured;

  // Arată imaginea curentă ca preview
  const previzualizare = document.querySelector("#edit-previzualizare-imagine");
  previzualizare.src = produs.image;

  // Resetează input-ul de fișier
  document.querySelector("#edit-image-file").value = "";

  mesajEdit.textContent = "";
  mesajEdit.className = "mesaj";
  modalOverlay.classList.remove("ascuns");
}

function inchideModal() {
  modalOverlay.classList.add("ascuns");
}

document.querySelector("#modal-inchide").addEventListener("click", inchideModal);
document.querySelector("#modal-anuleaza").addEventListener("click", inchideModal);
modalOverlay.addEventListener("click", function (e) {
  if (e.target === modalOverlay) inchideModal();
});

formEdit.addEventListener("submit", async function (e) {
  e.preventDefault();
  mesajEdit.textContent = "";
  mesajEdit.className = "mesaj";

  const date = new FormData(formEdit);
  const id = date.get("id");
  const inputFisier = document.querySelector("#edit-image-file");

  try {
    // Dacă s-a selectat un fișier nou, îl urcăm
    let numeFisier = String(date.get("image")).trim();
    if (inputFisier.files[0]) {
      mesajEdit.textContent = "Se încarcă imaginea...";
      numeFisier = await uploadImagine(inputFisier);
    }

    const payload = {
      name:        String(date.get("name")).trim(),
      category:    String(date.get("category")),
      price:       Number(date.get("price")),
      description: String(date.get("description")).trim(),
      image:       numeFisier,
      alt:         String(date.get("alt")).trim(),
      isFeatured:  date.get("isFeatured") === "on",
    };

    const raspuns = await fetch(`${URL_API}/products/${id}`, {
      method: "PUT",
      headers: headersAutorizare(),
      body: JSON.stringify(payload),
    });

    if (raspuns.ok) {
      const produs = await raspuns.json();
      mesajEdit.textContent = `✓ "${produs.name}" actualizat cu succes.`;
      mesajEdit.className = "mesaj mesaj--succes";
      incarcaProduse();
      setTimeout(inchideModal, 1200);
    } else if (raspuns.status === 401) {
      mesajEdit.textContent = "Sesiune expirată. Reconectează-te.";
      mesajEdit.className = "mesaj mesaj--eroare";
      stergeToken();
      arataLogin();
    } else {
      mesajEdit.textContent = "Nu s-a putut actualiza produsul.";
      mesajEdit.className = "mesaj mesaj--eroare";
    }
  } catch (err) {
    mesajEdit.textContent = err.message || "Eroare de conexiune cu serverul.";
    mesajEdit.className = "mesaj mesaj--eroare";
  }
});

///////////////////////////////////////////////////////////
// Șterge produs

async function stergeProdus(id, nume) {
  if (!confirm(`Ești sigur că vrei să ștergi "${nume}"?`)) return;

  mesajStergere.textContent = "";
  mesajStergere.className = "mesaj";

  try {
    const raspuns = await fetch(`${URL_API}/products/${id}`, {
      method: "DELETE",
      headers: headersAutorizare(),
    });

    if (raspuns.status === 204) {
      mesajStergere.textContent = `✓ "${nume}" a fost șters.`;
      mesajStergere.className = "mesaj mesaj--succes";
      incarcaProduse();
    } else if (raspuns.status === 401) {
      mesajStergere.textContent = "Sesiune expirată. Reconectează-te.";
      mesajStergere.className = "mesaj mesaj--eroare";
      stergeToken();
      arataLogin();
    } else {
      mesajStergere.textContent = "Nu s-a putut șterge produsul.";
      mesajStergere.className = "mesaj mesaj--eroare";
    }
  } catch {
    mesajStergere.textContent = "Eroare de conexiune cu serverul.";
    mesajStergere.className = "mesaj mesaj--eroare";
  }
}
