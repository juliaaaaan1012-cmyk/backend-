from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import Usuario
from schemas import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from utils import aplicar, baja_logica, datos, obtener_o_404, solo_activos
from auth import hash_password

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])
CLAVE = "usuarios"
NOMBRE = "Usuario"


@router.get("/", response_model=list[UsuarioResponse])
def obtener_todos(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE)),
):
    consulta = solo_activos(db.query(Usuario), Usuario, incluir_inactivos)
    return consulta.order_by(Usuario.id).all()


@router.get("/{id}", response_model=UsuarioResponse)
def obtener_uno(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE))):
    return obtener_o_404(db, Usuario, id, NOMBRE)


@router.post("/", response_model=UsuarioResponse)
def crear(
    cuerpo: UsuarioCreate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "crear")),
):
    valores = datos(cuerpo, excluir=("password",))
    nuevo = Usuario(**valores, password_hash=hash_password(cuerpo.password))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{id}", response_model=UsuarioResponse)
def actualizar(
    id: int,
    cuerpo: UsuarioUpdate,
    db: Session = Depends(get_db),
    _=Depends(permiso(CLAVE, "editar")),
):
    obj = obtener_o_404(db, Usuario, id, NOMBRE)
    valores = cuerpo.model_dump(exclude={"password"})
    aplicar(obj, valores)
    if cuerpo.password:
        obj.password_hash = hash_password(cuerpo.password)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{id}")
def eliminar(id: int, db: Session = Depends(get_db), _=Depends(permiso(CLAVE, "eliminar"))):
    obj = obtener_o_404(db, Usuario, id, NOMBRE)
    return baja_logica(db, obj, NOMBRE)
