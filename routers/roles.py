from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Rol
from schemas import RolCreate, RolResponse
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos


router = APIRouter(prefix="/roles", tags=["Roles"])
CLAVE = "roles"
NOMBRE = "Rol"


@router.get("/", response_model=list[RolResponse])
def obtener_todos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE)),
):
    consulta = solo_activos(db.query(Rol), Rol, incluir_inactivos)
    return consulta.order_by(Rol.id).all()


@router.get("/{id}", response_model=RolResponse)
def obtener_uno(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, Rol, id, NOMBRE)


@router.post("/", response_model=RolResponse)
def crear(
    cuerpo: RolCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nuevo = Rol(**datos(cuerpo))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=RolResponse)
def actualizar(
    id: int,
    cuerpo: RolCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, Rol, id, NOMBRE)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))):
    obj = obtener_o_404(db, Rol, id, NOMBRE)
    return baja_logica(db, obj, NOMBRE)
