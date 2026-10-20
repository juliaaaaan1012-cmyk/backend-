<script>
  // Un campo de formulario: texto, número, fecha, hora, lista, casilla...
  // Las listas muestran NOMBRES (nunca IDs).
  let { campo, valor = $bindable(), opciones = [], esNuevo = true } = $props();

  const obligatorio = $derived(campo.required === true || (campo.required === 'crear' && esNuevo));
  const id = $derived(`campo-${campo.key}`);
</script>

{#if campo.type === 'boolean'}
  <label class="campo casilla" for={id}>
    <input {id} type="checkbox" bind:checked={valor} />
    <span>{campo.label}</span>
  </label>
{:else}
  <div class="campo" class:ancho-completo={campo.type === 'textarea'}>
    <label for={id}>{campo.label}{#if obligatorio}<b>*</b>{/if}</label>

    {#if campo.type === 'select'}
      <select {id} bind:value={valor} required={obligatorio}>
        <option value="">Selecciona una opción</option>
        {#each opciones as opcion}
          <option value={opcion.valor}>{opcion.etiqueta}</option>
        {/each}
      </select>
    {:else if campo.type === 'textarea'}
      <textarea {id} rows="3" bind:value={valor} required={obligatorio}></textarea>
    {:else if campo.type === 'number'}
      <input {id} type="number" step={campo.paso ?? '1'} bind:value={valor} required={obligatorio} />
    {:else}
      <input {id} type={campo.type} bind:value={valor} required={obligatorio} autocomplete="off" />
    {/if}

    {#if campo.ayuda}<small>{campo.ayuda}</small>{/if}
  </div>
{/if}
