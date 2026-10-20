from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import EstudianteRuta
from schemas import EstudianteRutaCreate, EstudianteRutaResponse
from scope import ids_estudiantes
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos

router = APIRouter(prefix="/estudiante-ruta", tags=["Estudiante - Ruta"])
CLAVE = "estudiante-ruta"
NOMBRE = "Asignación"


@router.get("/", response_model=list[EstudianteRutaResponse])
def obtener_asignaciones(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE)),
):
    q = solo_activos(db.query(EstudianteRuta), EstudianteRuta, incluir_inactivos)
    ids = ids_estudiantes(db, usuario)
    if ids is not None:
        q = q.filter(EstudianteRuta.estudiante_id.in_(ids or [-1]))
    return q.order_by(EstudianteRuta.id).all()


@router.get("/{id}", response_model=EstudianteRutaResponse)
def obtener_asignacion(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, EstudianteRuta, id, NOMBRE)


@router.post("/", response_model=EstudianteRutaResponse)
def crear_asignacion(
    cuerpo: EstudianteRutaCreate, db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    nueva = EstudianteRuta(**datos(cuerpo))
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.put("/{id}", response_model=EstudianteRutaResponse)
def actualizar_asignacion(
    id: int, cuerpo: EstudianteRutaCreate, db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, EstudianteRuta, id, NOMBRE)
    aplicar(obj, cuerpo.model_dump())
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar_asignacion(
    id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))
):
    return baja_logica(db, obtener_o_404(db, EstudianteRuta, id, NOMBRE), NOMBRE)
