"""Carga los datos iniciales: roles, módulos, permisos (roles_modulos)
y datos de ejemplo de Cartagena.

Uso:
    python seed.py            # solo carga si la base está vacía
    python seed.py --reset    # BORRA las tablas del proyecto y las recrea
    python seed.py --reset --yes   # igual, sin pedir confirmación

Funciona igual en la base local y en la de la nube: usa DATABASE_URL del .env.
"""
import random
import sys
import unicodedata
from datetime import timedelta, time

from auth import hash_password
from database import Base, SessionLocal, engine
import models as m

CLAVE_ADMIN = "Admin2026*"
CLAVE_GENERAL = "Ruta2026*"


def sin_tildes(texto):
    base = unicodedata.normalize("NFD", texto)
    return "".join(c for c in base if unicodedata.category(c) != "Mn").lower()


rnd = random.Random(2026)

# ------------------------------------------------------------
# Catálogos de apoyo
# ------------------------------------------------------------
NOMBRES_H = ["Carlos", "Luis", "Andrés", "Jorge", "Miguel", "Javier", "Hernán", "Edwin", "Rafael", "Fabián", "Julián", "Óscar"]
NOMBRES_M = ["María", "Luz", "Diana", "Paola", "Sandra", "Marta", "Yaneth", "Liliana", "Claudia", "Ángela", "Katherine", "Rosa"]
APELLIDOS = [
    "Pérez", "Rodríguez", "Martínez", "Herrera", "Castro", "Ortega", "Barrios",
    "Cabarcas", "Montes", "Salcedo", "Arrieta", "Padilla", "Villalba", "Caraballo",
    "Mendoza", "Hernández", "Gómez", "Torres", "Romero", "Julio", "Pacheco",
    "Ramos", "Jiménez", "Lozano", "Cueto", "Tapia",
]
NOMBRES_EST = [
    ("Samuel", "H"), ("Valentina", "M"), ("Mateo", "H"), ("Isabella", "M"),
    ("Santiago", "H"), ("Sofía", "M"), ("Daniel", "H"), ("Mariana", "M"),
    ("Sebastián", "H"), ("Camila", "M"), ("Juan David", "H"), ("Laura", "M"),
    ("Nicolás", "H"), ("Daniela", "M"), ("Emmanuel", "H"), ("Gabriela", "M"),
    ("Tomás", "H"), ("Salomé", "M"), ("Alejandro", "H"), ("Juliana", "M"),
]
BARRIOS = [
    "Bocagrande", "Castillogrande", "El Laguito", "Getsemaní", "Centro", "Manga",
    "Manga", "Crespo", "Marbella", "Torices", "Pie de la Popa", "Los Caracoles",
    "Ternera", "Albornoz", "El Bosque", "Zaragocilla", "Cabrero", "El Recreo",
    "Olaya Herrera", "Turbaco",
]
GRADOS = ["6°", "7°", "8°", "9°", "10°", "11°"]

