<script lang="ts">
  import { onMount } from 'svelte';
  import { getProducts } from '$lib/api';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import FilterTabs from '$lib/components/FilterTabs.svelte';
  import LoadingState from '$lib/components/LoadingState.svelte';
  import ProductGrid from '$lib/components/ProductGrid.svelte';
  import { allProductsFilter, buildCategoryFilters } from '$lib/data/categories';
  import { siteContent, uiText } from '$lib/data/siteContent';
  import type { Product } from '$lib/types';

  let products: Product[] = [];
  let filteredProducts: Product[] = [];
  let filters = [allProductsFilter];
  let activeFilter = allProductsFilter.id;
  let loading = true;

  onMount(async () => {
    try {
      products = await getProducts();
      filters = buildCategoryFilters(products.map((product) => product.category));
      applyFilter(allProductsFilter.id);
    } catch (error) {
      console.error('Error loading products:', error);
    } finally {
      loading = false;
    }
  });

  function applyFilter(filterId: string) {
    activeFilter = filterId;
    filteredProducts =
      filterId === allProductsFilter.id
        ? products
        : products.filter((product) => product.category === filterId);
  }
</script>

<section>
  <h2>{siteContent.productsTitle}</h2>
  <FilterTabs {filters} {activeFilter} onFilterChange={applyFilter} />

  {#if loading}
    <LoadingState message={uiText.products.loading} />
  {:else if filteredProducts.length === 0}
    <EmptyState message={uiText.products.emptyForCategory} />
  {:else}
    <ProductGrid products={filteredProducts} />
  {/if}
</section>
