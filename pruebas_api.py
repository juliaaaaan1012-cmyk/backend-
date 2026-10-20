"""Prueba automática de la API (login, permisos y los flujos entre roles).
Uso: python seed.py --reset --yes   y luego   python pruebas_api.py
(usa la base indicada en DATABASE_URL; conviene una base LOCAL de pruebas)."""
from fastapi.testclient import TestClient
from main import app
c = TestClient(app)

def login(correo, pw, rol):
    roles = {r["nombre"]: r["id"] for r in c.get("/auth/roles").json()}
    r = c.post("/auth/login", json={"correo": correo, "password": pw, "rol_id": roles[rol]})
    assert r.status_code == 200, (r.status_code, r.text)
    j = r.json()
    return {"Authorization": "Bearer " + j["access_token"]}, j

def ok(cond, msg):
    print(("OK  " if cond else "FAIL"), msg)
    assert cond, msg

# --- login
r = c.post("/auth/login", json={"correo":"admin@rutaescolar.co","password":"mala","rol_id":1}); ok(r.status_code==401, "login clave mala 401")
roles = {r["nombre"]: r["id"] for r in c.get("/auth/roles").json()}
r = c.post("/auth/login", json={"correo":"admin@rutaescolar.co","password":"Admin2026*","rol_id":roles["Conductor"]}); ok(r.status_code==403, "login con rol equivocado 403")
H_adm, j = login("admin@rutaescolar.co","Admin2026*","Administrador"); ok(len(j["modulos"])==14, "admin 14 módulos")
H_con, j = login("carlos.villalba@rutaescolar.co","Ruta2026*","Conductor"); print("  conductor módulos:", [m["nombre"] for m in j["modulos"]])
H_acu, j = login("maria.perez1@gmail.com","Ruta2026*","Acudiente"); print("  acudiente módulos:", [m["nombre"] for m in j["modulos"]])
H_est, j = login("samuel.perez1@estudiantes.rutaescolar.co","Ruta2026*","Estudiante"); print("  estudiante módulos:", [m["nombre"] for m in j["modulos"]])

# --- conteos admin
for p, minimo in [("usuarios",50),("acudientes",20),("estudiantes",20),("conductores",12),("vehiculos",12),("rutas",12),("paraderos",20),("estudiante-ruta",20),("registros-abordaje",30),("ausencias",10),("fallas-vehiculo",10),("roles",4),("modulos",14),("roles-modulos",20)]:
    n = len(c.get(f"/{p}/", headers=H_adm).json()); ok(n>=minimo, f"admin {p}: {n}")

# --- sin token / permisos
ok(c.get("/estudiantes/").status_code==401, "sin token 401")
ok(c.get("/usuarios/", headers=H_con).status_code==403, "conductor no ve usuarios 403")
ok(c.post("/rutas/", headers=H_acu, json={}).status_code==403, "acudiente no crea rutas 403")

# --- alcance
rutas_con = c.get("/rutas/", headers=H_con).json(); ok(len(rutas_con)==1, f"conductor ve su ruta: {[r['nombre'] for r in rutas_con]}")
est_acu = c.get("/estudiantes/", headers=H_acu).json(); ok(len(est_acu)==1, "acudiente ve 1 hijo: "+est_acu[0]["nombre_completo"])
est_est = c.get("/estudiantes/", headers=H_est).json(); ok(len(est_est)==1, "estudiante se ve a sí mismo")

# --- FLUJO CRUZADO 1: conductor registra abordaje -> acudiente y estudiante lo ven
ruta_id = rutas_con[0]["id"]
estu_con = c.get("/estudiantes/", headers=H_con).json(); print("  estudiantes de la ruta:", [e["nombre_completo"] for e in estu_con])
samuel = est_est[0]["id"]
n_antes = len(c.get("/registros-abordaje/", headers=H_acu).json())
r = c.post("/registros-abordaje/", headers=H_con, json={"estudiante_id": samuel, "ruta_id": ruta_id, "tipo":"Bajada"}); ok(r.status_code==200, "conductor registra abordaje")
ab_id = r.json()["id"]
ok(len(c.get("/registros-abordaje/", headers=H_acu).json())==n_antes+1, "acudiente ve el nuevo abordaje")
ok(len(c.get("/registros-abordaje/", headers=H_est).json())==n_antes+1, "estudiante ve el nuevo abordaje")
r = c.post("/registros-abordaje/", headers=H_con, json={"estudiante_id": 9999, "ruta_id": ruta_id, "tipo":"Subida"}); ok(r.status_code==400, "abordaje a estudiante no asignado 400")

