<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import Boton from './Boton.svelte';
  import Alerta from './Alerta.svelte';

  let { mensajeInicial = '', onIngreso } = $props();

  let roles = $state([]);
  let rolId = $state('');
  let correo = $state('');
  let password = $state('');
  let error = $state('');
  let cargando = $state(false);
  let cargandoRoles = $state(true);

  onMount(async () => {
    error = mensajeInicial;
    try {
      roles = await api.roles();
    } catch (e) {
      error = e.message;
    } finally {
      cargandoRoles = false;
    }
  });

  async function ingresar(e) {
    e.preventDefault();
    error = '';
    cargando = true;
    try {
      onIngreso(await api.login({ correo, password, rol_id: Number(rolId) }));
    } catch (err) {
      error = err.message;
    } finally {
      cargando = false;
    }
  }
</script>

<main class="login">
  <section class="login-marca">
    <span class="marca-logo grande">R</span>
    <p class="sobretitulo claro">RUTAESCOLAR</p>
    <h1>La operación escolar, en movimiento.</h1>
    <p>Un acceso pensado para cada persona que hace posible el recorrido.</p>
    <div class="login-bus" aria-hidden="true">🚌</div>
  </section>

  <section class="login-tarjeta">
    <p class="sobretitulo">BIENVENIDO</p>
    <h2>Inicia sesión</h2>
    <p class="texto-suave">Selecciona tu rol e ingresa tus credenciales.</p>

    <form onsubmit={ingresar}>
      <div class="campo">
        <label for="rol">Rol</label>
        <select id="rol" bind:value={rolId} required disabled={cargandoRoles}>
          <option value="">{cargandoRoles ? 'Cargando roles…' : 'Selecciona tu rol'}</option>
          {#each roles as rol}
            <option value={rol.id}>{rol.nombre}</option>
          {/each}
        </select>
      </div>
      <div class="campo">
        <label for="correo">Correo</label>
        <input id="correo" type="email" bind:value={correo} autocomplete="username" required />
      </div>
      <div class="campo">
        <label for="password">Contraseña</label>
        <input id="password" type="password" bind:value={password} autocomplete="current-password" required />
      </div>

      {#if error}<Alerta tipo="error">{error}</Alerta>{/if}

      <Boton tipo="submit" ancho deshabilitado={cargando}>{cargando ? 'Ingresando…' : 'Ingresar'}</Boton>
    </form>
  </section>
</main>
