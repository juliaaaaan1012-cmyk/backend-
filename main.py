import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from database import Base, engine
import models  # noqa: F401  (registra las tablas)

# ============================================================
# ROUTERS
# ============================================================

from routers.auth import router as auth_router
from routers.roles import router as roles_router
from routers.modulos import router as modulos_router
from routers.roles_modulos import router as roles_modulos_router
from routers.usuarios import router as usuarios_router
from routers.acudientes import router as acudientes_router
from routers.estudiantes import router as estudiantes_router
from routers.conductores import router as conductores_router
from routers.vehiculos import router as vehiculos_router
from routers.rutas import router as rutas_router
from routers.paraderos import router as paraderos_router
from routers.estudiante_ruta import router as estudiante_ruta_router
from routers.registros_abordaje import router as registros_abordaje_router
from routers.ausencias import router as ausencias_router
from routers.fallas_vehiculo import router as fallas_vehiculo_router

# ============================================================
# CREACIÓN DE LA API
# ============================================================

app = FastAPI(
    title="Gestión de Rutas y Transporte Escolar",
    description="API para la gestión del transporte escolar",
    version="2.0.0",
)

# Crea las tablas que falten (útil en la versión local).
Base.metadata.create_all(bind=engine)

# ============================================================
# CORS
# ============================================================

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "https://fanciful-duckanoo-fc5130.netlify.app",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ERRORES DE INTEGRIDAD
# ============================================================


@app.exception_handler(IntegrityError)
async def manejar_error_integridad(request: Request, exc: IntegrityError):
    """Conflicto legible cuando se viola una clave única o foránea."""
    return JSONResponse(
        status_code=409,
        content={
            "detail": (
                "No se pudo guardar el registro: "
                "ya existe o referencia datos inexistentes."
            )
        },
    )


# ============================================================
# REGISTRO DE ROUTERS
# ============================================================

for router in (
    auth_router, roles_router, modulos_router, roles_modulos_router,
    usuarios_router, acudientes_router, estudiantes_router,
    conductores_router, vehiculos_router, rutas_router, paraderos_router,
    estudiante_ruta_router, registros_abordaje_router,
    ausencias_router, fallas_vehiculo_router,
):
    app.include_router(router)

# ============================================================
# RUTAS DE ESTADO
# ============================================================


@app.get("/")
def inicio():
    return {"mensaje": "API funcionando"}


@app.get("/health")
def health_check():
    """Para que Render compruebe que la API levantó."""
    return {"status": "ok"}


@app.get("/prueba-db")
def prueba_db():
    """Comprueba la conexión con la base de datos."""
    with engine.connect() as connection:
        resultado = connection.execute(text("SELECT 1"))
        return {
            "mensaje": "Conexion con la base de datos exitosa",
            "resultado": resultado.scalar(),
        }
