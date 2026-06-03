<script lang="ts">
  import type { Product } from '$lib/types';
  import ProductCard from '$lib/components/ProductCard.svelte';

  export let products: Product[] = [];
  export let variant: 'compact' | 'catalog' = 'catalog';
</script>

<div class={variant === 'compact' ? 'grila-3-coloane produse-featured' : 'grila-produse'}>
  {#each products as product}
    <ProductCard {product} {variant} />
  {/each}
</div>
