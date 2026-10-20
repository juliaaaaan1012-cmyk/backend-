from datetime import time, date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict

Estado = Literal["Activo", "Inactivo"]


class Opcional(BaseModel):
    """Permite reactivar un registro enviando estado='Activo'."""
    estado: Optional[Estado] = None


class Salida(BaseModel):
    """Campos comunes que devuelve cada tabla."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    creado: datetime
    actualizado: datetime
    estado: str


# ---------------- AUTENTICACIÓN ----------------

class LoginRequest(BaseModel):
    correo: str
    password: str
    rol_id: int


class ModuloMenu(BaseModel):
    clave: str
    nombre: str
    icono: Optional[str] = None
    orden: int
    puede_crear: bool
    puede_editar: bool
    puede_eliminar: bool


class UsuarioSesion(BaseModel):
    id: int
    nombre_completo: str
    correo: str
    rol: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioSesion
    modulos: list[ModuloMenu]


# ---------------- ROLES ----------------

class RolCreate(Opcional):
    nombre: str
    descripcion: Optional[str] = None


class RolResponse(Salida):
    nombre: str
    descripcion: Optional[str] = None


# ---------------- MÓDULOS ----------------

class ModuloCreate(Opcional):
    nombre: str
    clave: str
    icono: Optional[str] = None
    orden: int = 0


class ModuloResponse(Salida):
    nombre: str
    clave: str
    icono: Optional[str] = None
    orden: int


# ---------------- ROLES_MODULOS ----------------

class RolModuloCreate(Opcional):
    rol_id: int
    modulo_id: int
    etiqueta: Optional[str] = None
    puede_crear: bool = False
    puede_editar: bool = False
    puede_eliminar: bool = False


class RolModuloResponse(Salida):
    rol_id: int
    modulo_id: int
    rol_nombre: Optional[str] = None
    modulo_nombre: Optional[str] = None
    etiqueta: Optional[str] = None
    puede_crear: bool
    puede_editar: bool
    puede_eliminar: bool


# ---------------- USUARIOS ----------------

class UsuarioCreate(Opcional):
    nombre: str
    apellido: str
    correo: str
    telefono: Optional[str] = None
    rol_id: int
    password: str


class UsuarioUpdate(Opcional):
    nombre: str
    apellido: str
    correo: str
    telefono: Optional[str] = None
    rol_id: int
    password: Optional[str] = None  # vacío = no cambiar


class UsuarioResponse(Salida):
    nombre: str
    apellido: str
    nombre_completo: str
    correo: str
    telefono: Optional[str] = None
    rol_id: int
    rol_nombre: Optional[str] = None


# ---------------- ACUDIENTES ----------------

class AcudienteCreate(Opcional):
    nombre: str
    apellido: str
    documento: str
    telefono: str
    correo: Optional[str] = None
    usuario_id: int


class AcudienteResponse(Salida):
    nombre: str
    apellido: str
    nombre_completo: str
    documento: str
    telefono: str
    correo: Optional[str] = None
    usuario_id: int
    usuario_nombre: Optional[str] = None


# ---------------- ESTUDIANTES ----------------

class EstudianteCreate(Opcional):
    nombre: str
    apellido: str
    documento: str
    grado: Optional[str] = None
    direccion: Optional[str] = None
    acudiente_id: Optional[int] = None   # el acudiente lo deja vacío
    usuario_id: Optional[int] = None


class EstudianteResponse(Salida):
    nombre: str
    apellido: str
    nombre_completo: str
    documento: str
    grado: Optional[str] = None
    direccion: Optional[str] = None
    acudiente_id: int
    acudiente_nombre: Optional[str] = None
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None


# ---------------- CONDUCTORES ----------------

class ConductorCreate(Opcional):
    nombre: str
    apellido: str
    documento: str
    licencia: str
    telefono: Optional[str] = None
    usuario_id: Optional[int] = None


class ConductorResponse(Salida):
    nombre: str
    apellido: str
    nombre_completo: str
    documento: str
    licencia: str
    telefono: Optional[str] = None
    usuario_id: Optional[int] = None
    usuario_nombre: Optional[str] = None


# ---------------- VEHÍCULOS ----------------

class VehiculoCreate(Opcional):
    placa: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    capacidad: int
    disponibilidad: str = "Disponible"


class VehiculoResponse(Salida):
    placa: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    capacidad: int
    disponibilidad: str


# ---------------- RUTAS ----------------

class RutaCreate(Opcional):
    nombre: str
    descripcion: Optional[str] = None
    hora_salida: time
    hora_llegada: Optional[time] = None
    conductor_id: int
    vehiculo_id: int


class RutaResponse(Salida):
    nombre: str
    descripcion: Optional[str] = None
    hora_salida: time
    hora_llegada: Optional[time] = None
    conductor_id: int
    vehiculo_id: int
    conductor_nombre: Optional[str] = None
    vehiculo_placa: Optional[str] = None


# ---------------- PARADEROS ----------------

class ParaderoCreate(Opcional):
    nombre: str
    direccion: str
    referencia: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class ParaderoResponse(Salida):
    nombre: str
    direccion: str
    referencia: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


# ---------------- ESTUDIANTE - RUTA ----------------

class EstudianteRutaCreate(Opcional):
    estudiante_id: int
    ruta_id: int
    paradero_id: int


class EstudianteRutaResponse(Salida):
    estudiante_id: int
    ruta_id: int
    paradero_id: int
    estudiante_nombre: Optional[str] = None
    ruta_nombre: Optional[str] = None
    paradero_nombre: Optional[str] = None
    hora_salida: Optional[time] = None


# ---------------- REGISTROS DE ABORDAJE ----------------

class RegistroAbordajeCreate(Opcional):
    estudiante_id: int
    ruta_id: int
    tipo: Literal["Subida", "Bajada"]


class RegistroAbordajeResponse(Salida):
    estudiante_id: int
    ruta_id: int
    tipo: str
    fecha_hora: datetime
    estudiante_nombre: Optional[str] = None
    ruta_nombre: Optional[str] = None


# ---------------- AUSENCIAS ----------------

class AusenciaCreate(Opcional):
    estudiante_id: Optional[int] = None   # el estudiante lo deja vacío
    fecha: date
    motivo: str
    atencion: Optional[Literal["Pendiente", "Vista por conductor"]] = None


class AusenciaResponse(Salida):
    estudiante_id: int
    ruta_id: Optional[int] = None
    fecha: date
    motivo: str
    atencion: str
    estudiante_nombre: Optional[str] = None
    ruta_nombre: Optional[str] = None
    reportado_por_nombre: Optional[str] = None


# ---------------- FALLAS DE VEHÍCULO ----------------

class FallaVehiculoCreate(Opcional):
    ruta_id: int
    tipo: Literal["Mecánica", "Eléctrica", "Llantas", "Frenos", "Accidente", "Otra"]
    gravedad: Literal["Baja", "Media", "Alta"] = "Media"
    descripcion: str
    atencion: Optional[Literal["Reportada", "En revisión", "Resuelta"]] = None
    observacion_admin: Optional[str] = None


class FallaVehiculoResponse(Salida):
    ruta_id: int
    vehiculo_id: int
    conductor_id: int
    tipo: str
    gravedad: str
    descripcion: str
    atencion: str
    observacion_admin: Optional[str] = None
    fecha_hora: datetime
    ruta_nombre: Optional[str] = None
    vehiculo_placa: Optional[str] = None
    conductor_nombre: Optional[str] = None
