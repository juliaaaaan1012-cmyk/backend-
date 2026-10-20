// Descripción de cada módulo: columnas de la tabla y campos del formulario.
// IMPORTANTE: el MENÚ y los PERMISOS no están aquí; salen de la base de datos
// (tabla roles_modulos). Aquí solo se define CÓMO se ve cada módulo.
//
// Tipos de columna: texto | insignia | hora | fecha | fechahora | si-no
// Campos: tipo text|email|tel|number|date|time|password|textarea|boolean|select
//   - source: carga las opciones desde otro módulo (el usuario ve nombres, no IDs)
//   - visibleFor: roles que ven el campo
//   - required: true | false | 'crear' (solo al crear)

const ADMIN = 'Administrador';

export const etiquetaDeFuente = {
  roles: (x) => x.nombre,
  modulos: (x) => x.nombre,
  usuarios: (x) => `${x.nombre_completo} (${x.rol_nombre})`,
  acudientes: (x) => x.nombre_completo,
  estudiantes: (x) => x.nombre_completo,
  conductores: (x) => x.nombre_completo,
  vehiculos: (x) => `${x.placa} · ${x.marca ?? ''}`,
  rutas: (x) => x.nombre,
  paraderos: (x) => x.nombre
};

export const recursos = {
  roles: {
    columnas: [
      { key: 'nombre', label: 'Rol' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'nombre', label: 'Nombre del rol', type: 'text', required: true },
      { key: 'descripcion', label: 'Descripción', type: 'text' }
    ]
  },

  modulos: {
    columnas: [
      { key: 'icono', label: 'Icono' },
      { key: 'nombre', label: 'Módulo' },
      { key: 'clave', label: 'Clave' },
      { key: 'orden', label: 'Orden' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'nombre', label: 'Nombre del módulo', type: 'text', required: true },
      { key: 'clave', label: 'Clave (ruta de la API)', type: 'text', required: true },
      { key: 'icono', label: 'Icono (emoji)', type: 'text' },
      { key: 'orden', label: 'Orden en el menú', type: 'number', required: true }
    ]
  },

  'roles-modulos': {
    columnas: [
      { key: 'rol_nombre', label: 'Rol' },
      { key: 'modulo_nombre', label: 'Módulo' },
      { key: 'etiqueta', label: 'Nombre en el menú' },
      { key: 'puede_crear', label: 'Crear', tipo: 'si-no' },
      { key: 'puede_editar', label: 'Editar', tipo: 'si-no' },
      { key: 'puede_eliminar', label: 'Eliminar', tipo: 'si-no' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'rol_id', label: 'Rol', type: 'select', source: 'roles', required: true },
      { key: 'modulo_id', label: 'Módulo', type: 'select', source: 'modulos', required: true },
      { key: 'etiqueta', label: 'Nombre en el menú (opcional)', type: 'text' },
      { key: 'puede_crear', label: 'Puede crear', type: 'boolean' },
      { key: 'puede_editar', label: 'Puede editar', type: 'boolean' },
      { key: 'puede_eliminar', label: 'Puede eliminar', type: 'boolean' }
    ]
  },

  usuarios: {
    columnas: [
      { key: 'nombre_completo', label: 'Nombre' },
      { key: 'correo', label: 'Correo' },
      { key: 'telefono', label: 'Teléfono' },
      { key: 'rol_nombre', label: 'Rol' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'nombre', label: 'Nombres', type: 'text', required: true },
      { key: 'apellido', label: 'Apellidos', type: 'text', required: true },
      { key: 'correo', label: 'Correo', type: 'email', required: true },
      { key: 'telefono', label: 'Teléfono', type: 'tel' },
      { key: 'rol_id', label: 'Rol', type: 'select', source: 'roles', required: true },
      { key: 'password', label: 'Contraseña', type: 'password', required: 'crear',
        ayuda: 'Al editar, déjala vacía para conservar la actual.' }
    ]
  },

  acudientes: {
    columnas: [
      { key: 'nombre_completo', label: 'Acudiente' },
      { key: 'documento', label: 'Documento' },
      { key: 'telefono', label: 'Teléfono' },
      { key: 'correo', label: 'Correo' },
      { key: 'usuario_nombre', label: 'Cuenta de acceso' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'nombre', label: 'Nombres', type: 'text', required: true },
      { key: 'apellido', label: 'Apellidos', type: 'text', required: true },
      { key: 'documento', label: 'Documento', type: 'text', required: true },
      { key: 'telefono', label: 'Teléfono', type: 'tel', required: true },
      { key: 'correo', label: 'Correo', type: 'email' },
      { key: 'usuario_id', label: 'Cuenta de acceso', type: 'select', source: 'usuarios', required: true }
    ]
  },

  estudiantes: {
    columnas: [
      { key: 'nombre_completo', label: 'Estudiante' },
      { key: 'documento', label: 'Documento' },
      { key: 'grado', label: 'Grado' },
      { key: 'direccion', label: 'Dirección' },
      { key: 'acudiente_nombre', label: 'Acudiente' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'nombre', label: 'Nombres', type: 'text', required: true, visibleFor: [ADMIN, 'Acudiente'] },
      { key: 'apellido', label: 'Apellidos', type: 'text', required: true, visibleFor: [ADMIN, 'Acudiente'] },
      { key: 'documento', label: 'Documento', type: 'text', required: true, visibleFor: [ADMIN, 'Acudiente'] },
      { key: 'grado', label: 'Grado', type: 'text' },
      { key: 'direccion', label: 'Dirección de recogida', type: 'text' },
      { key: 'acudiente_id', label: 'Acudiente', type: 'select', source: 'acudientes', required: true, visibleFor: [ADMIN] },
      { key: 'usuario_id', label: 'Cuenta de acceso', type: 'select', source: 'usuarios', visibleFor: [ADMIN] }
    ]
  },

  conductores: {
    columnas: [
      { key: 'nombre_completo', label: 'Conductor' },
      { key: 'documento', label: 'Documento' },
      { key: 'licencia', label: 'Licencia' },
      { key: 'telefono', label: 'Teléfono' },
      { key: 'usuario_nombre', label: 'Cuenta de acceso' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'nombre', label: 'Nombres', type: 'text', required: true },
      { key: 'apellido', label: 'Apellidos', type: 'text', required: true },
      { key: 'documento', label: 'Documento', type: 'text', required: true },
      { key: 'licencia', label: 'Licencia de conducción', type: 'text', required: true },
      { key: 'telefono', label: 'Teléfono', type: 'tel' },
      { key: 'usuario_id', label: 'Cuenta de acceso', type: 'select', source: 'usuarios' }
    ]
  },

  vehiculos: {
    columnas: [
      { key: 'placa', label: 'Placa' },
      { key: 'marca', label: 'Marca' },
      { key: 'modelo', label: 'Modelo' },
      { key: 'capacidad', label: 'Capacidad' },
      { key: 'disponibilidad', label: 'Disponibilidad', tipo: 'insignia' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'placa', label: 'Placa', type: 'text', required: true },
      { key: 'marca', label: 'Marca', type: 'text' },
      { key: 'modelo', label: 'Modelo', type: 'text' },
      { key: 'capacidad', label: 'Capacidad (pasajeros)', type: 'number', required: true },
      { key: 'disponibilidad', label: 'Disponibilidad', type: 'select',
        options: ['Disponible', 'En ruta', 'Mantenimiento'], required: true }
    ]
  },

  rutas: {
    columnas: [
      { key: 'nombre', label: 'Ruta' },
      { key: 'hora_salida', label: 'Salida', tipo: 'hora' },
      { key: 'hora_llegada', label: 'Llegada', tipo: 'hora' },
      { key: 'conductor_nombre', label: 'Conductor' },
      { key: 'vehiculo_placa', label: 'Vehículo' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'nombre', label: 'Nombre de la ruta', type: 'text', required: true },
      { key: 'descripcion', label: 'Descripción', type: 'text' },
      { key: 'hora_salida', label: 'Hora de salida', type: 'time', required: true },
      { key: 'hora_llegada', label: 'Hora de llegada', type: 'time' },
      { key: 'conductor_id', label: 'Conductor', type: 'select', source: 'conductores', required: true },
      { key: 'vehiculo_id', label: 'Vehículo', type: 'select', source: 'vehiculos', required: true }
    ]
  },

  paraderos: {
    columnas: [
      { key: 'nombre', label: 'Paradero' },
      { key: 'direccion', label: 'Dirección' },
      { key: 'referencia', label: 'Referencia' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'nombre', label: 'Nombre', type: 'text', required: true },
      { key: 'direccion', label: 'Dirección', type: 'text', required: true },
      { key: 'referencia', label: 'Referencia', type: 'text' },
      { key: 'latitud', label: 'Latitud', type: 'number', paso: 'any' },
      { key: 'longitud', label: 'Longitud', type: 'number', paso: 'any' }
    ]
  },

  'estudiante-ruta': {
    columnas: [
      { key: 'estudiante_nombre', label: 'Estudiante' },
      { key: 'ruta_nombre', label: 'Ruta' },
      { key: 'paradero_nombre', label: 'Paradero' },
      { key: 'hora_salida', label: 'Hora de salida', tipo: 'hora' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'estudiante_id', label: 'Estudiante', type: 'select', source: 'estudiantes', required: true },
      { key: 'ruta_id', label: 'Ruta', type: 'select', source: 'rutas', required: true },
      { key: 'paradero_id', label: 'Paradero', type: 'select', source: 'paraderos', required: true }
    ]
  },

  'registros-abordaje': {
    columnas: [
      { key: 'fecha_hora', label: 'Fecha y hora', tipo: 'fechahora' },
      { key: 'estudiante_nombre', label: 'Estudiante' },
      { key: 'ruta_nombre', label: 'Ruta' },
      { key: 'tipo', label: 'Tipo', tipo: 'insignia' },
      { key: 'estado', label: 'Estado', tipo: 'insignia' }
    ],
    campos: [
      { key: 'estudiante_id', label: 'Estudiante', type: 'select', source: 'estudiantes', required: true },
      { key: 'ruta_id', label: 'Ruta', type: 'select', source: 'rutas', required: true },
      { key: 'tipo', label: 'Tipo de registro', type: 'select', options: ['Subida', 'Bajada'], required: true }
    ]
  },

  ausencias: {
    columnas: [
      { key: 'fecha', label: 'Fecha', tipo: 'fecha' },
      { key: 'estudiante_nombre', label: 'Estudiante' },
      { key: 'ruta_nombre', label: 'Ruta' },
      { key: 'motivo', label: 'Motivo' },
      { key: 'atencion', label: 'Atención', tipo: 'insignia' },
      { key: 'reportado_por_nombre', label: 'Reportado por' }
    ],
    campos: [
      { key: 'estudiante_id', label: 'Estudiante', type: 'select', source: 'estudiantes',
        required: true, visibleFor: [ADMIN, 'Acudiente'] },
      { key: 'fecha', label: 'Fecha de la ausencia', type: 'date', required: true,
        visibleFor: [ADMIN, 'Acudiente', 'Estudiante'] },
      { key: 'motivo', label: 'Motivo', type: 'text', required: true,
        visibleFor: [ADMIN, 'Acudiente', 'Estudiante'] },
      { key: 'atencion', label: 'Atención', type: 'select',
        options: ['Pendiente', 'Vista por conductor'], visibleFor: [ADMIN, 'Conductor'] }
    ]
  },

  'fallas-vehiculo': {
    columnas: [
      { key: 'fecha_hora', label: 'Reportada', tipo: 'fechahora' },
      { key: 'ruta_nombre', label: 'Ruta' },
      { key: 'vehiculo_placa', label: 'Vehículo' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'gravedad', label: 'Gravedad', tipo: 'insignia' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'atencion', label: 'Estado de la falla', tipo: 'insignia' }
    ],
    campos: [
      { key: 'ruta_id', label: 'Ruta afectada', type: 'select', source: 'rutas', required: true },
      { key: 'tipo', label: 'Tipo de falla', type: 'select',
        options: ['Mecánica', 'Eléctrica', 'Llantas', 'Frenos', 'Accidente', 'Otra'], required: true },
      { key: 'gravedad', label: 'Gravedad', type: 'select', options: ['Baja', 'Media', 'Alta'], required: true },
      { key: 'descripcion', label: 'Descripción de la falla', type: 'textarea', required: true },
      { key: 'atencion', label: 'Estado de la falla', type: 'select',
        options: ['Reportada', 'En revisión', 'Resuelta'], visibleFor: [ADMIN] },
      { key: 'observacion_admin', label: 'Observación del administrador', type: 'textarea', visibleFor: [ADMIN] }
    ]
  }
};

// Mensajes de bienvenida por rol (pantalla de inicio).
export const bienvenida = {
  Administrador: 'Controla rutas, vehículos, usuarios y permisos desde un solo lugar.',
  Conductor: 'Registra los abordajes, revisa las ausencias y reporta fallas de tu vehículo.',
  Acudiente: 'Sigue el transporte de tus hijos y avisa cuando no tomarán la ruta.',
  Estudiante: 'Consulta tu ruta, tus abordajes y las alertas de tu vehículo.'
};