# --- FLUJO 2: acudiente reporta ausencia -> conductor la ve y la confirma
r = c.post("/ausencias/", headers=H_acu, json={"estudiante_id": samuel, "fecha":"2026-10-22", "motivo":"Cita médica"}); ok(r.status_code==200, "acudiente crea ausencia")
aus = r.json(); ok(aus["ruta_nombre"] is not None and aus["atencion"]=="Pendiente", "ausencia con ruta derivada y Pendiente")
visibles = [a for a in c.get("/ausencias/", headers=H_con).json() if a["id"]==aus["id"]]; ok(len(visibles)==1, "conductor ve la ausencia")
r = c.put(f"/ausencias/{aus['id']}", headers=H_con, json={"estudiante_id": samuel, "fecha":"2030-01-01", "motivo":"HACK", "atencion":"Vista por conductor"})
j = r.json(); ok(j["atencion"]=="Vista por conductor" and j["motivo"]=="Cita médica", "conductor solo cambia 'atencion'")
ok(c.get(f"/ausencias/{aus['id']}", headers=H_acu).json()["atencion"]=="Vista por conductor", "acudiente ve confirmación del conductor")
# estudiante crea la suya sin enviar estudiante_id
r = c.post("/ausencias/", headers=H_est, json={"fecha":"2026-10-23","motivo":"Examen en otra sede"}); ok(r.status_code==200 and r.json()["estudiante_id"]==samuel, "estudiante reporta ausencia propia")

# --- FLUJO 3: conductor reporta falla -> admin gestiona -> acudiente/estudiante la ven
r = c.post("/fallas-vehiculo/", headers=H_con, json={"ruta_id": ruta_id, "tipo":"Frenos","gravedad":"Alta","descripcion":"Pedal blando"}); ok(r.status_code==200, "conductor reporta falla")
f = r.json(); ok(f["vehiculo_placa"] and f["atencion"]=="Reportada", "falla con vehículo derivado de la ruta: "+f["vehiculo_placa"])
ok(any(x["id"]==f["id"] for x in c.get("/fallas-vehiculo/", headers=H_acu).json()), "acudiente ve la alerta")
ok(any(x["id"]==f["id"] for x in c.get("/fallas-vehiculo/", headers=H_est).json()), "estudiante ve la alerta")
r = c.put(f"/fallas-vehiculo/{f['id']}", headers=H_adm, json={"ruta_id": ruta_id,"tipo":"Frenos","gravedad":"Alta","descripcion":"Pedal blando","atencion":"En revisión","observacion_admin":"Enviado a taller"}); ok(r.json()["atencion"]=="En revisión", "admin pone En revisión")
veh = [v for v in c.get("/vehiculos/", headers=H_adm).json() if v["placa"]==f["vehiculo_placa"]][0]; ok(veh["disponibilidad"]=="Mantenimiento", "vehículo pasó a Mantenimiento")
r = c.put(f"/fallas-vehiculo/{f['id']}", headers=H_con, json={"ruta_id": ruta_id,"tipo":"Frenos","gravedad":"Alta","descripcion":"Pedal blando y ruido","atencion":"Resuelta"}); ok(r.json()["atencion"]=="En revisión", "conductor no puede resolver")
ok(c.get(f"/fallas-vehiculo/{f['id']}", headers=H_acu).json()["atencion"]=="En revisión", "acudiente ve estado En revisión")

# --- baja lógica
r = c.delete(f"/registros-abordaje/{ab_id}", headers=H_con); ok(r.status_code==200, "eliminar abordaje")
ok(not any(x["id"]==ab_id for x in c.get("/registros-abordaje/", headers=H_acu).json()), "ya no aparece en listados")
ok(any(x["id"]==ab_id and x["estado"]=="Inactivo" for x in c.get("/registros-abordaje/?incluir_inactivos=true", headers=H_adm).json()), "sigue en BD con estado Inactivo")

# --- auditoría: actualizado cambia
e = est_acu[0]
r = c.put(f"/estudiantes/{e['id']}", headers=H_acu, json={**{k:e[k] for k in ("nombre","apellido","documento","grado")}, "direccion":"Calle nueva 1-2", "acudiente_id": 999}); j=r.json()
ok(j["direccion"]=="Calle nueva 1-2" and j["acudiente_id"]==e["acudiente_id"], "acudiente edita hijo; no puede cambiar acudiente_id")
ok(j["actualizado"]>=e["actualizado"] and j["creado"]==e["creado"], "creado fijo / actualizado cambia")
# acudiente crea hijo
r = c.post("/estudiantes/", headers=H_acu, json={"nombre":"Pedro","apellido":"Pérez Ortega","documento":"1100000001","grado":"6°","direccion":"Manga"}); ok(r.status_code==200 and r.json()["acudiente_id"]==e["acudiente_id"], "acudiente registra un hijo (acudiente_id automático)")
# estudiante solo edita grado/direccion
r = c.put(f"/estudiantes/{samuel}", headers=H_est, json={"nombre":"X","apellido":"Y","documento":"0","grado":"11°","direccion":"Otra"}); j=r.json(); ok(j["grado"]=="11°" and j["nombre"]=="Samuel", "estudiante solo edita grado y dirección")
# otro acudiente no ve hijos ajenos
ok(c.get(f"/estudiantes/{est_con_id}", headers=H_acu).status_code==404 if (est_con_id:=estu_con[0]["id"]) != e["id"] else True, "acudiente no ve hijos ajenos")
print("\nTODO OK")
