from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import EstudianteRuta, RegistroAbordaje, ahora
from schemas import RegistroAbordajeCreate, RegistroAbordajeResponse
from scope import es_admin, ids_estudiantes, ids_rutas
from utils import aplicar, baja_logica, datos, solo_activos

router = APIRouter(prefix="/registros-abordaje", tags=["Registros de abordaje"])
CLAVE = "registros-abordaje"
NOMBRE = "Registro de abordaje"


def _consulta_visible(db, usuario):
    q = db.query(RegistroAbordaje)
    if es_admin(usuario):
        return q
    rol = usuario.rol.nombre
    if rol == "Conductor":
        return q.filter(RegistroAbordaje.ruta_id.in_(ids_rutas(db, usuario) or [-1]))
    return q.filter(
        RegistroAbordaje.estudiante_id.in_(ids_estudiantes(db, usuario) or [-1])
    )


def _obtener(db, usuario, id):
    obj = _consulta_visible(db, usuario).filter(RegistroAbordaje.id == id).first()
    if not obj:
        raise HTTPException(404, f"{NOMBRE} no encontrado")
    return obj


def _validar(db, usuario, estudiante_id, ruta_id):
    """El conductor solo registra en sus rutas, y el estudiante debe
    estar asignado a esa ruta."""
    if not es_admin(usuario) and ruta_id not in (ids_rutas(db, usuario) or []):
        raise HTTPException(403, "Esa ruta no está a tu cargo")
    asignado = db.query(EstudianteRuta).filter(
        EstudianteRuta.estudiante_id == estudiante_id,
        EstudianteRuta.ruta_id == ruta_id,
        EstudianteRuta.estado == "Activo",
    ).first()
    if not asignado:
        raise HTTPException(400, "El estudiante no está asignado a esa ruta")


@router.get("/", response_model=list[RegistroAbordajeResponse])
def obtener_abordajes(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE)),
):
    q = solo_activos(_consulta_visible(db, usuario), RegistroAbordaje, incluir_inactivos)
    return q.order_by(RegistroAbordaje.fecha_hora.desc()).all()


@router.get("/{id}", response_model=RegistroAbordajeResponse)
def obtener_abordaje(id: int, db: Session = Depends(get_db), usuario=Depends(permiso(CLAVE))):
    return _obtener(db, usuario, id)


@router.post("/", response_model=RegistroAbordajeResponse)
def crear_abordaje(
    cuerpo: RegistroAbordajeCreate, db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "crear")),
):
    _validar(db, usuario, cuerpo.estudiante_id, cuerpo.ruta_id)
    nuevo = RegistroAbordaje(**datos(cuerpo), fecha_hora=ahora())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=RegistroAbordajeResponse)
def actualizar_abordaje(
    id: int, cuerpo: RegistroAbordajeCreate, db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "editar")),
):
    obj = _obtener(db, usuario, id)
    _validar(db, usuario, cuerpo.estudiante_id, cuerpo.ruta_id)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar_abordaje(
    id: int, db: Session = Depends(get_db), usuario=Depends(permiso(CLAVE, "eliminar"))
):
    return baja_logica(db, _obtener(db, usuario, id), NOMBRE)
