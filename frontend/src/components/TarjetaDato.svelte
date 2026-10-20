<script>
  // Tarjeta de resumen del inicio (número + título). Es un botón de acceso.
  let { icono, titulo, valor, color = 'azul', onclick } = $props();
</script>

<button class="tarjeta-dato" {onclick}>
  <span class="tarjeta-icono {color}">{icono}</span>
  <span>
    <small>{titulo}</small>
    <strong>{valor ?? '…'}</strong>
  </span>
</button>
