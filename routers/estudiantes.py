from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Estudiante
from schemas import EstudianteCreate, EstudianteResponse
from scope import acudiente_de, consulta_estudiantes, es_admin
from utils import aplicar, baja_logica, datos, solo_activos

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])
CLAVE = "estudiantes"
NOMBRE = "Estudiante"

# Qué campos puede modificar cada rol al editar.
CAMPOS_EDITABLES = {
    "Administrador": None,  # todos
    "Acudiente": {"nombre", "apellido", "documento", "grado", "direccion"},
    "Estudiante": {"grado", "direccion"},
}


def _visible(db, usuario, id):
    estudiante = consulta_estudiantes(db, usuario).filter(Estudiante.id == id).first()
    if not estudiante:
        raise HTTPException(404, "Estudiante no encontrado")
    return estudiante


@router.get("/", response_model=list[EstudianteResponse])
def obtener_estudiantes(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE)),
):
    q = solo_activos(consulta_estudiantes(db, usuario), Estudiante, incluir_inactivos)
    return q.order_by(Estudiante.id).all()


@router.get("/{id}", response_model=EstudianteResponse)
def obtener_estudiante(
    id: int, db: Session = Depends(get_db), usuario=Depends(permiso(CLAVE))
):
    return _visible(db, usuario, id)


@router.post("/", response_model=EstudianteResponse)
def crear_estudiante(
    cuerpo: EstudianteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "crear")),
):
    valores = datos(cuerpo)

    if es_admin(usuario):
        if not valores.get("acudiente_id"):
            raise HTTPException(422, "Debes seleccionar el acudiente")
    else:
        # Un acudiente solo registra estudiantes a su propio cargo.
        acudiente = acudiente_de(db, usuario)
        if not acudiente:
            raise HTTPException(403, "Tu usuario no tiene un acudiente asociado")
        valores["acudiente_id"] = acudiente.id
        valores["usuario_id"] = None

    nuevo = Estudiante(**valores)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=EstudianteResponse)
def actualizar_estudiante(
    id: int,
    cuerpo: EstudianteCreate,
    db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "editar")),
):
    estudiante = _visible(db, usuario, id)
    permitidos = CAMPOS_EDITABLES.get(usuario.rol.nombre, set())
    aplicar(estudiante, cuerpo.model_dump(exclude_unset=True), permitidos)
    db.commit()
    db.refresh(estudiante)
    return estudiante


@router.delete("/{id}")
def eliminar_estudiante(
    id: int, db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "eliminar")),
):
    return baja_logica(db, _visible(db, usuario, id), NOMBRE)
