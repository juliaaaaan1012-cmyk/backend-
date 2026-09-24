# Gestión de Transporte Escolar

Proyecto con API FastAPI y frontend independiente en Svelte + Vite. El frontend no usa SvelteKit.

```text
gestion-transporte-api/
├── routers/            # Endpoints de la API
├── main.py             # Aplicación FastAPI
├── database.py         # Conexión SQLAlchemy
├── requirements.txt    # Dependencias Python
├── render.yaml         # Despliegue de la API en Render
└── frontend/           # Cliente Svelte + Vite
    ├── src/
    ├── index.html
    └── package.json
```

## Desarrollo local

1. Copia `.env.example` a `.env` y configura `DATABASE_URL`.
2. Instala y ejecuta la API:

   ```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. En otra terminal, entra a `frontend`, copia `.env.example` a `.env`, ejecuta `npm install` y después `npm run dev`.

La API está en `http://localhost:8000`, su documentación en `/docs` y el estado del servicio en `/health`.

## Despliegue

1. Crea un repositorio en GitHub desde esta carpeta y sube todos los archivos salvo los ignorados.
2. En Render crea un **Blueprint** desde el repositorio. Detectará `render.yaml` y usará `uvicorn main:app --host 0.0.0.0 --port $PORT`.
3. En Render define `DATABASE_URL` y `CORS_ORIGINS`. En `CORS_ORIGINS` incluye la URL final del frontend, sin barra al final.
4. Cuando Render publique la API, usa su URL en `frontend/.env`:

   ```env
   VITE_API_URL=https://tu-api.onrender.com
   ```

5. Ejecuta `npm run build` dentro de `frontend` y publica la carpeta `frontend/dist` en el hosting estático elegido.

Los secretos, entornos virtuales, dependencias y compilados están excluidos en `.gitignore`.
