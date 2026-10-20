<script>
  let { sobretitulo = '', titulo, subtitulo = '', children } = $props();
</script>

<div class="encabezado-pagina">
  <div>
    {#if sobretitulo}<p class="sobretitulo">{sobretitulo}</p>{/if}
    <h1>{titulo}</h1>
    {#if subtitulo}<p class="subtitulo">{subtitulo}</p>{/if}
  </div>
  <div class="encabezado-acciones">{@render children?.()}</div>
</div>
