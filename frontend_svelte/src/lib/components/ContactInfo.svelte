<script lang="ts">
  import { uiText } from '$lib/data/siteContent';
  import type { ContactDetail } from '$lib/types';

  export let title: string;
  export let intro: string;
  export let details: ContactDetail[] = [];
  export let schedule: string[] = [];
</script>

<div class="contact-info">
  <h3>{title}</h3>
  <p class="text-antet contact-intro">{intro}</p>

  <ul class="contact-detalii">
    {#each details as detail}
      <li>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="contact-pictograma"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          {#each detail.iconPath.split(' M') as path, index}
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d={index === 0 ? path : `M${path}`}
            />
          {/each}
        </svg>
        <span>{detail.label}</span>
      </li>
    {/each}
  </ul>

  <div class="program">
    <p><strong>{uiText.contact.scheduleTitle}</strong></p>
    {#each schedule as item}
      <p>{item}</p>
    {/each}
  </div>
</div>
