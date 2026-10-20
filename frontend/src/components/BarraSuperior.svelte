<script>
  import Boton from './Boton.svelte';
  let { usuario, onMenu, onSalir } = $props();
  const hoy = new Date().toLocaleDateString('es-CO', { weekday: 'long', day: 'numeric', month: 'long' });
</script>

<header class="barra-superior">
  <button class="boton-menu" onclick={onMenu} aria-label="Abrir menú">☰</button>
  <span class="fecha">{hoy}</span>
  <div class="barra-usuario">
    <span class="rol-etiqueta">{usuario.rol}</span>
    <Boton variante="secundario" onclick={onSalir}>Cerrar sesión</Boton>
  </div>
</header>
