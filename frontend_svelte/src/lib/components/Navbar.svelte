<script lang="ts">
  import { page } from '$app/state';
  import { navLinks, siteContent } from '$lib/data/siteContent';
  import { authState } from '$lib/auth.svelte';

  function isActive(href: string, match: string) {
    if (match === 'exact') {
      return page.url.pathname === href;
    }
    return page.url.pathname.startsWith(href);
  }
</script>

<header class="antet-pagina">
  <a href="/" class="link-logo">{siteContent.brandName}</a>
  <nav>
    {#each navLinks as link}
      {#if !link.admin}
        <a
          href={link.href}
          class="nav-link"
          class:activ={isActive(link.href, link.match)}
        >
          {link.label}
        </a>
      {/if}
    {/each}

    {#if authState.currentUser}
      <a
        href="/manager"
        class="nav-link nav-link-staff"
        class:activ={isActive('/manager', 'prefix')}
      >
        Panou Manager
      </a>
      
      {#if authState.currentUser.role === 'admin'}
        <a
          href="/admin"
          class="nav-link nav-link-admin"
          class:activ={isActive('/admin', 'prefix')}
        >
          Panou Admin
        </a>
      {/if}

      <button type="button" class="nav-btn-logout" onclick={() => authState.logout()}>
        Deconectare
      </button>
    {:else}
      <a href="/login" class="nav-link" class:activ={isActive('/login', 'exact')}>
        Autentificare
      </a>
    {/if}
  </nav>
</header>

<style>
  .nav-link-staff {
    color: #2e6e5f;
    font-weight: bold;
  }
  .nav-link-admin {
    color: #8a4b08;
    font-weight: bold;
  }
  .nav-btn-logout {
    background: transparent;
    border: 1px solid #ccc;
    padding: 4px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    margin-left: 10px;
  }
  .nav-btn-logout:hover {
    background: #f0f0f0;
  }
</style>
