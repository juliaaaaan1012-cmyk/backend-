<script>
  import Modal from './Modal.svelte';
  import Boton from './Boton.svelte';

  let { titulo, mensaje, textoConfirmar = 'Confirmar', onConfirmar, onCancelar, cargando = false } = $props();
</script>

<Modal {titulo} onCerrar={onCancelar}>
  <p class="mensaje-confirmar">{mensaje}</p>
  <div class="acciones-formulario">
    <Boton variante="secundario" onclick={onCancelar}>Cancelar</Boton>
    <Boton variante="peligro" onclick={onConfirmar} deshabilitado={cargando}>{textoConfirmar}</Boton>
  </div>
</Modal>
