"""Ausencias: el acudiente/estudiante avisa; el conductor lo ve y lo confirma."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Ausencia, Estudiante, EstudianteRuta
from schemas import AusenciaCreate, AusenciaResponse
from scope import (
    consulta_estudiantes, es_admin, estudiante_de, ids_estudiantes,
)
from utils import aplicar, baja_logica, solo_activos

router = APIRouter(prefix="/ausencias", tags=["Ausencias"])
CLAVE = "ausencias"
NOMBRE = "Ausencia"


def _consulta_visible(db, usuario):
    q = db.query(Ausencia)
    if es_admin(usuario):
        return q
    return q.filter(Ausencia.estudiante_id.in_(ids_estudiantes(db, usuario) or [-1]))


def _obtener(db, usuario, id):
    obj = _consulta_visible(db, usuario).filter(Ausencia.id == id).first()
    if not obj:
        raise HTTPException(404, f"{NOMBRE} no encontrada")
    return obj


def _estudiante_objetivo(db, usuario, estudiante_id):
    """Un estudiante solo reporta por sí mismo; un acudiente, por sus hijos."""
    if usuario.rol.nombre == "Estudiante":
        propio = estudiante_de(db, usuario)
        if not propio:
            raise HTTPException(403, "Tu usuario no tiene un estudiante asociado")
        return propio
    if not estudiante_id:
        raise HTTPException(422, "Debes seleccionar el estudiante")
    est = consulta_estudiantes(db, usuario).filter(Estudiante.id == estudiante_id).first()
    if not est:
        raise HTTPException(404, "Estudiante no encontrado")
    return est


def _ruta_del_estudiante(db, estudiante_id):
    asignacion = db.query(EstudianteRuta).filter(
        EstudianteRuta.estudiante_id == estudiante_id,
        EstudianteRuta.estado == "Activo",
    ).first()
    return asignacion.ruta_id if asignacion else None


@router.get("/", response_model=list[AusenciaResponse])
def obtener_ausencias(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE)),
):
    q = solo_activos(_consulta_visible(db, usuario), Ausencia, incluir_inactivos)
    return q.order_by(Ausencia.fecha.desc(), Ausencia.id.desc()).all()


@router.get("/{id}", response_model=AusenciaResponse)
def obtener_ausencia(id: int, db: Session = Depends(get_db), usuario=Depends(permiso(CLAVE))):
    return _obtener(db, usuario, id)


@router.post("/", response_model=AusenciaResponse)
def crear_ausencia(
    cuerpo: AusenciaCreate, db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "crear")),
):
    estudiante = _estudiante_objetivo(db, usuario, cuerpo.estudiante_id)
    nueva = Ausencia(
        estudiante_id=estudiante.id,
        ruta_id=_ruta_del_estudiante(db, estudiante.id),
        fecha=cuerpo.fecha,
        motivo=cuerpo.motivo,
        atencion="Pendiente",
        reportado_por_id=usuario.id,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.put("/{id}", response_model=AusenciaResponse)
def actualizar_ausencia(
    id: int, cuerpo: AusenciaCreate, db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "editar")),
):
    ausencia = _obtener(db, usuario, id)
    rol = usuario.rol.nombre

    if rol == "Conductor":
        # El conductor solo confirma que ya vio el aviso.
        if cuerpo.atencion:
            ausencia.atencion = cuerpo.atencion
    else:
        ausencia.fecha = cuerpo.fecha
        ausencia.motivo = cuerpo.motivo
        if rol == "Administrador":
            if cuerpo.atencion:
                ausencia.atencion = cuerpo.atencion
            if cuerpo.estudiante_id:
                ausencia.estudiante_id = cuerpo.estudiante_id
                ausencia.ruta_id = _ruta_del_estudiante(db, cuerpo.estudiante_id)
        aplicar(ausencia, {"estado": cuerpo.estado})

    db.commit()
    db.refresh(ausencia)
    return ausencia


@router.delete("/{id}")
def eliminar_ausencia(
    id: int, db: Session = Depends(get_db), usuario=Depends(permiso(CLAVE, "eliminar"))
):
    return baja_logica(db, _obtener(db, usuario, id), NOMBRE)
