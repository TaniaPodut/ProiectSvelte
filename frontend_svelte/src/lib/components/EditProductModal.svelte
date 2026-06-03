<script lang="ts">
  import { uiText } from '$lib/data/siteContent';
  import type { Product, ProductFormData } from '$lib/types';
  import ProductForm from '$lib/components/ProductForm.svelte';

  export let product: Product;
  export let categories: string[] = [];
  export let message = '';
  export let status = '';
  export let onCancel: () => void = () => {};
  export let onSubmit: (product: ProductFormData, imageFile: File | null) => void | Promise<void> = () => {};
</script>

<div class="modal-overlay">
  <div class="modal-card">
    <ProductForm
      product={product}
      {categories}
      title={`${uiText.admin.editTitle} ${product.name}`}
      submitLabel={uiText.admin.editButton}
      {message}
      {status}
      idPrefix="edit-product"
      {onSubmit}
    />
    <div class="modal-actiuni">
      <button type="button" class="btn-logout btn-anuleaza" onclick={onCancel}>{uiText.admin.cancel}</button>
    </div>
  </div>
</div>
