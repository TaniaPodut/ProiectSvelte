<script lang="ts">
  import { createOrder } from '$lib/api';
  import { uiText } from '$lib/data/siteContent';
  import type { OrderPayload, Product } from '$lib/types';

  export let product: Product;

  let contactName = '';
  let contactEmail = '';
  let contactPhone = '';
  let deliveryAddress = '';
  let quantity = 1;
  let specialRequests = '';
  let orderMessage = '';
  let orderStatus = '';
  let orderLoading = false;

  async function submitOrder(event: SubmitEvent) {
    event.preventDefault();
    orderLoading = true;
    orderMessage = 'Se trimite comanda...';
    orderStatus = '';

    const payload: OrderPayload = {
      contact_name: contactName,
      contact_email: contactEmail,
      contact_phone: contactPhone,
      delivery_address: deliveryAddress,
      produs_id: product.id,
      quantity,
      special_requests: specialRequests.trim() || null
    };

    try {
      await createOrder(payload);
      orderMessage = 'Comanda a fost trimisă cu succes. Te vom contacta pentru confirmare.';
      orderStatus = 'succes';
      contactName = '';
      contactEmail = '';
      contactPhone = '';
      deliveryAddress = '';
      quantity = 1;
      specialRequests = '';
    } catch (error) {
      orderMessage = error instanceof Error ? error.message : 'Comanda nu a putut fi trimisă.';
      orderStatus = 'eroare';
    } finally {
      orderLoading = false;
    }
  }
</script>

<div class="detaliu-grid">
  <div class="detaliu-img-container">
    <img src={`/${product.image}`} alt={product.alt} />
  </div>
  <div class="detaliu-info">
    <div>
      <span class="detaliu-eticheta">{product.category}</span>
      {#if product.isFeatured}
        <span class="detaliu-featured">{uiText.common.featured}</span>
      {/if}
    </div>
    <h1 class="detaliu-titlu">{product.name}</h1>
    <p class="detaliu-descriere">{product.description}</p>
    <p class="detaliu-pret">{product.price.toFixed(2)} {uiText.common.priceCurrency}</p>
  </div>
</div>

<section class="sectiune-comanda">
  <div>
    <h2>Comandă produsul</h2>
    <p class="text-comanda">
      Completează datele de livrare, iar comanda va fi salvată în baza de date și preluată din panoul de administrare.
    </p>
  </div>

  <form class="formular-comanda" onsubmit={submitOrder}>
    <div class="form-grup">
      <label for="order-name">Nume complet</label>
      <input id="order-name" type="text" bind:value={contactName} required />
    </div>

    <div class="form-grup">
      <label for="order-email">Email</label>
      <input id="order-email" type="email" bind:value={contactEmail} required />
    </div>

    <div class="form-grup">
      <label for="order-phone">Telefon</label>
      <input id="order-phone" type="tel" bind:value={contactPhone} required minlength="6" />
    </div>

    <div class="form-grup">
      <label for="order-quantity">Cantitate</label>
      <input id="order-quantity" type="number" bind:value={quantity} min="1" max="10" required />
    </div>

    <div class="form-grup form-grup--lat">
      <label for="order-address">Adresă de livrare</label>
      <input id="order-address" type="text" bind:value={deliveryAddress} required minlength="5" />
    </div>

    <div class="form-grup form-grup--lat">
      <label for="order-requests">Observații</label>
      <textarea id="order-requests" bind:value={specialRequests} rows="4"></textarea>
    </div>

    <button class="buton buton--mare btn-trimite form-grup--lat" type="submit" disabled={orderLoading}>
      {orderLoading ? 'Se trimite...' : uiText.products.addToCart}
    </button>

    {#if orderMessage}
      <p class={`mesaj-comanda mesaj-comanda--${orderStatus}`}>{orderMessage}</p>
    {/if}
  </form>
</section>
