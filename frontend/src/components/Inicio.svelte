<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/api.js';
  import { bienvenida } from '../lib/registro.js';
  import EncabezadoPagina from './EncabezadoPagina.svelte';
  import TarjetaDato from './TarjetaDato.svelte';
  import Insignia from './Insignia.svelte';
  import Boton from './Boton.svelte';

  let { usuario, modulos, onIr } = $props();

  let conteos = $state({});
  const colores = ['azul', 'amarillo', 'verde', 'morado'];
  const destacados = $derived(modulos.slice(0, 4));

  onMount(() => {
    // Número de registros de cada módulo (datos reales de la base de datos).
    for (const m of destacados) {
      api.listar(m.clave).then((d) => (conteos[m.clave] = d.length)).catch(() => (conteos[m.clave] = '–'));
    }
  });
</script>

<EncabezadoPagina sobretitulo={usuario.rol.toUpperCase()} titulo={`Hola, ${usuario.nombre_completo.split(' ')[0]}`} />

<section class="bienvenida">
  <div>
    <Insignia texto={usuario.rol} color="azul" />
    <h2>Tu transporte, organizado.</h2>
    <p>{bienvenida[usuario.rol] ?? 'Gestiona la información del transporte escolar.'}</p>
    {#if modulos.length}
      <Boton onclick={() => onIr(modulos[0].clave)}>Comenzar →</Boton>
    {/if}
  </div>
  <div class="bienvenida-bus" aria-hidden="true">🚌</div>
</section>

<section class="tarjetas">
  {#each destacados as m, i (m.clave)}
    <TarjetaDato icono={m.icono ?? '•'} titulo={m.nombre} valor={conteos[m.clave]} color={colores[i % 4]} onclick={() => onIr(m.clave)} />
  {/each}
</section>

<section class="panel accesos">
  <h2>Accesos disponibles</h2>
  <div class="chips">
    {#each modulos as m (m.clave)}
      <button class="chip" onclick={() => onIr(m.clave)}>{m.icono} {m.nombre}</button>
    {/each}
  </div>
</section>
