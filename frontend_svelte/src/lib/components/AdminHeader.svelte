<script lang="ts">
  import { uiText } from '$lib/data/siteContent';

  export let onLogout: () => void | Promise<void> = () => {};
</script>

<header class="admin-antet">
  <span class="admin-titlu">{uiText.admin.title}</span>
  <div class="admin-actiuni">
    <a href="/" class="btn-logout admin-link-site">{uiText.admin.siteLink}</a>
    <button class="btn-logout" type="button" onclick={onLogout}>{uiText.admin.logout}</button>
  </div>
</header>
