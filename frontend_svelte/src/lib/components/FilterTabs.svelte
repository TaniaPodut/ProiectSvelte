<script lang="ts">
  export let filters: { id: string; label: string }[] = [];
  export let activeFilter = 'toate';
  export let onFilterChange: (filterId: string) => void = () => {};
</script>

<div class="filtre">
  {#each filters as filter}
    <button
      type="button"
      class="btn-filtru"
      class:activ={activeFilter === filter.id}
      onclick={() => onFilterChange(filter.id)}
    >
      {filter.label}
    </button>
  {/each}
</div>
