<script lang="ts">
  import { uiText } from '$lib/data/siteContent';

  export let onLogout: () => void | Promise<void> = () => {};
  export let title = uiText.admin.title;
  export let subtitle = '';
</script>

<header class="admin-antet">
  <div>
    <span class="admin-titlu">{title}</span>
    {#if subtitle}
      <span class="admin-subtitlu">{subtitle}</span>
    {/if}
  </div>
  <div class="admin-actiuni">
    <a href="/" class="btn-logout admin-link-site">{uiText.admin.siteLink}</a>
    <button class="btn-logout" type="button" onclick={onLogout}>{uiText.admin.logout}</button>
  </div>
</header>
