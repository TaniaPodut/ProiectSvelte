<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getProducts } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import ProductGrid from '$lib/components/ProductGrid.svelte';
  import type { Product } from '$lib/types';
  import '../admin/admin.css';

  let isReady = $state(false);
  let products = $state<Product[]>([]);
  let loadingProducts = $state(false);

  onMount(async () => {
    authState.hydrate();
    if (!authState.token) {
      await goto('/login');
      return;
    }
    if (authState.role !== 'client') {
      await goto(authState.dashboardHref);
      return;
    }
    isReady = true;
    loadProducts();
  });

  async function handleLogout() {
    await authState.logout();
    await goto('/login');
  }

  async function loadProducts() {
    loadingProducts = true;
    try {
      products = await getProducts();
    } finally {
      loadingProducts = false;
    }
  }
</script>

<svelte:head>
  <title>Client Dashboard - Webtania</title>
</svelte:head>

{#if isReady}
  <div class="panou-admin">
    <header class="admin-antet">
      <div>
        <span class="admin-titlu">Dashboard Client</span>
        <span class="admin-subtitlu">
          {authState.displayName ? `Bine ai venit, ${authState.displayName}` : 'Cont client'}
        </span>
      </div>
      <div class="admin-actiuni">
        <a href="/" class="btn-logout admin-link-site">Site principal</a>
        <button class="btn-logout" type="button" onclick={handleLogout}>Deconectare</button>
      </div>
    </header>

    <main class="admin-main">
      <section class="sectiune-card client-actions">
        <a class="client-action" href="/products">Vezi catalogul</a>
        <a class="client-action" href="/contact">Trimite mesaj</a>
      </section>

      <section class="sectiune-card">
        <div class="admin-sectiune-antet">
          <h2 class="sectiune-titlu admin-sectiune-titlu">Produse recomandate</h2>
          <button class="btn-primar btn-reincarca" type="button" onclick={loadProducts}>Reincarca</button>
        </div>
        {#if loadingProducts}
          <p>Se incarca produsele...</p>
        {:else}
          <ProductGrid products={products.filter((product) => product.isFeatured).slice(0, 3)} />
        {/if}
      </section>
    </main>
  </div>
{/if}

<style>
  .client-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }

  .client-action {
    display: block;
    padding: 18px 20px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    color: #064e3b;
    font-weight: 700;
    text-decoration: none;
    background: #fff;
  }

  .client-action:hover {
    border-color: #087f5b;
    background: #f0fdf4;
  }

  @media (max-width: 640px) {
    .client-actions {
      grid-template-columns: 1fr;
    }
  }
</style>
