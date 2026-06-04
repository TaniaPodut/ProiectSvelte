<script lang="ts">
  import "../app.css";
  import Navbar from "$lib/components/Navbar.svelte";
  import Footer from "$lib/components/Footer.svelte";
  import { onMount } from "svelte";
  import { authState } from "$lib/auth.svelte";
  import { page } from "$app/state";

  let { children } = $props();
  const dashboardRoutes = ["/admin", "/manager", "/client"];
  let isDashboard = $derived(dashboardRoutes.some((route) => page.url.pathname.startsWith(route)));

  onMount(async () => {
    await authState.hydrate();
  });
</script>

<div class="container">
  {#if !isDashboard}
    <Navbar />
  {/if}
  <main>
    {@render children()}
  </main>
  {#if !isDashboard}
    <Footer />
  {/if}
</div>
