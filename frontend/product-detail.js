const URL_API = "/api";
const continut = document.querySelector("#continut-detaliu");

document.querySelector("#an-curent").textContent = new Date().getFullYear();

async function incarcaDetaliu() {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");

  if (!id) {
    continut.innerHTML = `
      <a href="/products" class="detaliu-inapoi">&larr; Înapoi la produse</a>
      <p class="stare-incarcare">ID lipsă. <a href="/products">Vezi toate produsele.</a></p>
    `;
    return;
  }

  try {
    const raspuns = await fetch(`${URL_API}/products/${id}`);

    if (raspuns.status === 404) {
      continut.innerHTML = `
        <a href="/products" class="detaliu-inapoi">&larr; Înapoi la produse</a>
        <p class="stare-incarcare">Produsul cu ID-ul ${id} nu a fost găsit.</p>
      `;
      return;
    }

    const produs = await raspuns.json();
    document.title = `Magazin de Scaune — ${produs.name}`;

    continut.innerHTML = `
      <a href="/products" class="detaliu-inapoi">&larr; Înapoi la produse</a>
      <div class="detaliu-grid">
        <div class="detaliu-img-container">
          <img src="${produs.image}" alt="${produs.alt}" />
        </div>
        <div class="detaliu-info">
          <div>
            <span class="detaliu-eticheta">${produs.category}</span>
            ${produs.isFeatured ? '<span class="detaliu-featured">⭐ Featured</span>' : ""}
          </div>
          <h1 class="detaliu-titlu">${produs.name}</h1>
          <p class="detaliu-descriere">${produs.description}</p>
          <p class="detaliu-pret">${produs.price.toFixed(2)} lei</p>
          <a href="/#" class="detaliu-btn">Adaugă în coș &rarr;</a>
        </div>
      </div>
    `;
  } catch {
    continut.innerHTML = `
      <a href="/products" class="detaliu-inapoi">&larr; Înapoi la produse</a>
      <p class="stare-incarcare">Eroare la încărcarea produsului.</p>
    `;
  }
}

incarcaDetaliu();
