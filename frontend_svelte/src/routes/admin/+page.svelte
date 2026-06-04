<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import {
    createProduct,
    deleteProduct as removeProduct,
    getOrders,
    getProducts,
    updateProduct,
    uploadImage,
    getContactMessages
  } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import AdminHeader from '$lib/components/AdminHeader.svelte';
  import EditProductModal from '$lib/components/EditProductModal.svelte';
  import ProductForm from '$lib/components/ProductForm.svelte';
  import ProductTable from '$lib/components/ProductTable.svelte';
  import { defaultProductCategories } from '$lib/data/categories';
  import { emptyProduct, uiText } from '$lib/data/siteContent';
  import type { Order, Product, ProductFormData, ContactPayload } from '$lib/types';
  import './admin.css';

  let isReady = $state(false);
  let products = $state<Product[]>([]);
  let orders = $state<Order[]>([]);
  let messages = $state<ContactPayload[]>([]);
  let loadingProducts = $state(false);
  let loadingOrders = $state(false);
  let loadingMessages = $state(false);
  let newProduct: ProductFormData = { ...emptyProduct };
  let addMessage = $state('');
  let addStatus = $state('');
  let editProduct = $state<Product | null>(null);
  let editMessage = $state('');
  let editStatus = $state('');

  $: categories = [
    ...new Set([...defaultProductCategories, ...products.map((product) => product.category).filter(Boolean)])
  ];

  onMount(async () => {
    authState.hydrate();
    if (!authState.token) {
      await goto('/login');
      return;
    }
    isReady = true;
    loadAdminData();
  });

  async function handleLogout() {
    await authState.logout();
    await goto('/login');
  }

  async function loadProducts() {
    loadingProducts = true;
    try {
      products = await getProducts();
    } catch (error) {
      console.error(error);
    } finally {
      loadingProducts = false;
    }
  }

  async function loadOrders() {
    if (!authState.token) return;
    loadingOrders = true;
    try {
      orders = await getOrders(authState.token);
    } catch (error) {
      console.error(error);
    } finally {
      loadingOrders = false;
    }
  }

  async function loadMessages() {
      if (!authState.token) return;
      loadingMessages = true;
      try {
          messages = await getContactMessages(authState.token);
      } catch (error) {
          console.error(error);
      } finally {
          loadingMessages = false;
      }
  }

  async function loadAdminData() {
    await Promise.all([loadProducts(), loadOrders(), loadMessages()]);
  }

  async function resolveImage(currentImage: string, imageFile: File | null) {
    if (!imageFile || !authState.token) {
      return currentImage;
    }
    const { filename } = await uploadImage(imageFile, authState.token);
    return filename;
  }

  async function handleAddProduct(product: ProductFormData, imageFile: File | null) {
    if (!authState.token) return;
    addMessage = uiText.admin.addProcessing;
    addStatus = '';
    try {
      const image = await resolveImage(product.image, imageFile);
      await createProduct({ ...product, image }, authState.token);
      addMessage = uiText.admin.addSuccess;
      addStatus = 'succes';
      newProduct = { ...emptyProduct };
      await loadProducts();
    } catch (error: any) {
      addMessage = error.message || uiText.admin.addError;
      addStatus = 'eroare';
    }
  }

  async function handleEditProduct(product: ProductFormData, imageFile: File | null) {
    if (!editProduct || !authState.token) return;
    editMessage = uiText.admin.editProcessing;
    editStatus = '';
    try {
      const image = await resolveImage(product.image, imageFile);
      await updateProduct(editProduct.id, { ...product, image }, authState.token);
      editMessage = uiText.admin.editSuccess;
      editStatus = 'succes';
      await loadProducts();
      setTimeout(() => {
        editProduct = null;
      }, 1000);
    } catch (error: any) {
      editMessage = error.message || uiText.admin.editError;
      editStatus = 'eroare';
    }
  }

  async function handleDeleteProduct(product: Product) {
    if (!authState.token) return;
    if (!confirm(uiText.admin.deleteConfirm.replace('{name}', product.name))) return;
    try {
      await removeProduct(product.id, authState.token);
      await loadProducts();
    } catch (error: any) {
      alert(error.message || uiText.admin.deleteError);
    }
  }

  function openEdit(p: Product) {
    editProduct = { ...p };
    editMessage = '';
    editStatus = '';
  }
</script>

<svelte:head>
  <title>Admin Dashboard - Webtania</title>
</svelte:head>

{#if isReady}
  <div class="panou-admin">
    <AdminHeader onLogout={handleLogout} />

    <main class="admin-main">
      <ProductForm
        product={newProduct}
        {categories}
        title={uiText.admin.addTitle}
        submitLabel={uiText.admin.addButton}
        message={addMessage}
        status={addStatus}
        idPrefix="new-product"
        onSubmit={handleAddProduct}
      />

      <ProductTable
        {products}
        loading={loadingProducts}
        onReload={loadProducts}
        onEdit={openEdit}
        onDelete={handleDeleteProduct}
      />

      <section class="sectiune-card">
        <div class="admin-sectiune-antet">
          <h2 class="sectiune-titlu admin-sectiune-titlu">Comenzi recente</h2>
          <button class="btn-primar btn-reincarca" type="button" onclick={loadOrders}>Reîncarcă</button>
        </div>
        {#if loadingOrders}
          <p>Se încarcă comenzile...</p>
        {:else if orders.length === 0}
          <p>Nu există comenzi încă.</p>
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
            <button class="btn-primar btn-reincarca" type="button" onclick={loadMessages}>Reîncarcă</button>
          </div>
          {#if loadingMessages}
            <p>Se încarcă mesajele...</p>
          {:else if messages.length === 0}
            <p>Nu există mesaje noi.</p>
          {:else}
            <div class="messages-list" style="display: grid; gap: 1rem;">
              {#each messages as msg}
                <div style="padding: 1rem; border: 1px solid #eee; border-radius: 8px;">
                  <strong>{msg.nume}</strong> ({msg.email})
                  <p style="margin: 0.5rem 0 0;">{msg.mesaj}</p>
                </div>
              {/each}
            </div>
          {/if}
      </section>
    </main>
  </div>
{/if}

{#if editProduct}
  <EditProductModal
    product={editProduct}
    {categories}
    message={editMessage}
    status={editStatus}
    onCancel={() => (editProduct = null)}
    onSubmit={handleEditProduct}
  />
{/if}

<style>
    .badge {
        background: #d5e5e0;
        color: #203b35;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
    }
</style>
