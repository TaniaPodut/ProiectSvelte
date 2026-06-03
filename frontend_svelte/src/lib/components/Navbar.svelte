<script lang="ts">
  import { page } from '$app/state';
  import { navLinks, siteContent } from '$lib/data/siteContent';

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
      <a
        href={link.href}
        class="nav-link"
        class:nav-link-admin={link.admin}
        class:activ={isActive(link.href, link.match)}
      >
        {link.label}
      </a>
    {/each}
  </nav>
</header>
