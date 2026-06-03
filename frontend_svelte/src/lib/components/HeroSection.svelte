<script lang="ts">
  export let title: string;
  export let text: string;
  export let ctaLabel: string;
  export let ctaHref: string;
  export let image: string;
  export let imageAlt: string;
</script>

<header class="sectiune-hero">
  <div class="caseta-text-antet">
    <h1>{title}</h1>
    <p class="text-antet">{text}</p>
    <a class="buton buton--mare" href={ctaHref}>{ctaLabel}</a>
  </div>
  <img src={image} alt={imageAlt} />
</header>
