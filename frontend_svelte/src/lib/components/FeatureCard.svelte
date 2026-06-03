<script lang="ts">
  import type { FeatureItem } from '$lib/types';

  export let feature: FeatureItem;
</script>

<div>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    class="pictograma-caracteristici"
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
  >
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={feature.iconPath} />
  </svg>
  <p class="titlu-caracteristici"><strong>{feature.title}</strong></p>
  <p class="text-caracteristici">{feature.text}</p>
</div>
