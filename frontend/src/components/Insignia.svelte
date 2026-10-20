<script>
  // Etiqueta de color para estados.
  let { texto, color = 'gris' } = $props();
</script>

<span class="insignia {color}">{texto}</span>
