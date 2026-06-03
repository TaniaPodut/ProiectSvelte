<script lang="ts">
  export let message = '';
  export let status = '';
</script>

{#if message}
  <p class={`mesaj mesaj--${status}`}>{message}</p>
{/if}
