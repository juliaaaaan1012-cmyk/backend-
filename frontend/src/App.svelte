<script>
  import { onMount } from 'svelte';
  import { api, alSesionVencida, sesionGuardada } from './lib/api.js';
  import { recursos } from './lib/registro.js';
  import FormularioLogin from './components/FormularioLogin.svelte';
  import MenuLateral from './components/MenuLateral.svelte';
  import BarraSuperior from './components/BarraSuperior.svelte';
  import Inicio from './components/Inicio.svelte';
  import PaginaCrud from './components/PaginaCrud.svelte';

  let sesion = $state(sesionGuardada.leer());
  let activo = $state('inicio');
  let menuAbierto = $state(false);
  let mensajeLogin = $state('');

  // El menú sale de la base de datos (roles_modulos); aquí solo se
  // ignoran módulos que el frontend aún no sabe dibujar.
  const modulos = $derived((sesion?.modulos ?? []).filter((m) => recursos[m.clave]));
  const moduloActivo = $derived(modulos.find((m) => m.clave === activo));

  function cerrarSesion(mensaje = '') {
    sesionGuardada.borrar();
    sesion = null;
    activo = 'inicio';
    menuAbierto = false;
    mensajeLogin = mensaje;
    history.replaceState(null, '', location.pathname);
  }

  alSesionVencida(() => {
    if (sesion) cerrarSesion('Tu sesión venció. Ingresa de nuevo.');
  });

  function alIngresar(datos) {
    sesionGuardada.guardar(datos);
    sesion = datos;
    mensajeLogin = '';
    ir('inicio');
  }

  function ir(clave) {
    activo = clave;
    menuAbierto = false;
    history.replaceState(null, '', clave === 'inicio' ? location.pathname : `#/${clave}`);
    window.scrollTo({ top: 0 });
  }

  onMount(async () => {
    if (!sesion) return;
    try {
      // Recarga los módulos desde la base de datos por si cambiaron los permisos.
      const actualizada = await api.yo();
      sesion = actualizada;
      sesionGuardada.guardar(actualizada);
      const deseado = location.hash.replace('#/', '');
      if (deseado && modulos.some((m) => m.clave === deseado)) activo = deseado;
    } catch {
      /* si el token venció, alSesionVencida cierra la sesión */
    }
  });
</script>

{#if !sesion}
  <FormularioLogin mensajeInicial={mensajeLogin} onIngreso={alIngresar} />
{:else}
  <div class="estructura">
    <MenuLateral
      {modulos}
      {activo}
      usuario={sesion.usuario}
      abierto={menuAbierto}
      onSeleccionar={ir}
      onCerrar={() => (menuAbierto = false)}
    />

    <div class="contenido">
      <BarraSuperior usuario={sesion.usuario} onMenu={() => (menuAbierto = true)} onSalir={() => cerrarSesion()} />
      <main>
        {#if activo === 'inicio' || !moduloActivo}
          <Inicio usuario={sesion.usuario} {modulos} onIr={ir} />
        {:else}
          {#key moduloActivo.clave}
            <PaginaCrud modulo={moduloActivo} rol={sesion.usuario.rol} />
          {/key}
        {/if}
      </main>
    </div>
  </div>
{/if}