PARADEROS = [
    ("Parque de Bocagrande", "Av. San Martín con Calle 5", "Frente al parque", 10.4012, -75.5545),
    ("Castillogrande - Club de Pesca", "Cra 1 #5-20 Castillogrande", "Entrada principal", 10.3935, -75.5510),
    ("El Laguito - Hotel Hilton", "Av. Almirante Brión #1-10", "Cruce semafórico", 10.4065, -75.5580),
    ("Parque Flanagan", "Calle del Guerrero, Getsemaní", "Esquina del parque", 10.4245, -75.5475),
    ("Plaza de la Serrezuela", "Av. Venezuela, Centro", "Frente a la plaza", 10.4235, -75.5505),
    ("Parque Apolo", "Calle 30 #19-50, Manga", "Costado norte", 10.4130, -75.5370),
    ("Manga - Iglesia San Judas", "Cra 22 #24-10, Manga", "Frente a la iglesia", 10.4110, -75.5400),
    ("Crespo - Aeropuerto", "Av. Pedro de Heredia #70-15", "Frente a la terminal aérea", 10.4435, -75.5130),
    ("Marbella - Parque", "Calle 70 #3-25, Marbella", "Junto al parque", 10.4380, -75.5265),
    ("Torices - Iglesia", "Cra 14 #45-30, Torices", "Frente a la iglesia", 10.4200, -75.5260),
    ("Pie de la Popa - Convento", "Cra 20 #31-10", "Subida al convento", 10.4175, -75.5340),
    ("Los Caracoles - Tienda Don Pedro", "Calle 31 #85-40", "Esquina de la tienda", 10.4020, -75.4890),
    ("Ternera - Parque Principal", "Av. Pedro Romero, Ternera", "Costado del parque", 10.3830, -75.4660),
    ("Albornoz - Centro Comercial", "Transversal 54 #8-10", "Entrada del centro comercial", 10.3750, -75.5010),
    ("Bosque - Éxito", "Diag. 21 #52-65, El Bosque", "Entrada principal", 10.3960, -75.4960),
    ("Zaragocilla - Hospital Universitario", "Cra 52 #29-30", "Puerta de urgencias", 10.4050, -75.5080),
    ("Cabrero - Cuartel Naval", "Av. del Cabrero #35-10", "Frente a la glorieta", 10.4320, -75.5410),
    ("El Recreo - Parque", "Calle 28 #75-12, El Recreo", "Junto a la cancha", 10.3920, -75.4790),
    ("Olaya Herrera - Parque Central", "Calle 29 #56-20", "Parque principal", 10.4000, -75.5000),
    ("Turbaco - Peaje", "Troncal de Occidente, Turbaco", "Junto al peaje", 10.3300, -75.4170),
]

RUTAS = [
    ("Ruta 1 Bocagrande - Castillogrande", "Recorre Bocagrande, El Laguito y Castillogrande hasta el colegio."),
    ("Ruta 2 Centro - Getsemaní", "Parte del Centro Histórico y recoge en Getsemaní."),
    ("Ruta 3 Manga - Pie de la Popa", "Cubre Manga y los barrios al pie del cerro de La Popa."),
    ("Ruta 4 Crespo - Marbella", "Zona norte cercana al aeropuerto y al mar."),
    ("Ruta 5 Torices - Cabrero", "Barrios de la zona nororiental."),
    ("Ruta 6 Los Caracoles - Ternera", "Sector oriental y sur de la ciudad."),
    ("Ruta 7 Albornoz - Zaragocilla", "Zona industrial y barrios cercanos al hospital."),
    ("Ruta 8 El Bosque - Olaya", "Barrios del suroriente."),
    ("Ruta 9 El Recreo", "Recorrido corto por El Recreo y alrededores."),
    ("Ruta 10 Turbaco", "Ruta intermunicipal desde Turbaco."),
    ("Ruta 11 Mixta Norte", "Ruta de apoyo para la zona norte."),
    ("Ruta 12 Mixta Sur", "Ruta de apoyo para la zona sur."),
]

VEHICULOS = [
    ("UXH412", "Chevrolet", "NPR 2021", 32), ("UYB209", "Hino", "FC 2020", 36),
    ("TZK581", "Mercedes-Benz", "OF 1721 2019", 40), ("UXM334", "Foton", "BJ6 2022", 28),
    ("UXP778", "Chevrolet", "NKR 2022", 24), ("TZN145", "Kia", "Combi 2018", 19),
    ("UYC650", "Hino", "FC 2023", 36), ("UXS903", "Mercedes-Benz", "OH 1621 2020", 40),
    ("UYD317", "Foton", "Toano 2021", 19), ("UXT256", "Chevrolet", "NPR 2019", 32),
    ("UYE842", "Hyundai", "County 2022", 25), ("TZP090", "Kia", "Combi 2020", 19),
]

FALLAS = [
    ("Frenos", "Alta", "Ruido metálico al frenar y el pedal se siente blando.", "En revisión"),
    ("Llantas", "Media", "Llanta trasera derecha con baja presión y desgaste irregular.", "Reportada"),
    ("Eléctrica", "Baja", "Luz interior del pasillo no enciende.", "Resuelta"),
    ("Mecánica", "Alta", "Recalentamiento del motor en el trayecto de la mañana.", "En revisión"),
    ("Otra", "Baja", "El aire acondicionado no enfría lo suficiente.", "Reportada"),
    ("Llantas", "Media", "Se pinchó una llanta delantera; se cambió por la de repuesto.", "Resuelta"),
    ("Eléctrica", "Media", "Falla intermitente de las luces direccionales.", "Reportada"),
    ("Mecánica", "Media", "Ruido en la caja de cambios al subir a segunda.", "Reportada"),
    ("Accidente", "Media", "Raspón lateral leve en parqueadero, sin heridos.", "Resuelta"),
    ("Frenos", "Baja", "Pastillas delanteras cerca del límite de desgaste.", "Reportada"),
]

