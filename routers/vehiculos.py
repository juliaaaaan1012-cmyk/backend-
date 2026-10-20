from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Vehiculo
from schemas import VehiculoCreate, VehiculoResponse
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos


router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])
CLAVE = "vehiculos"
NOMBRE = "Vehículo"


@router.get("/", response_model=list[VehiculoResponse])
def obtener_todos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE)),
):
    consulta = solo_activos(db.query(Vehiculo), Vehiculo, incluir_inactivos)
    return consulta.order_by(Vehiculo.id).all()


@router.get("/{id}", response_model=VehiculoResponse)
def obtener_uno(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, Vehiculo, id, NOMBRE)


@router.post("/", response_model=VehiculoResponse)
def crear(
    cuerpo: VehiculoCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nuevo = Vehiculo(**datos(cuerpo))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=VehiculoResponse)
def actualizar(
    id: int,
    cuerpo: VehiculoCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, Vehiculo, id, NOMBRE)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))):
    obj = obtener_o_404(db, Vehiculo, id, NOMBRE)
    return baja_logica(db, obj, NOMBRE)
