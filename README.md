# Gestión de Transporte Escolar (RutaEscolar)

API FastAPI + frontend Svelte (Vite) + PostgreSQL. Roles: Administrador, Conductor, Acudiente, Estudiante.

```text
gestion-transporte-api/
├── routers/         # un archivo por entidad (misma estructura de la clase 1)
├── models.py        # tablas (todas con creado, actualizado y estado)
├── schemas.py       # validación y respuestas
├── auth.py          # JWT + permisos leídos de roles_modulos
├── scope.py         # qué datos ve cada rol
├── utils.py         # ayudas compartidas (baja lógica, etc.)
├── seed.py          # roles, módulos, permisos y datos de ejemplo
├── main.py
└── frontend/        # Svelte: components/ (componentes reutilizables), lib/
```

## Lo nuevo (indicaciones del profesor)

- **Tablas `modulos` y `roles_modulos`**: el menú de cada rol y sus permisos (crear/editar/eliminar) salen de la base de datos.
- **`creado`, `actualizado` y `estado` en TODAS las tablas.** Eliminar = `estado = 'Inactivo'` (no se borra la fila).
- **Login con JWT** y selector de rol (`POST /auth/login`).
- **Conductor**: reporta *fallas del vehículo* (`/fallas-vehiculo`) y ve las *ausencias* avisadas por los acudientes.
- **Acudiente**: reporta *ausencias* de sus hijos y ve abordajes y alertas de vehículos de sus rutas.
- Cambios de nombre: `vehiculos.estado` → `disponibilidad`; `conductores.activo` y `rutas.estado` → `estado` común.

### Funcionamiento entre roles
1. Conductor registra un abordaje → acudiente y estudiante lo ven.
2. Acudiente/estudiante reporta ausencia → el conductor la ve y la marca "Vista por conductor" → el acudiente ve el cambio.
3. Conductor reporta una falla → el administrador la pone "En revisión" (el vehículo pasa a *Mantenimiento*) o "Resuelta" → acudientes y estudiantes de esa ruta ven la alerta.

## Desarrollo local

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env        # y configura DATABASE_URL y JWT_SECRET
python seed.py --reset        # crea tablas y carga datos (BORRA las tablas del proyecto)
uvicorn main:app --reload
```

Frontend: `cd frontend`, copia `.env.example` a `.env`, `npm install`, `npm run dev`.

Cuentas de prueba (el login pide también el rol): `admin@rutaescolar.co / Admin2026*`;
los demás usuarios usan `Ruta2026*` (el seed imprime un correo de ejemplo por rol).

## Nube

1. `python seed.py --reset` apuntando al `DATABASE_URL` de la base en la nube (Supabase/Postgres).
2. Render: variables `DATABASE_URL`, `CORS_ORIGINS` (URL del frontend, sin barra final) y `JWT_SECRET`.
3. Frontend: `VITE_API_URL=https://tu-api.onrender.com`, `npm run build` y publica `frontend/dist`.
