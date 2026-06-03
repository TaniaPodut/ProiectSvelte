<script lang="ts">
  import "../app.css";
  import Navbar from "$lib/components/Navbar.svelte";
  import Footer from "$lib/components/Footer.svelte";
  import { onMount } from "svelte";
  import { authState } from "$lib/auth.svelte";

  let { children } = $props();

  onMount(async () => {
    await authState.hydrate();
  });
</script>

<div class="container">
  <Navbar />
  <main>
    {@render children()}
  </main>
  <Footer />
</div>
