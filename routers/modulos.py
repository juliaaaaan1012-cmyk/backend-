from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Modulo
from schemas import ModuloCreate, ModuloResponse
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos


router = APIRouter(prefix="/modulos", tags=["Módulos"])
CLAVE = "modulos"
NOMBRE = "Módulo"


@router.get("/", response_model=list[ModuloResponse])
def obtener_todos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE)),
):
    consulta = solo_activos(db.query(Modulo), Modulo, incluir_inactivos)
    return consulta.order_by(Modulo.id).all()


@router.get("/{id}", response_model=ModuloResponse)
def obtener_uno(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, Modulo, id, NOMBRE)


@router.post("/", response_model=ModuloResponse)
def crear(
    cuerpo: ModuloCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nuevo = Modulo(**datos(cuerpo))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=ModuloResponse)
def actualizar(
    id: int,
    cuerpo: ModuloCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, Modulo, id, NOMBRE)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))):
    obj = obtener_o_404(db, Modulo, id, NOMBRE)
    return baja_logica(db, obj, NOMBRE)
