<script>
  // Tabla con la librería DataTables (búsqueda, orden y paginación).
  import DataTable from 'datatables.net-dt';
  import 'datatables.net-dt/css/dataTables.dataTables.min.css';
  import { escapar, formatearCelda } from '../lib/formato.js';

  let { columnas, filas, puedeEditar = false, puedeEliminar = false, onEditar, onEliminar } = $props();
  let contenedor;

  const ES = {
    search: 'Buscar:',
    lengthMenu: 'Mostrar _MENU_ registros',
    info: 'Mostrando _START_ a _END_ de _TOTAL_ registros',
    infoEmpty: 'Sin registros',
    infoFiltered: '(filtrado de _MAX_ en total)',
    zeroRecords: 'No se encontraron resultados',
    emptyTable: 'No hay datos disponibles',
    paginate: { first: 'Primero', last: 'Último', next: 'Siguiente', previous: 'Anterior' }
  };

  $effect(() => {
    // Copias simples: DataTables no debe recibir objetos reactivos.
    const cols = $state.snapshot(columnas);
    const datos = $state.snapshot(filas);
    const conAcciones = puedeEditar || puedeEliminar;
    const editar = puedeEditar;
    const eliminar = puedeEliminar;

    const tabla = document.createElement('table');
    tabla.className = 'display';
    contenedor.appendChild(tabla);

    const definicion = cols.map((c) => ({
      title: c.label,
      data: c.key,
      defaultContent: '',
      render: (valor, tipo) => (tipo === 'display' ? formatearCelda(c, valor) : (valor ?? ''))
    }));

    if (conAcciones) {
      definicion.push({
        title: 'Acciones',
        data: null,
        orderable: false,
        searchable: false,
        className: 'celda-acciones',
        render: (_, tipo, __, meta) => {
          if (tipo !== 'display') return '';
          const i = escapar(meta.row);
          return (
            (editar ? `<button class="boton-tabla" data-accion="editar" data-i="${i}">Editar</button>` : '') +
            (eliminar ? `<button class="boton-tabla peligro" data-accion="eliminar" data-i="${i}">Eliminar</button>` : '')
          );
        }
      });
    }

    const dt = new DataTable(tabla, {
      data: datos,
      columns: definicion,
      language: ES,
      pageLength: 10,
      lengthMenu: [5, 10, 25, 50],
      order: []
    });

    const alHacerClic = (e) => {
      const boton = e.target.closest('button[data-accion]');
      if (!boton) return;
      const fila = datos[Number(boton.dataset.i)];
      if (!fila) return;
      if (boton.dataset.accion === 'editar') onEditar?.(fila);
      else onEliminar?.(fila);
    };
    tabla.addEventListener('click', alHacerClic);

    return () => {
      tabla.removeEventListener('click', alHacerClic);
      dt.destroy();
      tabla.remove();
    };
  });
</script>

<div class="tabla-contenedor" bind:this={contenedor}></div>
