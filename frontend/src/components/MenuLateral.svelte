<script>
  // Menú de navegación. Sus opciones llegan de la base de datos
  // (tabla roles_modulos) a través del login.
  let { modulos, activo, usuario, abierto = false, onSeleccionar, onCerrar } = $props();
  const iniciales = $derived(usuario.nombre_completo.split(' ').slice(0, 2).map((p) => p[0]).join(''));
</script>

{#if abierto}
  <button class="velo-menu" aria-label="Cerrar menú" onclick={onCerrar}></button>
{/if}

<aside class="menu-lateral" class:abierto>
  <div class="marca">
    <span class="marca-logo">R</span>
    <div>
      <strong>RutaEscolar</strong>
      <small>{usuario.rol}</small>
    </div>
  </div>

  <nav aria-label="Menú principal">
    <button class:activo={activo === 'inicio'} onclick={() => onSeleccionar('inicio')}>
      <span class="icono">🏠</span> Inicio
    </button>
    <p>MÓDULOS</p>
    {#each modulos as modulo (modulo.clave)}
      <button class:activo={activo === modulo.clave} onclick={() => onSeleccionar(modulo.clave)}>
        <span class="icono">{modulo.icono ?? '•'}</span> {modulo.nombre}
      </button>
    {/each}
  </nav>

  <div class="menu-pie">
    <span class="avatar">{iniciales}</span>
    <div>
      <strong>{usuario.nombre_completo}</strong>
      <small>{usuario.correo}</small>
    </div>
  </div>
</aside>
