from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Acudiente
from schemas import AcudienteCreate, AcudienteResponse
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos


router = APIRouter(prefix="/acudientes", tags=["Acudientes"])
CLAVE = "acudientes"
NOMBRE = "Acudiente"


@router.get("/", response_model=list[AcudienteResponse])
def obtener_todos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE)),
):
    consulta = solo_activos(db.query(Acudiente), Acudiente, incluir_inactivos)
    return consulta.order_by(Acudiente.id).all()


@router.get("/{id}", response_model=AcudienteResponse)
def obtener_uno(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, Acudiente, id, NOMBRE)


@router.post("/", response_model=AcudienteResponse)
def crear(
    cuerpo: AcudienteCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nuevo = Acudiente(**datos(cuerpo))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=AcudienteResponse)
def actualizar(
    id: int,
    cuerpo: AcudienteCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, Acudiente, id, NOMBRE)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))):
    obj = obtener_o_404(db, Acudiente, id, NOMBRE)
    return baja_logica(db, obj, NOMBRE)
