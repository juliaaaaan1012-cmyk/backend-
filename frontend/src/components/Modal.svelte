<script>
  // Ventana emergente. Se cierra con Esc o tocando el fondo.
  let { titulo, onCerrar, children } = $props();

  function alTeclear(e) {
    if (e.key === 'Escape') onCerrar?.();
  }
</script>

<svelte:window onkeydown={alTeclear} />

<div class="fondo-modal" role="presentation" onclick={(e) => e.target === e.currentTarget && onCerrar?.()}>
  <div class="modal" role="dialog" aria-modal="true" aria-label={titulo}>
    <div class="modal-cabecera">
      <h2>{titulo}</h2>
      <button class="cerrar" onclick={onCerrar} aria-label="Cerrar">×</button>
    </div>
    {@render children?.()}
  </div>
</div>
