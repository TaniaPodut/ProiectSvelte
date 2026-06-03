const URL_API = "/api";
const grila = document.querySelector("#grila-produse");
const butoaneFiltru = document.querySelectorAll(".btn-filtru");

document.querySelector("#an-curent").textContent = new Date().getFullYear();

function genereazaCard(produs) {
  return `
    <a href="/product?id=${produs.id}" class="produs-link">
      <div class="card-produs">
        <img src="${produs.image}" alt="${produs.alt}" loading="lazy" />
        <div class="card-produs-continut">
          <span class="card-produs-eticheta">${produs.category}</span>
          <p class="card-produs-titlu">${produs.name}</p>
          <p class="card-produs-descriere">${produs.description}</p>
          <p class="card-produs-pret">${produs.price.toFixed(2)} lei</p>
        </div>
      </div>
    </a>
  `;
}

let toateProdusele = [];

async function incarcaProduse() {
  try {
    const raspuns = await fetch(`${URL_API}/products`);
    toateProdusele = await raspuns.json();
    afiseazaProduse("toate");
  } catch {
    grila.innerHTML = `<p class="stare-incarcare">Eroare la încărcarea produselor.</p>`;
  }
}

function afiseazaProduse(filtru) {
  const lista = filtru === "toate"
    ? toateProdusele
    : toateProdusele.filter(p => p.category === filtru);

  if (lista.length === 0) {
    grila.innerHTML = `<p class="stare-incarcare">Niciun produs în categoria selectată.</p>`;
    return;
  }

  grila.innerHTML = lista.map(genereazaCard).join("");
}

butoaneFiltru.forEach(btn => {
  btn.addEventListener("click", () => {
    butoaneFiltru.forEach(b => b.classList.remove("activ"));
    btn.classList.add("activ");
    afiseazaProduse(btn.dataset.filtru);
  });
});

incarcaProduse();
