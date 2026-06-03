<script lang="ts">
  import { onMount } from 'svelte';
  import {
    createProduct,
    deleteProduct as removeProduct,
    getOrders,
    getProducts,
    loginAdmin,
    logoutAdmin,
    updateProduct,
    uploadImage
  } from '$lib/api';
  import AdminHeader from '$lib/components/AdminHeader.svelte';
  import AdminLogin from '$lib/components/AdminLogin.svelte';
  import EditProductModal from '$lib/components/EditProductModal.svelte';
  import ProductForm from '$lib/components/ProductForm.svelte';
  import ProductTable from '$lib/components/ProductTable.svelte';
  import { defaultProductCategories } from '$lib/data/categories';
  import { emptyProduct, uiText } from '$lib/data/siteContent';
  import type { AdminCredentials, Order, Product, ProductFormData } from '$lib/types';
  import './admin.css';

  const tokenKey = 'webtania_admin_token';

  let loggedIn = false;
  let loginError = '';
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

  onMount(() => {
    const token = localStorage.getItem(tokenKey);
    if (token) {
      loggedIn = true;
      loadAdminData();
    }
  });

  function getToken() {
    return localStorage.getItem(tokenKey) || '';
  }

  function errorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
  }

  async function handleLogin(credentials: AdminCredentials) {
    loginError = '';
    try {
      const { token } = await loginAdmin(credentials);
      localStorage.setItem(tokenKey, token);
      loggedIn = true;
      await loadAdminData();
    } catch (error) {
      loginError = errorMessage(error, uiText.admin.loginError);
    }
  }

  async function handleLogout() {
    const token = getToken();
    try {
      if (token) {
        await logoutAdmin(token);
      }
    } catch {
      // Logout should still clear the local session.
    }

    localStorage.removeItem(tokenKey);
    loggedIn = false;
    products = [];
    orders = [];
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
    loadingOrders = true;
    try {
      orders = await getOrders(getToken());
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
    if (!imageFile) {
      return currentImage;
    }

    const { filename } = await uploadImage(imageFile, getToken());
    return filename;
  }

  async function handleAddProduct(product: ProductFormData, imageFile: File | null) {
    addMessage = uiText.admin.addProcessing;
    addStatus = '';

    try {
      const image = await resolveImage(product.image, imageFile);
      await createProduct({ ...product, image }, getToken());
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
    if (!editProduct) return;

    editMessage = uiText.admin.editProcessing;
    editStatus = '';

    try {
      const image = await resolveImage(product.image, imageFile);
      await updateProduct(editProduct.id, { ...product, image }, getToken());
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
    if (!confirm(uiText.admin.deleteConfirm.replace('{name}', product.name))) return;

    try {
      await removeProduct(product.id, getToken());
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

{#if !loggedIn}
  <AdminLogin error={loginError} onLogin={handleLogin} />
{:else}
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
          <h2 class="sectiune-titlu admin-sectiune-titlu">Comenzi primite</h2>
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
                  <th>Produs</th>
                  <th>Cantitate</th>
                  <th>Adresă</th>
                  <th>Observații</th>
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
                    <td>{order.delivery_address}</td>
                    <td>{order.special_requests || '-'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
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
