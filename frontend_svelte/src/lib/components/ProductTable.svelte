<script lang="ts">
  import { uiText } from '$lib/data/siteContent';
  import type { Product } from '$lib/types';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import LoadingState from '$lib/components/LoadingState.svelte';

  export let products: Product[] = [];
  export let loading = false;
  export let onReload: () => void | Promise<void> = () => {};
  export let onEdit: (product: Product) => void = () => {};
  export let onDelete: (product: Product) => void | Promise<void> = () => {};
  export let showActions = true;
</script>

<section class="sectiune-card">
  <div class="admin-sectiune-antet">
    <h2 class="sectiune-titlu admin-sectiune-titlu">{uiText.admin.productsTitle}</h2>
    <button class="btn-primar btn-reincarca" type="button" onclick={onReload}>{uiText.admin.reload}</button>
  </div>

  {#if loading}
    <LoadingState message={uiText.products.loading} />
  {:else if products.length === 0}
    <EmptyState message={uiText.admin.productsEmpty} />
  {:else}
    <div class="tabel-container">
      <table class="tabel-produse">
        <thead>
          <tr>
            <th>{uiText.admin.tableHeaders.id}</th>
            <th>{uiText.admin.tableHeaders.image}</th>
            <th>{uiText.admin.tableHeaders.name}</th>
            <th>{uiText.admin.tableHeaders.category}</th>
            <th>{uiText.admin.tableHeaders.price}</th>
            <th>{uiText.admin.tableHeaders.featured}</th>
            {#if showActions}
              <th>{uiText.admin.tableHeaders.actions}</th>
            {/if}
          </tr>
        </thead>
        <tbody>
          {#each products as product}
            <tr>
              <td>{product.id}</td>
              <td><img src={`/${product.image}`} alt={product.alt} class="tabel-img" /></td>
              <td>{product.name}</td>
              <td>{product.category}</td>
              <td>{product.price.toFixed(2)} {uiText.common.priceCurrency}</td>
              <td>
                <span class={`badge ${product.isFeatured ? 'badge--da' : 'badge--nu'}`}>
                  {product.isFeatured ? uiText.common.yes : uiText.common.no}
                </span>
              </td>
              {#if showActions}
                <td>
                  <button class="btn-edit" type="button" onclick={() => onEdit(product)}>
                    {uiText.admin.rowActions.edit}
                  </button>
                  <button class="btn-sterge" type="button" onclick={() => onDelete(product)}>
                    {uiText.admin.rowActions.delete}
                  </button>
                </td>
              {/if}
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</section>
