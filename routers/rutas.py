from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Ruta
from schemas import RutaCreate, RutaResponse
from scope import ids_rutas
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos

router = APIRouter(prefix="/rutas", tags=["Rutas"])
CLAVE = "rutas"
NOMBRE = "Ruta"


@router.get("/", response_model=list[RutaResponse])
def obtener_rutas(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE)),
):
    q = solo_activos(db.query(Ruta), Ruta, incluir_inactivos)
    ids = ids_rutas(db, usuario)
    if ids is not None:
        q = q.filter(Ruta.id.in_(ids or [-1]))
    return q.order_by(Ruta.id).all()


@router.get("/{id}", response_model=RutaResponse)
def obtener_ruta(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, Ruta, id, NOMBRE)


@router.post("/", response_model=RutaResponse)
def crear_ruta(
    cuerpo: RutaCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nueva = Ruta(**datos(cuerpo))
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.put("/{id}", response_model=RutaResponse)
def actualizar_ruta(
    id: int, cuerpo: RutaCreate, db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    ruta = obtener_o_404(db, Ruta, id, NOMBRE)
    aplicar(ruta, cuerpo.model_dump())
    db.commit()
    db.refresh(ruta)
    return ruta


@router.delete("/{id}")
def eliminar_ruta(
    id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))
):
    return baja_logica(db, obtener_o_404(db, Ruta, id, NOMBRE), NOMBRE)