MOTIVOS = [
    "Cita médica programada", "Viaje familiar", "Gripa con recomendación de reposo",
    "Cita odontológica", "Calamidad doméstica", "Examen de inglés en otra sede",
    "Controles médicos de rutina", "Será recogido por un familiar",
    "Trámite de documentos", "Malestar estomacal",
]

# ------------------------------------------------------------
# Módulos y permisos (roles_modulos)
# ------------------------------------------------------------
# (clave, nombre, icono, orden)
MODULOS = [
    ("roles", "Roles", "🛡️", 1),
    ("modulos", "Módulos", "🧩", 2),
    ("roles-modulos", "Permisos por rol", "🔑", 3),
    ("usuarios", "Usuarios", "👤", 4),
    ("acudientes", "Acudientes", "👪", 5),
    ("estudiantes", "Estudiantes", "🎒", 6),
    ("conductores", "Conductores", "🧑‍✈️", 7),
    ("vehiculos", "Vehículos", "🚌", 8),
    ("rutas", "Rutas", "🗺️", 9),
    ("paraderos", "Paraderos", "📍", 10),
    ("estudiante-ruta", "Asignaciones", "🔗", 11),
    ("registros-abordaje", "Abordajes", "✅", 12),
    ("ausencias", "Ausencias", "📅", 13),
    ("fallas-vehiculo", "Fallas de vehículo", "🛠️", 14),
]

# rol -> lista de (clave, etiqueta o None, crear, editar, eliminar)
T, F = True, False
PERMISOS = {
    "Administrador": [(c, None, T, T, T) for c, *_ in MODULOS],
    "Conductor": [
        ("rutas", "Mis rutas", F, F, F),
        ("estudiantes", "Estudiantes de mi ruta", F, F, F),
        ("registros-abordaje", "Registrar abordajes", T, T, T),
        ("fallas-vehiculo", "Fallas de mi vehículo", T, T, T),
        ("ausencias", "Ausencias reportadas", F, T, F),
    ],
    "Acudiente": [
        ("estudiantes", "Mis estudiantes", T, T, T),
        ("rutas", "Rutas de mis hijos", F, F, F),
        ("estudiante-ruta", "Paraderos y horarios", F, F, F),
        ("registros-abordaje", "Abordajes de mis hijos", F, F, F),
        ("ausencias", "Reportar ausencias", T, T, T),
        ("fallas-vehiculo", "Alertas de vehículos", F, F, F),
    ],
    "Estudiante": [
        ("estudiantes", "Mis datos", F, T, F),
        ("estudiante-ruta", "Mi ruta", F, F, F),
        ("registros-abordaje", "Mis abordajes", F, F, F),
        ("ausencias", "Mis ausencias", T, T, T),
        ("fallas-vehiculo", "Alertas de mi ruta", F, F, F),
    ],
}

DESCRIPCION_ROLES = {
    "Administrador": "Gestiona toda la operación del transporte escolar.",
    "Conductor": "Registra abordajes y reporta fallas de su vehículo.",
    "Acudiente": "Consulta el transporte de sus hijos y reporta ausencias.",
    "Estudiante": "Consulta su ruta, abordajes y alertas.",
}


def telefono():
    return f"3{rnd.randint(0, 2)}{rnd.randint(0, 9)}{rnd.randint(1000000, 9999999)}"


def documento(prefijo=""):
    return f"{prefijo}{rnd.randint(10000000, 99999999)}"


