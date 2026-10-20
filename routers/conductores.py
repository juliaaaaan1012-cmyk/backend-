from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Conductor
from schemas import ConductorCreate, ConductorResponse
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos


router = APIRouter(prefix="/conductores", tags=["Conductores"])
CLAVE = "conductores"
NOMBRE = "Conductor"


@router.get("/", response_model=list[ConductorResponse])
def obtener_todos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE)),
):
    consulta = solo_activos(db.query(Conductor), Conductor, incluir_inactivos)
    return consulta.order_by(Conductor.id).all()


@router.get("/{id}", response_model=ConductorResponse)
def obtener_uno(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, Conductor, id, NOMBRE)


@router.post("/", response_model=ConductorResponse)
def crear(
    cuerpo: ConductorCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nuevo = Conductor(**datos(cuerpo))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=ConductorResponse)
def actualizar(
    id: int,
    cuerpo: ConductorCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, Conductor, id, NOMBRE)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))):
    obj = obtener_o_404(db, Conductor, id, NOMBRE)
    return baja_logica(db, obj, NOMBRE)
