<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getContactMessages, getOrders, getProducts } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import AdminHeader from '$lib/components/AdminHeader.svelte';
  import ProductTable from '$lib/components/ProductTable.svelte';
  import type { ContactPayload, Order, Product } from '$lib/types';
  import '../admin/admin.css';

  let isReady = $state(false);
  let products = $state<Product[]>([]);
  let orders = $state<Order[]>([]);
  let messages = $state<ContactPayload[]>([]);
  let loadingProducts = $state(false);
  let loadingOrders = $state(false);
  let loadingMessages = $state(false);

  onMount(async () => {
    authState.hydrate();
    if (!authState.token) {
      await goto('/login');
      return;
    }
    if (authState.role !== 'manager') {
      await goto(authState.dashboardHref);
      return;
    }
    isReady = true;
    loadManagerData();
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

  async function loadOrders() {
    if (!authState.token) return;
    loadingOrders = true;
    try {
      orders = await getOrders(authState.token);
    } finally {
      loadingOrders = false;
    }
  }

  async function loadMessages() {
    if (!authState.token) return;
    loadingMessages = true;
    try {
      messages = await getContactMessages(authState.token);
    } finally {
      loadingMessages = false;
    }
  }

  async function loadManagerData() {
    await Promise.all([loadProducts(), loadOrders(), loadMessages()]);
  }
</script>

<svelte:head>
  <title>Manager Dashboard - Webtania</title>
</svelte:head>

{#if isReady}
  <div class="panou-admin">
    <AdminHeader
      title="Dashboard Manager"
      subtitle={authState.displayName ? `Conectat ca ${authState.displayName}` : 'Comenzi si mesaje'}
      onLogout={handleLogout}
    />

    <main class="admin-main">
      <ProductTable {products} loading={loadingProducts} onReload={loadProducts} showActions={false} />

      <section class="sectiune-card">
        <div class="admin-sectiune-antet">
          <h2 class="sectiune-titlu admin-sectiune-titlu">Comenzi recente</h2>
          <button class="btn-primar btn-reincarca" type="button" onclick={loadOrders}>Reincarca</button>
        </div>
        {#if loadingOrders}
          <p>Se incarca comenzile...</p>
        {:else if orders.length === 0}
          <p>Nu exista comenzi inca.</p>
        {:else}
          <div class="tabel-container">
            <table class="tabel-produse">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Client</th>
                  <th>Contact</th>
                  <th>Produs ID</th>
                  <th>Cantitate</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {#each orders as order}
                  <tr>
                    <td>{order.id}</td>
                    <td>{order.contact_name}</td>
                    <td>{order.contact_email}<br />{order.contact_phone}</td>
                    <td>{order.produs_id}</td>
                    <td>{order.quantity}</td>
                    <td><span class="badge">{order.status}</span></td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </section>

      <section class="sectiune-card">
        <div class="admin-sectiune-antet">
          <h2 class="sectiune-titlu admin-sectiune-titlu">Mesaje contact</h2>
          <button class="btn-primar btn-reincarca" type="button" onclick={loadMessages}>Reincarca</button>
        </div>
        {#if loadingMessages}
          <p>Se incarca mesajele...</p>
        {:else if messages.length === 0}
          <p>Nu exista mesaje noi.</p>
        {:else}
          <div class="messages-list">
            {#each messages as msg}
              <article class="message-item">
                <strong>{msg.nume}</strong> ({msg.email})
                <p>{msg.mesaj}</p>
              </article>
            {/each}
          </div>
        {/if}
      </section>
    </main>
  </div>
{/if}

<style>
  .messages-list {
    display: grid;
    gap: 16px;
  }

  .message-item {
    padding: 16px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
  }

  .message-item p {
    margin: 8px 0 0;
  }
</style>
