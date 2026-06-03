<script lang="ts">
  import { siteContent } from '$lib/data/siteContent';
</script>

<footer>
  {siteContent.footerPrefix} &copy; {new Date().getFullYear()} {siteContent.footerText}
</footer>
