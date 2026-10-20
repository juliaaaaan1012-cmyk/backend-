from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import RolModulo
from schemas import RolModuloCreate, RolModuloResponse
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos


router = APIRouter(prefix="/roles-modulos", tags=["Roles y módulos"])
CLAVE = "roles-modulos"
NOMBRE = "Permiso"


@router.get("/", response_model=list[RolModuloResponse])
def obtener_todos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE)),
):
    consulta = solo_activos(db.query(RolModulo), RolModulo, incluir_inactivos)
    return consulta.order_by(RolModulo.id).all()


@router.get("/{id}", response_model=RolModuloResponse)
def obtener_uno(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, RolModulo, id, NOMBRE)


@router.post("/", response_model=RolModuloResponse)
def crear(
    cuerpo: RolModuloCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nuevo = RolModulo(**datos(cuerpo))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=RolModuloResponse)
def actualizar(
    id: int,
    cuerpo: RolModuloCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, RolModulo, id, NOMBRE)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))):
    obj = obtener_o_404(db, RolModulo, id, NOMBRE)
    return baja_logica(db, obj, NOMBRE)
