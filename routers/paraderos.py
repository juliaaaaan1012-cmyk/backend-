from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Paradero
from schemas import ParaderoCreate, ParaderoResponse
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos


router = APIRouter(prefix="/paraderos", tags=["Paraderos"])
CLAVE = "paraderos"
NOMBRE = "Paradero"


@router.get("/", response_model=list[ParaderoResponse])
def obtener_todos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE)),
):
    consulta = solo_activos(db.query(Paradero), Paradero, incluir_inactivos)
    return consulta.order_by(Paradero.id).all()


@router.get("/{id}", response_model=ParaderoResponse)
def obtener_uno(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, Paradero, id, NOMBRE)


@router.post("/", response_model=ParaderoResponse)
def crear(
    cuerpo: ParaderoCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nuevo = Paradero(**datos(cuerpo))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=ParaderoResponse)
def actualizar(
    id: int,
    cuerpo: ParaderoCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, Paradero, id, NOMBRE)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))):
    obj = obtener_o_404(db, Paradero, id, NOMBRE)
    return baja_logica(db, obj, NOMBRE)
