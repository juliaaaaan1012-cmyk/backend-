"""Autenticación JWT y permisos por módulo (tabla roles_modulos)."""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import Modulo, RolModulo, Usuario

SECRET_KEY = os.getenv("JWT_SECRET", "cambia-esta-clave-en-produccion")
ALGORITMO = "HS256"
HORAS_SESION = 8
ITERACIONES = 120_000

bearer = HTTPBearer(auto_error=False)


# ---------------- contraseñas ----------------

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), ITERACIONES
    ).hex()
    return f"pbkdf2${ITERACIONES}${salt}${h}"


def verificar_password(password: str, almacenado: str) -> bool:
    try:
        _, iteraciones, salt, h = almacenado.split("$")
        calculado = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), int(iteraciones)
        ).hex()
        return hmac.compare_digest(calculado, h)
    except (ValueError, AttributeError):
        return False


# ---------------- token ----------------

def crear_token(usuario: Usuario) -> str:
    payload = {
        "sub": str(usuario.id),
        "rol": usuario.rol.nombre,
        "exp": datetime.now(timezone.utc) + timedelta(hours=HORAS_SESION),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITMO)


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if not credenciales:
        raise HTTPException(401, "Debes iniciar sesión")
    try:
        payload = jwt.decode(
            credenciales.credentials, SECRET_KEY, algorithms=[ALGORITMO]
        )
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(401, "Sesión inválida o vencida")

    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id, Usuario.estado == "Activo"
    ).first()
    if not usuario:
        raise HTTPException(401, "Usuario no disponible")
    return usuario


# ---------------- permisos ----------------

def permisos_del_rol(db: Session, rol_id: int):
    """Módulos activos del rol, ordenados, leídos de roles_modulos."""
    return (
        db.query(RolModulo, Modulo)
        .join(Modulo, RolModulo.modulo_id == Modulo.id)
        .filter(
            RolModulo.rol_id == rol_id,
            RolModulo.estado == "Activo",
            Modulo.estado == "Activo",
        )
        .order_by(Modulo.orden)
        .all()
    )


def permiso(clave: str, accion: str = "ver"):
    """Dependencia: exige que el rol del usuario tenga el módulo `clave`
    y, si aplica, la acción 'crear', 'editar' o 'eliminar'."""
    campo = {
        "crear": "puede_crear",
        "editar": "puede_editar",
        "eliminar": "puede_eliminar",
    }.get(accion)

    def verificar(
        usuario: Usuario = Depends(usuario_actual),
        db: Session = Depends(get_db),
    ) -> Usuario:
        for rm, modulo in permisos_del_rol(db, usuario.rol_id):
            if modulo.clave == clave:
                if campo and not getattr(rm, campo):
                    raise HTTPException(
                        403, "Tu rol no tiene permiso para esta acción"
                    )
                return usuario
        raise HTTPException(403, "Tu rol no tiene acceso a este módulo")

    return verificar
