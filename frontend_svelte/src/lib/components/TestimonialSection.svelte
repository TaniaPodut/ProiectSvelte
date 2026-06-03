<script lang="ts">
  export let image: string;
  export let imageAlt: string;
  export let title: string;
  export let quote: string;
  export let author: string;
</script>

<section class="sectiune-marturii">
  <div class="grila-3-coloane">
    <img src={image} alt={imageAlt} />
    <div class="caseta-marturii">
      <h2>{title}</h2>
      <blockquote class="text-marturii">{quote}</blockquote>
      <p class="autor-marturii">&mdash; {author}</p>
    </div>
  </div>
</section>
