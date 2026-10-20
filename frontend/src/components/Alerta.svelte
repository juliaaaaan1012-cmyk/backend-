<script>
  // Mensaje de éxito, error o información. Se puede cerrar.
  let { tipo = 'info', onCerrar, children } = $props();
  const iconos = { ok: '✓', error: '⚠', info: 'ℹ' };
</script>

<div class="alerta {tipo}" role={tipo === 'error' ? 'alert' : 'status'}>
  <span class="alerta-icono">{iconos[tipo]}</span>
  <div class="alerta-texto">{@render children?.()}</div>
  {#if onCerrar}
    <button class="alerta-cerrar" onclick={onCerrar} aria-label="Cerrar mensaje">×</button>
  {/if}
</div>
