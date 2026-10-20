from datetime import datetime, timezone, timedelta

from sqlalchemy import (
    Column, Integer, String, Boolean, Time, Date, DECIMAL, DateTime,
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base

# Colombia no tiene horario de verano: UTC-5 todo el año.
ZONA_CO = timezone(timedelta(hours=-5))


def ahora():
    """Fecha y hora actual de Colombia (sin zona, lista para guardar)."""
    return datetime.now(ZONA_CO).replace(tzinfo=None)


class Auditoria:
    """Campos que llevan TODAS las tablas: creado, actualizado y estado.

    El borrado es lógico: eliminar un registro = estado 'Inactivo'.
    """
    creado = Column(DateTime, nullable=False, default=ahora)
    actualizado = Column(DateTime, nullable=False, default=ahora, onupdate=ahora)
    estado = Column(String(20), nullable=False, default="Activo")


# ============================================================
# SEGURIDAD: roles, módulos y permisos
# ============================================================

class Rol(Auditoria, Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(String(150))

    usuarios = relationship("Usuario", back_populates="rol")
    permisos = relationship("RolModulo", back_populates="rol")


class Modulo(Auditoria, Base):
    """Pantallas del sistema. `clave` coincide con la ruta de la API."""
    __tablename__ = "modulos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(80), nullable=False)
    clave = Column(String(50), nullable=False, unique=True)
    icono = Column(String(10))
    orden = Column(Integer, nullable=False, default=0)

    permisos = relationship("RolModulo", back_populates="modulo")


class RolModulo(Auditoria, Base):
    """Tabla roles_modulos: qué módulos ve cada rol y qué puede hacer."""
    __tablename__ = "roles_modulos"
    __table_args__ = (
        UniqueConstraint("rol_id", "modulo_id", name="uq_rol_modulo"),
    )

    id = Column(Integer, primary_key=True, index=True)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    modulo_id = Column(Integer, ForeignKey("modulos.id"), nullable=False)
    etiqueta = Column(String(80))  # nombre del menú para ese rol (opcional)
    puede_crear = Column(Boolean, nullable=False, default=False)
    puede_editar = Column(Boolean, nullable=False, default=False)
    puede_eliminar = Column(Boolean, nullable=False, default=False)

    rol = relationship("Rol", back_populates="permisos")
    modulo = relationship("Modulo", back_populates="permisos")

    @property
    def rol_nombre(self):
        return self.rol.nombre if self.rol else None

    @property
    def modulo_nombre(self):
        return self.modulo.nombre if self.modulo else None


# ============================================================
# PERSONAS
# ============================================================

class Usuario(Auditoria, Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    correo = Column(String(100), nullable=False, unique=True)
    telefono = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    rol = relationship("Rol", back_populates="usuarios")

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def rol_nombre(self):
        return self.rol.nombre if self.rol else None


class Acudiente(Auditoria, Base):
    __tablename__ = "acudientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    documento = Column(String(30), nullable=False, unique=True)
    telefono = Column(String(20), nullable=False)
    correo = Column(String(100))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario")
    estudiantes = relationship("Estudiante", back_populates="acudiente")

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def usuario_nombre(self):
        return self.usuario.nombre_completo if self.usuario else None


class Estudiante(Auditoria, Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    documento = Column(String(30), nullable=False, unique=True)
    grado = Column(String(30))
    direccion = Column(String(150))
    acudiente_id = Column(Integer, ForeignKey("acudientes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))  # cuenta de acceso

    acudiente = relationship("Acudiente", back_populates="estudiantes")
    usuario = relationship("Usuario")

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def acudiente_nombre(self):
        return self.acudiente.nombre_completo if self.acudiente else None

    @property
    def usuario_nombre(self):
        return self.usuario.nombre_completo if self.usuario else None


class Conductor(Auditoria, Base):
    __tablename__ = "conductores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    documento = Column(String(30), nullable=False, unique=True)
    licencia = Column(String(50), nullable=False, unique=True)
    telefono = Column(String(20))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))  # cuenta de acceso

    usuario = relationship("Usuario")

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def usuario_nombre(self):
        return self.usuario.nombre_completo if self.usuario else None


# ============================================================
# TRANSPORTE
# ============================================================

class Vehiculo(Auditoria, Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), nullable=False, unique=True)
    marca = Column(String(50))
    modelo = Column(String(50))
    capacidad = Column(Integer, nullable=False)
    # Situación operativa (antes se llamaba "estado"; ahora "estado" es el
    # campo común de baja lógica).
    disponibilidad = Column(String(30), nullable=False, default="Disponible")


class Ruta(Auditoria, Base):
    __tablename__ = "rutas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(200))
    hora_salida = Column(Time, nullable=False)
    hora_llegada = Column(Time)
    conductor_id = Column(Integer, ForeignKey("conductores.id"), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)

    conductor = relationship("Conductor")
    vehiculo = relationship("Vehiculo")

    @property
    def conductor_nombre(self):
        return self.conductor.nombre_completo if self.conductor else None

    @property
    def vehiculo_placa(self):
        return self.vehiculo.placa if self.vehiculo else None


class Paradero(Auditoria, Base):
    __tablename__ = "paraderos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(150), nullable=False)
    referencia = Column(String(200))
    latitud = Column(DECIMAL(10, 7))
    longitud = Column(DECIMAL(10, 7))


class EstudianteRuta(Auditoria, Base):
    __tablename__ = "estudiante_ruta"
    __table_args__ = (
        UniqueConstraint(
            "estudiante_id", "ruta_id", "paradero_id",
            name="uq_estudiante_ruta_asignacion",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    paradero_id = Column(Integer, ForeignKey("paraderos.id"), nullable=False)

    estudiante = relationship("Estudiante")
    ruta = relationship("Ruta")
    paradero = relationship("Paradero")

    @property
    def estudiante_nombre(self):
        return self.estudiante.nombre_completo if self.estudiante else None

    @property
    def ruta_nombre(self):
        return self.ruta.nombre if self.ruta else None

    @property
    def paradero_nombre(self):
        return self.paradero.nombre if self.paradero else None

    @property
    def hora_salida(self):
        return self.ruta.hora_salida if self.ruta else None


class RegistroAbordaje(Auditoria, Base):
    __tablename__ = "registros_abordaje"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    fecha_hora = Column(DateTime, nullable=False, default=ahora)
    tipo = Column(String(20), nullable=False)  # Subida | Bajada

    estudiante = relationship("Estudiante")
    ruta = relationship("Ruta")

    @property
    def estudiante_nombre(self):
        return self.estudiante.nombre_completo if self.estudiante else None

    @property
    def ruta_nombre(self):
        return self.ruta.nombre if self.ruta else None


# ============================================================
# FUNCIONALIDADES NUEVAS: acudiente y conductor
# ============================================================

class Ausencia(Auditoria, Base):
    """El acudiente (o el estudiante) avisa que no tomará la ruta.

    El conductor la ve en su panel y la marca como 'Vista por conductor'.
    """
    __tablename__ = "ausencias"

    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    ruta_id = Column(Integer, ForeignKey("rutas.id"))
    fecha = Column(Date, nullable=False)
    motivo = Column(String(200), nullable=False)
    atencion = Column(String(30), nullable=False, default="Pendiente")
    reportado_por_id = Column(Integer, ForeignKey("usuarios.id"))

    estudiante = relationship("Estudiante")
    ruta = relationship("Ruta")
    reportado_por = relationship("Usuario")

    @property
    def estudiante_nombre(self):
        return self.estudiante.nombre_completo if self.estudiante else None

    @property
    def ruta_nombre(self):
        return self.ruta.nombre if self.ruta else None

    @property
    def reportado_por_nombre(self):
        return self.reportado_por.nombre_completo if self.reportado_por else None


class FallaVehiculo(Auditoria, Base):
    """El conductor reporta una falla; el administrador la gestiona.

    Acudientes y estudiantes ven la alerta de las rutas que usan.
    """
    __tablename__ = "fallas_vehiculo"

    id = Column(Integer, primary_key=True, index=True)
    ruta_id = Column(Integer, ForeignKey("rutas.id"), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    conductor_id = Column(Integer, ForeignKey("conductores.id"), nullable=False)
    tipo = Column(String(30), nullable=False)
    gravedad = Column(String(20), nullable=False, default="Media")
    descripcion = Column(String(300), nullable=False)
    atencion = Column(String(30), nullable=False, default="Reportada")
    observacion_admin = Column(String(300))
    fecha_hora = Column(DateTime, nullable=False, default=ahora)

    ruta = relationship("Ruta")
    vehiculo = relationship("Vehiculo")
    conductor = relationship("Conductor")

    @property
    def ruta_nombre(self):
        return self.ruta.nombre if self.ruta else None

    @property
    def vehiculo_placa(self):
        return self.vehiculo.placa if self.vehiculo else None

    @property
    def conductor_nombre(self):
        return self.conductor.nombre_completo if self.conductor else None
