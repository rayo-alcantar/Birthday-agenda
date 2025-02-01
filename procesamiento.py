# procesamiento.py
"""
Módulo encargado de manejar la lógica de notificaciones de cumpleaños.
Lee el archivo CSV, filtra los cumpleaños próximos y envía las notificaciones.
"""

import csv
import datetime
import json
import os
from config import IMPORTANCIA_1, IMPORTANCIA_2, IMPORTANCIA_3
from notificaciones import enviar_mensaje

# Rutas de archivos
CSV_PATH = "data/fechas.csv"
LOG_PATH = "data/enviados.json"

def cargar_cumpleaños():
	"""Carga la lista de cumpleaños desde el CSV y devuelve una lista de diccionarios."""
	cumpleaños = []
	try:
		with open(CSV_PATH, mode="r", encoding="utf-8") as file:
			reader = csv.reader(file)
			next(reader, None)  # Saltar encabezado si existe
			for row in reader:
				if len(row) >= 3:
					cumpleaños.append({
						"nombre": row[0].strip(),
						"fecha": row[1].strip(),
						"importancia": int(row[2].strip())
					})
	except FileNotFoundError:
		print("❌ ERROR: Archivo fechas.csv no encontrado.")
	except Exception as e:
		print(f"❌ ERROR al leer el archivo CSV: {e}")
	return cumpleaños

def calcular_dias_restantes(fecha):
	"""Calcula cuántos días faltan para el cumpleaños."""
	hoy = datetime.date.today()
	try:
		mes, dia = map(int, fecha.split("/"))
		fecha_cumple = datetime.date(hoy.year, mes, dia)
		# Si el cumpleaños ya pasó este año, ajustamos para el siguiente
		if fecha_cumple < hoy:
			fecha_cumple = datetime.date(hoy.year + 1, mes, dia)
		return (fecha_cumple - hoy).days
	except ValueError:
		print(f"❌ ERROR: Formato de fecha inválido ({fecha}). Debe ser MM/DD.")
		return None  # Retorna None si hay un error en la fecha

def filtrar_cumpleaños():
	"""Filtra los cumpleaños que deben notificarse hoy según su importancia."""
	cumpleaños = cargar_cumpleaños()
	notificar = []
	for c in cumpleaños:
		dias = calcular_dias_restantes(c["fecha"])
		if dias is None:
			continue  # Ignorar si la fecha es inválida
		importancia = c["importancia"]
		umbrales = IMPORTANCIA_1 if importancia == 1 else IMPORTANCIA_2 if importancia == 2 else IMPORTANCIA_3
		if dias in umbrales:
			notificar.append((c["nombre"], dias))
	return notificar

def cargar_registro():
	"""Carga el registro de notificaciones enviadas. Si no existe, lo crea vacío."""
	directorio = os.path.dirname(LOG_PATH)
	if not os.path.exists(directorio):
		os.makedirs(directorio)
	if not os.path.exists(LOG_PATH):
		print("⚠️ `enviados.json` no existe. Creándolo...")
		try:
			with open(LOG_PATH, "w", encoding="utf-8") as file:
				json.dump({}, file, indent=4)
			print("✅ `enviados.json` creado exitosamente.")
		except Exception as e:
			print(f"❌ ERROR al crear `enviados.json`: {e}")
	try:
		with open(LOG_PATH, "r", encoding="utf-8") as file:
			return json.load(file)
	except json.JSONDecodeError:
		print("⚠️ ADVERTENCIA: `enviados.json` está corrupto. Se reiniciará.")
		return {}
	except Exception as e:
		print(f"❌ ERROR al leer `enviados.json`: {e}")
		return {}

def guardar_registro(registro):
	"""Guarda el registro actualizado de notificaciones enviadas."""
	try:
		with open(LOG_PATH, "w", encoding="utf-8") as file:
			json.dump(registro, file, indent=4)
	except Exception as e:
		print(f"❌ ERROR al guardar `enviados.json`: {e}")

def registrar_notificacion(nombre, dias):
	"""
	Registra una notificación con el nombre y el umbral de días antes para evitar duplicados.
	Si hoy es el primer día del mes, se utiliza un registro mensual para evitar múltiples notificaciones
	durante el mismo día.
	"""
	registro = cargar_registro()
	hoy = datetime.date.today()
	fecha_hoy = str(hoy)
	
	if hoy.day == 1:
		mes_actual = hoy.strftime("%Y-%m")
		if mes_actual not in registro:
			registro[mes_actual] = {}
		if nombre in registro[mes_actual]:
			return False
		registro[mes_actual][nombre] = dias
	else:
		if fecha_hoy not in registro:
			registro[fecha_hoy] = {}
		if nombre not in registro[fecha_hoy]:
			registro[fecha_hoy][nombre] = []
		if dias in registro[fecha_hoy][nombre]:
			return False
		registro[fecha_hoy][nombre].append(dias)
	
	guardar_registro(registro)
	return True

def procesar_notificaciones():
	"""Procesa y envía notificaciones según los cumpleaños cercanos."""
	pendientes = filtrar_cumpleaños()
	for nombre, dias in pendientes:
		if registrar_notificacion(nombre, dias):
			if dias == 0:
				mensaje = f"🎉 ¡Hoy es el cumpleaños de {nombre}! 🎂✨"
			elif dias == 1:
				mensaje = f"🎉 ¡Mañana es el cumpleaños de {nombre}! 🎁"
			else:
				mensaje = f"🎉 ¡{nombre} cumple años en {dias} días! 🎈"
			enviar_mensaje(mensaje)

if __name__ == "__main__":
	procesar_notificaciones()