def main():
    reset = "--reset" in sys.argv
    if reset:
        if "--yes" not in sys.argv:
            print("ATENCIÓN: se borrarán las tablas del proyecto y sus datos.")
            if input("Escribe SI para continuar: ").strip() != "SI":
                print("Cancelado.")
                return
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(m.Rol).count() > 0:
            print("La base ya tiene datos. Usa --reset si quieres recargarla.")
            return

        # ---- roles ----
        roles = {}
        for nombre, desc in DESCRIPCION_ROLES.items():
            roles[nombre] = m.Rol(nombre=nombre, descripcion=desc)
            db.add(roles[nombre])
        db.flush()

        # ---- módulos ----
        modulos = {}
        for clave, nombre, icono, orden in MODULOS:
            modulos[clave] = m.Modulo(nombre=nombre, clave=clave, icono=icono, orden=orden)
            db.add(modulos[clave])
        db.flush()

        # ---- roles_modulos ----
        for rol, lista in PERMISOS.items():
            for clave, etiqueta, crear, editar, eliminar in lista:
                db.add(m.RolModulo(
                    rol_id=roles[rol].id, modulo_id=modulos[clave].id,
                    etiqueta=etiqueta, puede_crear=crear,
                    puede_editar=editar, puede_eliminar=eliminar,
                ))

        # ---- usuarios ----
        hash_admin = hash_password(CLAVE_ADMIN)
        hash_general = hash_password(CLAVE_GENERAL)  # se reutiliza el hash

        def usuario(nombre, apellido, correo, rol, clave_hash):
            u = m.Usuario(
                nombre=nombre, apellido=apellido, correo=correo,
                telefono=telefono(), rol_id=roles[rol].id,
                password_hash=clave_hash,
            )
            db.add(u)
            db.flush()
            return u

        usuario("Administrador", "General", "admin@rutaescolar.co", "Administrador", hash_admin)

        # ---- conductores ----
        apellidos = APELLIDOS[:]
        rnd.shuffle(apellidos)
        conductores = []
        for i in range(12):
            nombre = NOMBRES_H[i % len(NOMBRES_H)]
            ape = f"{apellidos[i]} {apellidos[(i + 7) % len(apellidos)]}"
            correo = f"{sin_tildes(nombre)}.{sin_tildes(apellidos[i])}@rutaescolar.co"
            u = usuario(nombre, ape, correo, "Conductor", hash_general)
            c = m.Conductor(
                nombre=nombre, apellido=ape, documento=documento("1"),
                licencia=f"C2-{rnd.randint(100000, 999999)}",
                telefono=u.telefono, usuario_id=u.id,
            )
            db.add(c)
            conductores.append(c)
        db.flush()

        # ---- vehículos ----
        vehiculos = []
        for placa, marca, modelo, capacidad in VEHICULOS:
            v = m.Vehiculo(placa=placa, marca=marca, modelo=modelo, capacidad=capacidad)
            db.add(v)
            vehiculos.append(v)
        db.flush()

        # ---- rutas ----
        rutas = []
        for i, (nombre, desc) in enumerate(RUTAS):
            salida = time(5, 40 + (i % 4) * 5)
            llegada = time(6, 45 + (i % 3) * 5)
            r = m.Ruta(
                nombre=nombre, descripcion=desc,
                hora_salida=salida, hora_llegada=llegada,
                conductor_id=conductores[i].id, vehiculo_id=vehiculos[i].id,
            )
            db.add(r)
            rutas.append(r)
        db.flush()

        # ---- paraderos ----
        paraderos = []
        for nombre, direccion, ref, lat, lon in PARADEROS:
            p = m.Paradero(nombre=nombre, direccion=direccion, referencia=ref, latitud=lat, longitud=lon)
            db.add(p)
            paraderos.append(p)
        db.flush()

        # ---- acudientes y estudiantes ----
        acudientes, estudiantes = [], []
        for i, (nombre_est, sexo) in enumerate(NOMBRES_EST):
            ap1, ap2 = APELLIDOS[(i * 3) % len(APELLIDOS)], APELLIDOS[(i * 5 + 2) % len(APELLIDOS)]
            nombre_ac = (NOMBRES_M if i % 2 == 0 else NOMBRES_H)[i % 12]
            correo_ac = f"{sin_tildes(nombre_ac)}.{sin_tildes(ap1)}{i + 1}@gmail.com"
            u_ac = usuario(nombre_ac, f"{ap1} {ap2}", correo_ac, "Acudiente", hash_general)
            ac = m.Acudiente(
                nombre=nombre_ac, apellido=f"{ap1} {ap2}", documento=documento("1"),
                telefono=u_ac.telefono, correo=correo_ac, usuario_id=u_ac.id,
            )
            db.add(ac)
            db.flush()
            acudientes.append(ac)

            correo_es = f"{sin_tildes(nombre_est.split()[0])}.{sin_tildes(ap1)}{i + 1}@estudiantes.rutaescolar.co"
            u_es = usuario(nombre_est, f"{ap1} {APELLIDOS[(i * 7 + 4) % len(APELLIDOS)]}", correo_es, "Estudiante", hash_general)
            barrio = BARRIOS[i % len(BARRIOS)]
            es = m.Estudiante(
                nombre=nombre_est, apellido=u_es.apellido, documento=documento("11"),
                grado=GRADOS[i % len(GRADOS)],
                direccion=f"Barrio {barrio}, Cartagena",
                acudiente_id=ac.id, usuario_id=u_es.id,
            )
            db.add(es)
            estudiantes.append(es)
        db.flush()

        # ---- asignaciones estudiante-ruta ----
        asignaciones = {}
        for i, es in enumerate(estudiantes):
            ruta = rutas[i % 10]
            db.add(m.EstudianteRuta(
                estudiante_id=es.id, ruta_id=ruta.id, paradero_id=paraderos[i % len(paraderos)].id,
            ))
            asignaciones[es.id] = ruta
        db.flush()

        # ---- abordajes (hoy y ayer) ----
        hoy = m.ahora().replace(hour=0, minute=0, second=0, microsecond=0)
        for i, es in enumerate(estudiantes):
            ruta = asignaciones[es.id]
            db.add(m.RegistroAbordaje(
                estudiante_id=es.id, ruta_id=ruta.id, tipo="Subida",
                fecha_hora=hoy + timedelta(hours=6, minutes=10 + i),
            ))
        for i, es in enumerate(estudiantes[:10]):
            ruta = asignaciones[es.id]
            db.add(m.RegistroAbordaje(
                estudiante_id=es.id, ruta_id=ruta.id, tipo="Bajada",
                fecha_hora=hoy - timedelta(days=1) + timedelta(hours=13, minutes=5 + i * 2),
            ))

        # ---- ausencias ----
        for i in range(10):
            es = estudiantes[i * 2 % len(estudiantes)]
            db.add(m.Ausencia(
                estudiante_id=es.id, ruta_id=asignaciones[es.id].id,
                fecha=(hoy + timedelta(days=1 + i % 4)).date(),
                motivo=MOTIVOS[i], atencion="Vista por conductor" if i % 3 == 0 else "Pendiente",
                reportado_por_id=es.acudiente.usuario_id,
            ))

        # ---- fallas de vehículo ----
        for i, (tipo, gravedad, desc, atencion) in enumerate(FALLAS):
            ruta = rutas[i]
            db.add(m.FallaVehiculo(
                ruta_id=ruta.id, vehiculo_id=ruta.vehiculo_id, conductor_id=ruta.conductor_id,
                tipo=tipo, gravedad=gravedad, descripcion=desc, atencion=atencion,
                observacion_admin="Se programó revisión en taller." if atencion != "Reportada" else None,
                fecha_hora=hoy - timedelta(days=i % 5, hours=-7),
            ))
            if atencion == "En revisión":
                vehiculos[i].disponibilidad = "Mantenimiento"

        db.commit()

        print("\nDatos cargados correctamente.\n")
        print("Cuentas de prueba (elige también el rol en el login):")
        print(f"  Administrador: admin@rutaescolar.co / {CLAVE_ADMIN}")
        print(f"  Conductor:     {conductores[0].usuario.correo} / {CLAVE_GENERAL}")
        print(f"  Acudiente:     {acudientes[0].correo} / {CLAVE_GENERAL}")
        print(f"  Estudiante:    {estudiantes[0].usuario.correo} / {CLAVE_GENERAL}")
        print("  (todos los conductores, acudientes y estudiantes usan la misma clave)")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
