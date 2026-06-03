<script lang="ts">
  import type { FeatureItem } from '$lib/types';
  import FeatureCard from '$lib/components/FeatureCard.svelte';

  export let title: string;
  export let features: FeatureItem[] = [];
</script>

<section>
  <h2>{title}</h2>
  <div class="grila-3-coloane">
    {#each features as feature}
      <FeatureCard {feature} />
    {/each}
  </div>
</section>
