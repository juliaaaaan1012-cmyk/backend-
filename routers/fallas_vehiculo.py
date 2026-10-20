"""Fallas de vehículo: las reporta el conductor, las gestiona el
administrador y las ven los acudientes y estudiantes de esa ruta."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import permiso
from database import get_db
from models import FallaVehiculo, Ruta, Vehiculo, ahora
from schemas import FallaVehiculoCreate, FallaVehiculoResponse
from scope import conductor_de, es_admin, ids_rutas
from utils import baja_logica, obtener_o_404, solo_activos

router = APIRouter(prefix="/fallas-vehiculo", tags=["Fallas de vehículo"])
CLAVE = "fallas-vehiculo"
NOMBRE = "Falla"


def _consulta_visible(db, usuario):
    q = db.query(FallaVehiculo)
    if es_admin(usuario):
        return q
    conductor = conductor_de(db, usuario) if usuario.rol.nombre == "Conductor" else None
    if usuario.rol.nombre == "Conductor":
        return q.filter(FallaVehiculo.conductor_id == (conductor.id if conductor else -1))
    return q.filter(FallaVehiculo.ruta_id.in_(ids_rutas(db, usuario) or [-1]))


def _obtener(db, usuario, id):
    obj = _consulta_visible(db, usuario).filter(FallaVehiculo.id == id).first()
    if not obj:
        raise HTTPException(404, f"{NOMBRE} no encontrada")
    return obj


def _sincronizar_vehiculo(db, falla):
    """Si la falla se revisa, el vehículo pasa a Mantenimiento;
    cuando se resuelve, vuelve a Disponible."""
    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == falla.vehiculo_id).first()
    if not vehiculo:
        return
    if falla.atencion == "En revisión":
        vehiculo.disponibilidad = "Mantenimiento"
    elif falla.atencion == "Resuelta":
        vehiculo.disponibilidad = "Disponible"


@router.get("/", response_model=list[FallaVehiculoResponse])
def obtener_fallas(
    incluir_inactivos: bool = False,
    db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE)),
):
    q = solo_activos(_consulta_visible(db, usuario), FallaVehiculo, incluir_inactivos)
    return q.order_by(FallaVehiculo.fecha_hora.desc()).all()


@router.get("/{id}", response_model=FallaVehiculoResponse)
def obtener_falla(id: int, db: Session = Depends(get_db), usuario=Depends(permiso(CLAVE))):
    return _obtener(db, usuario, id)


@router.post("/", response_model=FallaVehiculoResponse)
def crear_falla(
    cuerpo: FallaVehiculoCreate, db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "crear")),
):
    ruta = obtener_o_404(db, Ruta, cuerpo.ruta_id, "Ruta")

    if not es_admin(usuario) and ruta.id not in (ids_rutas(db, usuario) or []):
        raise HTTPException(403, "Esa ruta no está a tu cargo")

    # El vehículo y el conductor salen de la ruta: el usuario no los digita.
    nueva = FallaVehiculo(
        ruta_id=ruta.id,
        vehiculo_id=ruta.vehiculo_id,
        conductor_id=ruta.conductor_id,
        tipo=cuerpo.tipo,
        gravedad=cuerpo.gravedad,
        descripcion=cuerpo.descripcion,
        atencion="Reportada",
        fecha_hora=ahora(),
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.put("/{id}", response_model=FallaVehiculoResponse)
def actualizar_falla(
    id: int, cuerpo: FallaVehiculoCreate, db: Session = Depends(get_db),
    usuario=Depends(permiso(CLAVE, "editar")),
):
    falla = _obtener(db, usuario, id)

    # El conductor corrige su reporte; el administrador además lo gestiona.
    falla.tipo = cuerpo.tipo
    falla.gravedad = cuerpo.gravedad
    falla.descripcion = cuerpo.descripcion

    if es_admin(usuario):
        if cuerpo.atencion:
            falla.atencion = cuerpo.atencion
        falla.observacion_admin = cuerpo.observacion_admin
        if cuerpo.estado:
            falla.estado = cuerpo.estado
        _sincronizar_vehiculo(db, falla)

    db.commit()
    db.refresh(falla)
    return falla


@router.delete("/{id}")
def eliminar_falla(
    id: int, db: Session = Depends(get_db), usuario=Depends(permiso(CLAVE, "eliminar"))
):
    return baja_logica(db, _obtener(db, usuario, id), NOMBRE)
