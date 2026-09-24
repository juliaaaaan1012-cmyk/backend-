
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from database import engine


# ============================================================
# ROUTERS
# ============================================================

from routers.roles import router as roles_router
from routers.usuarios import router as usuarios_router
from routers.acudientes import router as acudientes_router
from routers.estudiantes import router as estudiantes_router
from routers.conductores import router as conductores_router
from routers.vehiculos import router as vehiculos_router
from routers.rutas import router as rutas_router
from routers.paraderos import router as paraderos_router
from routers.estudiante_ruta import router as estudiante_ruta_router
from routers.registros_abordaje import router as registros_abordaje_router


# ============================================================
# CREACIÓN DE LA API
# ============================================================

app = FastAPI(
    title="Gestión de Rutas y Transporte Escolar",
    description="API para la gestión del transporte escolar",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fanciful-duckanoo-fc5130.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CONFIGURACIÓN CORS
# ============================================================

# Permite configurar los orígenes desde Render mediante
# la variable de entorno CORS_ORIGINS.
#
# Ejemplo en Render:
#
# CORS_ORIGINS=https://fanciful-duckanoo-fc5130.netlify.app
#
# También se mantienen los orígenes utilizados durante
# el desarrollo local.

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "https://fanciful-duckanoo-fc5130.netlify.app"
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
# MANEJO DE ERRORES DE INTEGRIDAD
# ============================================================

@app.exception_handler(IntegrityError)
async def manejar_error_integridad(
    request: Request,
    exc: IntegrityError
):
    """
    Devuelve un conflicto legible cuando se viola
    una restricción de integridad de la base de datos,
    por ejemplo una clave única o una clave foránea.
    """

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

app.include_router(roles_router)
app.include_router(usuarios_router)
app.include_router(acudientes_router)
app.include_router(estudiantes_router)
app.include_router(conductores_router)
app.include_router(vehiculos_router)
app.include_router(rutas_router)
app.include_router(paraderos_router)
app.include_router(estudiante_ruta_router)
app.include_router(registros_abordaje_router)


# ============================================================
# RUTA PRINCIPAL
# ============================================================

@app.get("/")
def inicio():
    return {
        "mensaje": "API funcionando"
    }


# ============================================================
# ESTADO DEL SERVICIO
# ============================================================

@app.get("/health")
def health_check():
    """
    Endpoint liviano para comprobar que Render
    levantó correctamente la API.
    """

    return {
        "status": "ok"
    }


# ============================================================
# PRUEBA DE CONEXIÓN CON LA BASE DE DATOS
# ============================================================

@app.get("/prueba-db")
def prueba_db():
    """
    Comprueba que la API puede conectarse
    correctamente a Supabase/PostgreSQL.
    """

    with engine.connect() as connection:

        resultado = connection.execute(
            text("SELECT 1")
        )

        return {
            "mensaje": "Conexion con Supabase exitosa",
            "resultado": resultado.scalar()
        }

