"""Qué datos puede ver cada rol.

- Administrador: todo.
- Conductor: sus rutas y los estudiantes de esas rutas.
- Acudiente: sus estudiantes y las rutas que ellos usan.
- Estudiante: solo sus propios datos y su ruta.
"""
from sqlalchemy import false, select
from sqlalchemy.orm import Session

from models import (
    Acudiente, Conductor, Estudiante, EstudianteRuta, Ruta, Usuario,
)


def es_admin(usuario: Usuario) -> bool:
    return usuario.rol.nombre == "Administrador"


def conductor_de(db: Session, usuario: Usuario):
    return db.query(Conductor).filter(
        Conductor.usuario_id == usuario.id, Conductor.estado == "Activo"
    ).first()


def acudiente_de(db: Session, usuario: Usuario):
    return db.query(Acudiente).filter(
        Acudiente.usuario_id == usuario.id, Acudiente.estado == "Activo"
    ).first()


def estudiante_de(db: Session, usuario: Usuario):
    return db.query(Estudiante).filter(
        Estudiante.usuario_id == usuario.id, Estudiante.estado == "Activo"
    ).first()


def ids_rutas(db: Session, usuario: Usuario):
    """None = todas las rutas. Lista = solo esas."""
    rol = usuario.rol.nombre
    if rol == "Administrador":
        return None
    if rol == "Conductor":
        conductor = conductor_de(db, usuario)
        if not conductor:
            return []
        return [
            r.id for r in db.query(Ruta.id).filter(
                Ruta.conductor_id == conductor.id, Ruta.estado == "Activo"
            )
        ]
    ids_est = [e.id for e in consulta_estudiantes(db, usuario).with_entities(Estudiante.id)]
    if not ids_est:
        return []
    filas = db.query(EstudianteRuta.ruta_id).filter(
        EstudianteRuta.estudiante_id.in_(ids_est),
        EstudianteRuta.estado == "Activo",
    ).distinct()
    return [f[0] for f in filas]


def consulta_estudiantes(db: Session, usuario: Usuario):
    """Consulta de estudiantes (activos o no) que el usuario puede ver."""
    q = db.query(Estudiante)
    rol = usuario.rol.nombre
    if rol == "Administrador":
        return q
    if rol == "Acudiente":
        return q.join(Acudiente, Estudiante.acudiente_id == Acudiente.id).filter(
            Acudiente.usuario_id == usuario.id
        )
    if rol == "Estudiante":
        return q.filter(Estudiante.usuario_id == usuario.id)
    if rol == "Conductor":
        rutas = ids_rutas(db, usuario)
        sub = select(EstudianteRuta.estudiante_id).where(
            EstudianteRuta.ruta_id.in_(rutas or [-1]),
            EstudianteRuta.estado == "Activo",
        )
        return q.filter(Estudiante.id.in_(sub))
    return q.filter(false())


def ids_estudiantes(db: Session, usuario: Usuario):
    """None = todos. Lista = solo esos."""
    if es_admin(usuario):
        return None
    return [e.id for e in consulta_estudiantes(db, usuario).with_entities(Estudiante.id)]
