<script lang="ts">
  import { uiText } from '$lib/data/siteContent';
  import type { AdminCredentials } from '$lib/types';

  export let error = '';
  export let onLogin: (credentials: AdminCredentials) => void | Promise<void> = () => {};

  let username = '';
  let password = '';

  function submitLogin(event: SubmitEvent) {
    event.preventDefault();
    onLogin({ username, password });
  }
</script>

<div class="ecran-login">
  <div class="login-card">
    <h1 class="login-titlu">{uiText.admin.title}</h1>
    <p class="login-subtitlu">{uiText.admin.subtitle}</p>
    <form onsubmit={submitLogin}>
      <div class="camp">
        <label for="username">{uiText.admin.loginFields.username}</label>
        <input type="text" id="username" bind:value={username} required />
      </div>
      <div class="camp login-password">
        <label for="password">{uiText.admin.loginFields.password}</label>
        <input type="password" id="password" bind:value={password} required />
      </div>
      <button type="submit" class="btn-primar login-submit">{uiText.admin.loginButton}</button>
      {#if error}
        <p class="eroare-login">{error}</p>
      {/if}
    </form>
  </div>
</div>
