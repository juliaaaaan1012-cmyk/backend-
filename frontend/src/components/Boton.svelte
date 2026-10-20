<script>
  // Botón reutilizable: variante = primario | secundario | peligro | suave
  let { variante = 'primario', tipo = 'button', deshabilitado = false, ancho = false, onclick, children } = $props();
</script>

<button class="boton {variante}" class:ancho {onclick} type={tipo} disabled={deshabilitado}>
  {@render children?.()}
</button>
