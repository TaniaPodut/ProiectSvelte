<script lang="ts">
  import { sendContactMessage } from '$lib/api';
  import ContactForm from '$lib/components/ContactForm.svelte';
  import ContactInfo from '$lib/components/ContactInfo.svelte';
  import { contactDetails, siteContent, uiText } from '$lib/data/siteContent';
  import type { ContactPayload } from '$lib/types';

  let trimis = false;
  let loading = false;

  async function handleSubmit(payload: ContactPayload) {
    loading = true;
    try {
      await sendContactMessage(payload);
      trimis = true;
    } catch (error) {
      alert(uiText.contact.submitError);
    } finally {
      loading = false;
    }
  }
</script>

<section>
  <h2>{siteContent.contactTitle}</h2>
  <div class="contact-container">
    <ContactInfo
      title={siteContent.contactInfoTitle}
      intro={siteContent.contactIntro}
      details={contactDetails}
      schedule={siteContent.showroomSchedule}
    />
    <ContactForm sent={trimis} {loading} onSubmit={handleSubmit} onReset={() => (trimis = false)} />
  </div>
</section>
