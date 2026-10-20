from fastapi import HTTPException


def obtener_o_404(db, modelo, id_, nombre="Registro"):
    obj = db.query(modelo).filter(modelo.id == id_).first()
    if not obj:
        raise HTTPException(404, f"{nombre} no encontrado")
    return obj


def datos(esquema, excluir=()):
    """Diccionario listo para crear el modelo (sin estado vacío)."""
    d = esquema.model_dump()
    if d.get("estado") is None:
        d.pop("estado", None)
    for campo in excluir:
        d.pop(campo, None)
    return d


def aplicar(obj, valores: dict, permitidos=None):
    """Copia valores al objeto; `permitidos` limita qué campos se tocan."""
    for campo, valor in valores.items():
        if campo == "estado" and valor is None:
            continue
        if permitidos is not None and campo not in permitidos:
            continue
        setattr(obj, campo, valor)


def baja_logica(db, obj, nombre="Registro"):
    """Eliminar = cambiar el estado a 'Inactivo' (no se borra la fila)."""
    obj.estado = "Inactivo"
    db.commit()
    return {"mensaje": f"{nombre} eliminado correctamente (estado Inactivo)"}


def solo_activos(consulta, modelo, incluir_inactivos: bool):
    if not incluir_inactivos:
        consulta = consulta.filter(modelo.estado == "Activo")
    return consulta
