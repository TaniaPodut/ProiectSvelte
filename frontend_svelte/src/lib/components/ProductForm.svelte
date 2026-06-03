<script lang="ts">
  import { uiText } from '$lib/data/siteContent';
  import type { ProductFormData } from '$lib/types';
  import { emptyProduct } from '$lib/data/siteContent';
  import StatusMessage from '$lib/components/StatusMessage.svelte';

  export let product: ProductFormData = { ...emptyProduct };
  export let categories: string[] = [];
  export let title = '';
  export let submitLabel = uiText.admin.editButton;
  export let message = '';
  export let status = '';
  export let idPrefix = 'product';
  export let onSubmit: (product: ProductFormData, imageFile: File | null) => void | Promise<void> = () => {};

  let formData: ProductFormData = { ...product };
  let imageFile: File | null = null;

  $: formData = { ...product };

  async function submitProduct(event: SubmitEvent) {
    event.preventDefault();
    await onSubmit({ ...formData, price: Number(formData.price) }, imageFile);
  }

  function selectImage(event: Event) {
    const input = event.currentTarget as HTMLInputElement;
    imageFile = input.files?.[0] ?? null;
  }
</script>

<section class="sectiune-card">
  {#if title}
    <h2 class="sectiune-titlu">{title}</h2>
  {/if}

  <form onsubmit={submitProduct}>
    <div class="grila-form">
      <div class="camp">
        <label for={`${idPrefix}-name`}>{uiText.admin.productForm.name}</label>
        <input type="text" id={`${idPrefix}-name`} bind:value={formData.name} required />
      </div>
      <div class="camp">
        <label for={`${idPrefix}-category`}>{uiText.admin.productForm.category}</label>
        <select id={`${idPrefix}-category`} bind:value={formData.category} required>
          <option value="">{uiText.common.choose}</option>
          {#each categories as category}
            <option value={category}>{category}</option>
          {/each}
        </select>
      </div>
      <div class="camp">
        <label for={`${idPrefix}-price`}>{uiText.admin.productForm.price}</label>
        <input type="number" id={`${idPrefix}-price`} bind:value={formData.price} step="0.01" required />
      </div>
      <div class="camp camp--larg">
        <label for={`${idPrefix}-description`}>{uiText.admin.productForm.description}</label>
        <textarea id={`${idPrefix}-description`} bind:value={formData.description} rows="3" required></textarea>
      </div>
      <div class="camp camp--larg">
        <label for={`${idPrefix}-image`}>{uiText.admin.productForm.image}</label>
        <input type="file" id={`${idPrefix}-image`} onchange={selectImage} />
      </div>
      <div class="camp camp--larg">
        <label for={`${idPrefix}-alt`}>{uiText.admin.productForm.alt}</label>
        <input type="text" id={`${idPrefix}-alt`} bind:value={formData.alt} required />
      </div>
      <div class="camp camp--checkbox">
        <input type="checkbox" id={`${idPrefix}-featured`} bind:checked={formData.isFeatured} />
        <label for={`${idPrefix}-featured`}>{uiText.admin.productForm.featured}</label>
      </div>
    </div>

    <button type="submit" class="btn-primar">{submitLabel}</button>
    <StatusMessage {message} {status} />
  </form>
</section>
