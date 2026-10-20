<script>
  let { icono = '🗂️', titulo, descripcion = '' } = $props();
</script>

<div class="vacio">
  <span class="vacio-icono">{icono}</span>
  <strong>{titulo}</strong>
  {#if descripcion}<p>{descripcion}</p>{/if}
</div>
