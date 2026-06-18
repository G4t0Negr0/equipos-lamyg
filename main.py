from fastapi import FastAPI
from supabase import create_client
from datetime import date, timedelta

SUPABASE_URL = "https://yjkxvgillxyfemazczlu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlqa3h2Z2lsbHh5ZmVtYXpjemx1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3OTcxMzksImV4cCI6MjA5NzM3MzEzOX0.Ur4prZiESRkIcJ52t-LjBNnRB5zDaKx4BfrhZUZ-748"  # tu clave legacy anon

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI(title="Sistema de Equipos LAMYG")


@app.get("/equipos")
def listar_equipos():
    result = supabase.table("equipos").select("*").order("nombre").execute()
    return result.data


@app.get("/equipos/alertas")
def alertas_calibracion():
    hoy = date.today()
    limite = hoy + timedelta(days=60)
    result = supabase.table("equipos").select(
        "nombre, codigo, fecha_proxima_calibracion, calibrado_por, responsable"
    ).lte("fecha_proxima_calibracion", str(limite)).order("fecha_proxima_calibracion").execute()

    equipos = []
    for e in result.data:
        fecha = date.fromisoformat(e["fecha_proxima_calibracion"])
        dias = (fecha - hoy).days
        e["dias_para_vencer"] = dias
        e["estado_alerta"] = "vencido" if dias < 0 else "critico" if dias <= 30 else "proximo"
        equipos.append(e)
    return equipos


@app.get("/equipos/{codigo}")
def detalle_equipo(codigo: str):
    result = supabase.table("equipos").select("*").eq("codigo", codigo).execute()
    if not result.data:
        return {"error": "Equipo no encontrado"}
    return result.data[0]


@app.post("/equipos")
def crear_equipo(equipo: dict):
    result = supabase.table("equipos").insert(equipo).execute()
    return result.data


@app.put("/equipos/{codigo}/calibracion")
def registrar_calibracion(codigo: str, datos: dict):
    result = supabase.table("equipos").update(datos).eq("codigo", codigo).execute()
    return result.data