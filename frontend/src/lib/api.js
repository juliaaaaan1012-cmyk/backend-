// Cliente de la API. Guarda el token JWT y lo envía en cada petición.
const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');
const CLAVE_SESION = 'rutaescolar_sesion';

let alVencerSesion = () => {};
export const alSesionVencida = (fn) => { alVencerSesion = fn; };

export const sesionGuardada = {
  leer() {
    try { return JSON.parse(localStorage.getItem(CLAVE_SESION)); } catch { return null; }
  },
  guardar(datos) { localStorage.setItem(CLAVE_SESION, JSON.stringify(datos)); },
  borrar() { localStorage.removeItem(CLAVE_SESION); }
};

async function peticion(ruta, opciones = {}, conToken = true) {
  const headers = { 'Content-Type': 'application/json' };
  const token = sesionGuardada.leer()?.access_token;
  if (conToken && token) headers.Authorization = `Bearer ${token}`;

  let respuesta;
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, { ...opciones, headers });
  } catch {
    throw new Error('No hay conexión con el servidor. Intenta de nuevo en unos segundos.');
  }

  if (respuesta.status === 401 && conToken) alVencerSesion();

  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => ({}));
    const detalle = cuerpo.detail;
    throw new Error(
      typeof detalle === 'string' ? detalle : 'Revisa los datos ingresados e intenta de nuevo.'
    );
  }
  return respuesta.json();
}

export const api = {
  roles: () => peticion('/auth/roles', {}, false),
  login: (datos) => peticion('/auth/login', { method: 'POST', body: JSON.stringify(datos) }, false),
  yo: () => peticion('/auth/me'),
  listar: (recurso) => peticion(`/${recurso}/`),
  crear: (recurso, datos) => peticion(`/${recurso}/`, { method: 'POST', body: JSON.stringify(datos) }),
  actualizar: (recurso, id, datos) =>
    peticion(`/${recurso}/${id}`, { method: 'PUT', body: JSON.stringify(datos) }),
  eliminar: (recurso, id) => peticion(`/${recurso}/${id}`, { method: 'DELETE' })
};
