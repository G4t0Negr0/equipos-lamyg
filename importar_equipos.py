import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://yjkxvgillxyfemazczlu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inlqa3h2Z2lsbHh5ZmVtYXpjemx1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE3OTcxMzksImV4cCI6MjA5NzM3MzEzOX0.Ur4prZiESRkIcJ52t-LjBNnRB5zDaKx4BfrhZUZ-748"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def convertir_fecha(valor):
    if pd.isna(valor) or str(valor).strip() in ['----', '---', '-', '_', '', 'S/R', 'N/A', 'P', 'nan', 'None']:
        return None
    try:
        if isinstance(valor, pd.Timestamp):
            return valor.strftime('%Y-%m-%d')
        if isinstance(valor, (int, float)):
            return (pd.Timestamp('1899-12-30') + pd.Timedelta(days=int(valor))).strftime('%Y-%m-%d')
        return pd.to_datetime(str(valor), dayfirst=True).strftime('%Y-%m-%d')
    except:
        return None

def limpiar(valor):
    s = str(valor).strip()
    if s in ['nan', 'None', '----', '---', '-', '_', 'S/R', 'SIN NUMERO', '']:
        return None
    return s

df = pd.read_excel(
    r'C:\Users\Usuario\PycharmProjects\Equipos_LAMYG\Programa de Equipos LE-001-3.xlsx',
    sheet_name='2026',
    header=0
)

df.columns = [str(c).strip() for c in df.columns]

equipos_insertados = 0
errores = 0

for _, row in df.iterrows():
    codigo = limpiar(row.get('código identificación', ''))
    nombre = limpiar(row.get('Equipo', ''))
    if not codigo or not nombre:
        continue
    equipo = {
        'nombre': nombre,
        'codigo': codigo,
        'marca': limpiar(row.get('Marca/ modelo')),
        'numero_serie': limpiar(row.get('N° serie')),
        'rango_capacidad': limpiar(row.get('Rango o capacidad')),
        'resolucion': limpiar(row.get('Resolución')),
        'normas_asociadas': limpiar(row.get('NORMAS ASOCIADAS')),
        'tipo': limpiar(row.get('C/V/M')),
        'fecha_verificacion': convertir_fecha(row.get('Fecha Verificacíon')),
        'fecha_proxima_verificacion': convertir_fecha(row.get('Fecha próxima verificacion')),
        'fecha_calibracion': convertir_fecha(row.get('Fecha de calibración')),
        'fecha_proxima_calibracion': convertir_fecha(row.get('Fecha proxima calibración')),
        'calibrado_por': limpiar(row.get('Calibrado por:')),
        'fecha_mantenimiento': convertir_fecha(row.get('Fecha Mantenimiento')),
        'fecha_proximo_mantenimiento': convertir_fecha(row.get('Fecha próximo mantenimiento')),
        'puntos_calibracion': limpiar(row.get('Rango o puntos de calibración')),
        'responsable': limpiar(row.get('Responsable del equipo')),
        'observaciones': limpiar(row.get('Observaciones')),
        'estado': 'activo',
    }
    try:
        supabase.table('equipos').insert(equipo).execute()
        equipos_insertados += 1
        print(f"OK: {codigo} - {nombre}")
    except Exception as e:
        errores += 1
        print(f"ERROR {codigo}: {e}")

print(f"\nResumen: {equipos_insertados} insertados, {errores} errores")