<script lang="ts">
  import { onMount } from 'svelte';
  import { getProducts } from '$lib/api';
  import FeatureGrid from '$lib/components/FeatureGrid.svelte';
  import HeroSection from '$lib/components/HeroSection.svelte';
  import ProductGrid from '$lib/components/ProductGrid.svelte';
  import TestimonialSection from '$lib/components/TestimonialSection.svelte';
  import { features, siteContent } from '$lib/data/siteContent';
  import type { Product } from '$lib/types';

  let featuredProducts: Product[] = [];

  onMount(async () => {
    try {
      const products = await getProducts();
      featuredProducts = products.filter((product) => product.isFeatured).slice(0, 3);
    } catch (error) {
      console.error('Error loading products:', error);
    }
  });
</script>

<HeroSection {...siteContent.hero} />
<FeatureGrid title={siteContent.featuresTitle} {features} />
<TestimonialSection {...siteContent.testimonial} />

<section>
  <h2>{siteContent.featuredProductsTitle}</h2>
  <ProductGrid products={featuredProducts} variant="compact" />
  <div class="actiune-centrata">
    <a href="/products" class="buton buton--mare">{siteContent.allProductsCta}</a>
  </div>
</section>
