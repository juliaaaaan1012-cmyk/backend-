// Funciones de formato compartidas por las tablas y formularios.
export const escapar = (valor) =>
  String(valor ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export const hora = (v) => (v ? String(v).slice(0, 5) : '');

export const fecha = (v) => {
  if (!v) return '';
  const [a, m, d] = String(v).slice(0, 10).split('-');
  return `${d}/${m}/${a}`;
};

export const fechaHora = (v) => {
  if (!v) return '';
  const h = String(v).slice(11, 16);
  return `${fecha(v)} ${h}`;
};

// Color de cada estado / situación (clase CSS de la insignia).
const COLORES = {
  Activo: 'verde', Inactivo: 'gris',
  Disponible: 'verde', 'En ruta': 'azul', Mantenimiento: 'ambar',
  Pendiente: 'ambar', 'Vista por conductor': 'azul',
  Reportada: 'ambar', 'En revisión': 'azul', Resuelta: 'verde',
  Baja: 'verde', Media: 'ambar', Alta: 'rojo',
  Subida: 'azul', Bajada: 'ambar'
};

export const insignia = (valor) =>
  valor ? `<span class="insignia ${COLORES[valor] ?? 'gris'}">${escapar(valor)}</span>` : '';

export function formatearCelda(columna, valor) {
  switch (columna.tipo) {
    case 'insignia': return insignia(valor);
    case 'hora': return escapar(hora(valor));
    case 'fecha': return escapar(fecha(valor));
    case 'fechahora': return escapar(fechaHora(valor));
    case 'si-no': return valor ? 'Sí' : 'No';
    default: return escapar(valor);
  }
}
