<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import {
    createProduct,
    deleteProduct as removeProduct,
    getOrders,
    getProducts,
    updateProduct,
    uploadImage
  } from '$lib/api';
  import { authState } from '$lib/auth.svelte';
  import AdminHeader from '$lib/components/AdminHeader.svelte';
  import EditProductModal from '$lib/components/EditProductModal.svelte';
  import ProductForm from '$lib/components/ProductForm.svelte';
  import ProductTable from '$lib/components/ProductTable.svelte';
  import StaffManagementPanel from '$lib/components/StaffManagementPanel.svelte';
  import { defaultProductCategories } from '$lib/data/categories';
  import { emptyProduct, uiText } from '$lib/data/siteContent';
  import type { Order, Product, ProductFormData } from '$lib/types';
  import './admin.css';

  let isReady = false;
  let products: Product[] = [];
  let orders: Order[] = [];
  let loadingProducts = false;
  let loadingOrders = false;
  let newProduct: ProductFormData = { ...emptyProduct };
  let addMessage = '';
  let addStatus = '';
  let editProduct: Product | null = null;
  let editMessage = '';
  let editStatus = '';

  $: categories = [
    ...new Set([...defaultProductCategories, ...products.map((product) => product.category).filter(Boolean)])
  ];

  onMount(async () => {
    await authState.hydrate();
    if (!authState.currentUser) {
      await goto('/login');
      return;
    }
    
    // Doar adminii pot vedea această pagină completă
    if (authState.currentUser.role !== 'admin') {
      await goto('/manager');
      return;
    }

    isReady = true;
    loadAdminData();
  });

  function errorMessage(error: unknown, fallback: string) {
    if (error instanceof Error) return error.message;
    return fallback;
  }

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
    if (!authState.sessionToken) return;
    loadingOrders = true;
    try {
      orders = await getOrders(authState.sessionToken);
    } catch (error) {
      console.error(error);
    } finally {
      loadingOrders = false;
    }
  }

  async function loadAdminData() {
    await Promise.all([loadProducts(), loadOrders()]);
  }

  async function resolveImage(currentImage: string, imageFile: File | null) {
    if (!imageFile || !authState.sessionToken) {
      return currentImage;
    }

    const { filename } = await uploadImage(imageFile, authState.sessionToken);
    return filename;
  }

  async function handleAddProduct(product: ProductFormData, imageFile: File | null) {
    if (!authState.sessionToken) return;
    addMessage = uiText.admin.addProcessing;
    addStatus = '';

    try {
      const image = await resolveImage(product.image, imageFile);
      await createProduct({ ...product, image }, authState.sessionToken);
      addMessage = uiText.admin.addSuccess;
      addStatus = 'succes';
      newProduct = { ...emptyProduct };
      await loadProducts();
    } catch (error) {
      addMessage = errorMessage(error, uiText.admin.addError);
      addStatus = 'eroare';
    }
  }

  async function handleEditProduct(product: ProductFormData, imageFile: File | null) {
    if (!editProduct || !authState.sessionToken) return;

    editMessage = uiText.admin.editProcessing;
    editStatus = '';

    try {
      const image = await resolveImage(product.image, imageFile);
      await updateProduct(editProduct.id, { ...product, image }, authState.sessionToken);
      editMessage = uiText.admin.editSuccess;
      editStatus = 'succes';
      await loadProducts();
      setTimeout(() => {
        editProduct = null;
      }, 1000);
    } catch (error) {
      editMessage = errorMessage(error, uiText.admin.editError);
      editStatus = 'eroare';
    }
  }

  async function handleDeleteProduct(product: Product) {
    if (!authState.sessionToken) return;
    if (!confirm(uiText.admin.deleteConfirm.replace('{name}', product.name))) return;

    try {
      await removeProduct(product.id, authState.sessionToken);
      await loadProducts();
    } catch (error) {
      alert(errorMessage(error, uiText.admin.deleteError));
    }
  }

  function openEdit(product: Product) {
    editProduct = { ...product };
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
      <div class="admin-top-actions" style="margin-bottom: 2rem; display: flex; gap: 1rem;">
          <a href="/manager" class="btn-primar" style="background: #2e6e5f; text-decoration: none;">Vizualizare Manager (Comenzi)</a>
      </div>

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
                  <th>Dată</th>
                  <th>Client</th>
                  <th>Contact</th>
                  <th>Produs</th>
                  <th>Cantitate</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {#each orders.slice(0, 10) as order}
                  <tr>
                    <td>{order.id}</td>
                    <td>{new Date(order.created_at).toLocaleDateString()}</td>
                    <td>{order.contact_name}</td>
                    <td>{order.contact_email}<br />{order.contact_phone}</td>
                    <td>{order.produs_id}</td>
                    <td>{order.quantity}</td>
                    <td>
                        <span class="badge" style="background: #d5e5e0; color: #203b35; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem;">
                            {order.status}
                        </span>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </section>

      <StaffManagementPanel />
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
