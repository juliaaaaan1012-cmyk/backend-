from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import (
    crear_token, permisos_del_rol, usuario_actual, verificar_password,
)
from database import get_db
from models import Rol, Usuario
from schemas import (
    LoginRequest, LoginResponse, ModuloMenu, RolResponse, UsuarioSesion,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _modulos_menu(db: Session, usuario: Usuario) -> list[ModuloMenu]:
    """El menú sale SOLO de la tabla roles_modulos."""
    return [
        ModuloMenu(
            clave=modulo.clave,
            nombre=rm.etiqueta or modulo.nombre,
            icono=modulo.icono,
            orden=modulo.orden,
            puede_crear=rm.puede_crear,
            puede_editar=rm.puede_editar,
            puede_eliminar=rm.puede_eliminar,
        )
        for rm, modulo in permisos_del_rol(db, usuario.rol_id)
    ]


def _sesion(usuario: Usuario) -> UsuarioSesion:
    return UsuarioSesion(
        id=usuario.id,
        nombre_completo=usuario.nombre_completo,
        correo=usuario.correo,
        rol=usuario.rol.nombre,
    )


@router.get("/roles", response_model=list[RolResponse])
def roles_para_login(db: Session = Depends(get_db)):
    """Lista pública de roles para el selector del login."""
    return db.query(Rol).filter(Rol.estado == "Activo").order_by(Rol.id).all()


@router.post("/login", response_model=LoginResponse)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        Usuario.correo == datos.correo.strip().lower(),
        Usuario.estado == "Activo",
    ).first()

    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(401, "Correo o contraseña incorrectos")

    if usuario.rol_id != datos.rol_id:
        raise HTTPException(
            403, "Tu usuario no pertenece al rol seleccionado"
        )

    return LoginResponse(
        access_token=crear_token(usuario),
        usuario=_sesion(usuario),
        modulos=_modulos_menu(db, usuario),
    )


@router.get("/me", response_model=LoginResponse)
def yo(usuario: Usuario = Depends(usuario_actual), db: Session = Depends(get_db)):
    return LoginResponse(
        access_token=crear_token(usuario),
        usuario=_sesion(usuario),
        modulos=_modulos_menu(db, usuario),
    )
