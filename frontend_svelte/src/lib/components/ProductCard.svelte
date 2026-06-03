<script lang="ts">
  import { uiText } from '$lib/data/siteContent';
  import type { Product } from '$lib/types';

  export let product: Product;
  export let variant: 'compact' | 'catalog' = 'catalog';
</script>

{#if variant === 'compact'}
  <figure class="scaun">
    <a href={`/product/${product.id}`}><img src={`/${product.image}`} alt={product.alt} /></a>
    <div class="caseta-scaun">
      <h3>{product.name}</h3>
      <p class="scaun-descriere">{product.description}</p>
      <div class="pret-scaun">
        <strong>{product.price.toFixed(2)} {uiText.common.priceCurrency}</strong>
        <a href={`/product/${product.id}`} class="buton buton--mic">{uiText.products.viewDetails}</a>
      </div>
    </div>
  </figure>
{:else}
  <a href={`/product/${product.id}`} class="produs-link">
    <div class="card-produs">
      <img src={`/${product.image}`} alt={product.alt} loading="lazy" />
      <div class="card-produs-continut">
        <span class="card-produs-eticheta">{product.category}</span>
        <p class="card-produs-titlu">{product.name}</p>
        <p class="card-produs-descriere">{product.description}</p>
        <p class="card-produs-pret">{product.price.toFixed(2)} {uiText.common.priceCurrency}</p>
      </div>
    </div>
  </a>
{/if}
