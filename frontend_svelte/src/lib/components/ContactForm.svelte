<script lang="ts">
  import { uiText } from '$lib/data/siteContent';
  import type { ContactPayload } from '$lib/types';

  export let sent = false;
  export let loading = false;
  export let onSubmit: (payload: ContactPayload) => void | Promise<void> = () => {};
  export let onReset: () => void = () => {};

  let nume = '';
  let telefon = '';
  let email = '';
  let mesaj = '';

  function submitForm(event: SubmitEvent) {
    event.preventDefault();
    onSubmit({ nume, telefon, email, mesaj });
  }
</script>

<div class="formular-contact">
  {#if sent}
    <div class="succes-container">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="succes-pictograma"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="succes-mesaj">{uiText.contact.successMessage}</p>
      <button class="buton buton--mic" type="button" onclick={onReset}>{uiText.contact.resetButton}</button>
    </div>
  {:else}
    <form onsubmit={submitForm}>
      <div class="form-grup">
        <label for={uiText.contact.fields.name.id}>{uiText.contact.fields.name.label}</label>
        <input
          type="text"
          id={uiText.contact.fields.name.id}
          bind:value={nume}
          placeholder={uiText.contact.fields.name.placeholder}
          required
        />
      </div>
      <div class="form-grup">
        <label for={uiText.contact.fields.phone.id}>{uiText.contact.fields.phone.label}</label>
        <input
          type="tel"
          id={uiText.contact.fields.phone.id}
          bind:value={telefon}
          placeholder={uiText.contact.fields.phone.placeholder}
          required
        />
      </div>
      <div class="form-grup">
        <label for={uiText.contact.fields.email.id}>{uiText.contact.fields.email.label}</label>
        <input
          type="email"
          id={uiText.contact.fields.email.id}
          bind:value={email}
          placeholder={uiText.contact.fields.email.placeholder}
          required
        />
      </div>
      <div class="form-grup">
        <label for={uiText.contact.fields.message.id}>{uiText.contact.fields.message.label}</label>
        <textarea
          id={uiText.contact.fields.message.id}
          bind:value={mesaj}
          rows="5"
          placeholder={uiText.contact.fields.message.placeholder}
          required
        ></textarea>
      </div>
      <button type="submit" class="buton buton--mare btn-trimite" disabled={loading}>
        {loading ? uiText.contact.submitLoading : uiText.contact.submitButton}
      </button>
    </form>
  {/if}
</div>
