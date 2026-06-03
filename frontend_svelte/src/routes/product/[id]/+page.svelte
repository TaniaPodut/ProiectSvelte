<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { getProduct } from '$lib/api';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import LoadingState from '$lib/components/LoadingState.svelte';
  import ProductDetail from '$lib/components/ProductDetail.svelte';
  import { uiText } from '$lib/data/siteContent';
  import type { Product } from '$lib/types';

  let product: Product | null = null;
  let loading = true;
  let error: string | null = null;

  onMount(async () => {
    try {
      product = await getProduct(page.params.id || '');
    } catch (e) {
      error = e instanceof Error ? e.message : uiText.products.detailLoadError;
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>{uiText.products.detailPageTitle} — {product ? product.name : uiText.products.detailTitleFallback}</title>
</svelte:head>

<a href="/products" class="detaliu-inapoi">&larr; {uiText.products.backToProducts}</a>

{#if loading}
  <LoadingState message={uiText.products.loading} />
{:else if error}
  <EmptyState message={error} />
{:else if product}
  <ProductDetail {product} />
{/if}
