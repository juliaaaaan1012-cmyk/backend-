<script>
  // Página completa de un módulo: encabezado, tabla (DataTables) y
  // formulario en ventana. La usan TODOS los módulos de TODOS los roles.
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import { recursos, etiquetaDeFuente } from '../lib/registro.js';
  import EncabezadoPagina from './EncabezadoPagina.svelte';
  import TablaDatos from './TablaDatos.svelte';
  import Modal from './Modal.svelte';
  import ConfirmarDialogo from './ConfirmarDialogo.svelte';
  import CampoFormulario from './CampoFormulario.svelte';
  import Boton from './Boton.svelte';
  import Alerta from './Alerta.svelte';
  import EstadoVacio from './EstadoVacio.svelte';

  let { modulo, rol } = $props();

  const config = $derived(recursos[modulo.clave]);
  const camposVisibles = $derived(
    config.campos.filter((c) => !c.visibleFor || c.visibleFor.includes(rol))
  );

  let filas = $state([]);
  let opciones = $state({});
  let cargando = $state(true);
  let guardando = $state(false);
  let error = $state('');
  let aviso = $state('');
  let formulario = $state(null);   // null = cerrado
  let editando = $state(null);     // fila en edición (null = nuevo)
  let porEliminar = $state(null);

  onMount(() => {
    cargar();
    cargarOpciones();
  });

  async function cargar() {
    cargando = true;
    try {
      filas = await api.listar(modulo.clave);
      error = '';
    } catch (e) {
      filas = [];
      error = e.message;
    } finally {
      cargando = false;
    }
  }

  // Las listas desplegables se llenan con los datos de otros módulos.
  async function cargarOpciones() {
    const fuentes = [...new Set(camposVisibles.filter((c) => c.source).map((c) => c.source))];
    for (const fuente of fuentes) {
      try {
        const datos = await api.listar(fuente);
        opciones[fuente] = datos.map((d) => ({ valor: d.id, etiqueta: etiquetaDeFuente[fuente](d) }));
      } catch {
        opciones[fuente] = [];
      }
    }
  }

  function opcionesDe(campo) {
    if (campo.source) return opciones[campo.source] ?? [];
    return (campo.options ?? []).map((o) => ({ valor: o, etiqueta: o }));
  }

  function inicial(campo, fila) {
    const v = fila?.[campo.key];
    if (campo.type === 'boolean') return v ?? false;
    if (campo.type === 'time') return v ? String(v).slice(0, 5) : '';
    if (campo.type === 'password') return '';
    return v ?? '';
  }

  function abrir(fila = null) {
    editando = fila;
    formulario = Object.fromEntries(config.campos.map((c) => [c.key, inicial(c, fila)]));
    error = '';
  }

  function cerrar() {
    formulario = null;
    editando = null;
  }

  function armarDatos() {
    const datos = {};
    for (const c of config.campos) {
      let v = formulario[c.key];
      if (c.type === 'boolean') v = Boolean(v);
      else if (v === '' || v === undefined) v = null;
      else if (c.type === 'number' || c.source) v = Number(v);
      datos[c.key] = v;
    }
    return datos;
  }

  async function guardar(e) {
    e.preventDefault();
    guardando = true;
    error = '';
    try {
      const datos = armarDatos();
      if (editando) await api.actualizar(modulo.clave, editando.id, datos);
      else await api.crear(modulo.clave, datos);
      aviso = editando ? 'Cambios guardados correctamente.' : 'Registro creado correctamente.';
      cerrar();
      await cargar();
    } catch (err) {
      error = err.message;
    } finally {
      guardando = false;
    }
  }

  async function confirmarEliminar() {
    guardando = true;
    try {
      await api.eliminar(modulo.clave, porEliminar.id);
      aviso = 'Registro eliminado correctamente.';
      porEliminar = null;
      await cargar();
    } catch (err) {
      error = err.message;
      porEliminar = null;
    } finally {
      guardando = false;
    }
  }
</script>

<EncabezadoPagina
  sobretitulo={rol.toUpperCase()}
  titulo={modulo.nombre}
  subtitulo={cargando ? 'Cargando…' : `${filas.length} ${filas.length === 1 ? 'registro' : 'registros'}`}
>
  <Boton variante="secundario" onclick={cargar}>↻ Actualizar</Boton>
  {#if modulo.puede_crear}
    <Boton onclick={() => abrir()}>＋ Nuevo</Boton>
  {/if}
</EncabezadoPagina>

{#if aviso}<Alerta tipo="ok" onCerrar={() => (aviso = '')}>{aviso}</Alerta>{/if}
{#if error && !formulario}<Alerta tipo="error" onCerrar={() => (error = '')}>{error}</Alerta>{/if}

<section class="panel">
  {#if cargando}
    <EstadoVacio icono="⏳" titulo="Cargando información…" />
  {:else if !filas.length}
    <EstadoVacio titulo="Aún no hay registros" descripcion="Cuando se agreguen, aparecerán aquí." />
  {:else}
    <TablaDatos
      columnas={config.columnas}
      {filas}
      puedeEditar={modulo.puede_editar}
      puedeEliminar={modulo.puede_eliminar}
      onEditar={abrir}
      onEliminar={(fila) => (porEliminar = fila)}
    />
  {/if}
</section>

{#if formulario}
  <Modal titulo={`${editando ? 'Editar' : 'Nuevo'} · ${modulo.nombre}`} onCerrar={cerrar}>
    <form class="formulario" onsubmit={guardar}>
      {#each camposVisibles as campo (campo.key)}
        <CampoFormulario
          {campo}
          esNuevo={!editando}
          opciones={opcionesDe(campo)}
          bind:valor={formulario[campo.key]}
        />
      {/each}

      {#if error}<div class="ancho-completo"><Alerta tipo="error">{error}</Alerta></div>{/if}

      <div class="acciones-formulario">
        <Boton variante="secundario" onclick={cerrar}>Cancelar</Boton>
        <Boton tipo="submit" deshabilitado={guardando}>{guardando ? 'Guardando…' : 'Guardar'}</Boton>
      </div>
    </form>
  </Modal>
{/if}

{#if porEliminar}
  <ConfirmarDialogo
    titulo="Eliminar registro"
    mensaje="¿Seguro que deseas eliminar este registro? Dejará de mostrarse en el sistema."
    textoConfirmar="Sí, eliminar"
    cargando={guardando}
    onConfirmar={confirmarEliminar}
    onCancelar={() => (porEliminar = null)}
  />
{/if}
