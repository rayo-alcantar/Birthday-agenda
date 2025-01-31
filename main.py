# main.py
"""
Script principal del sistema de notificaciones de cumpleaños.
Se ejecuta diariamente y determina si debe:
- Enviar la lista mensual de cumpleaños (si es día 1).
- Enviar recordatorios escalonados según la proximidad de los cumpleaños.
"""

import datetime  # 🔹 Esto estaba faltando
import logging
from procesamiento import procesar_notificaciones, cargar_cumpleaños
from notificaciones import enviar_mensaje

# Configuración del logging
logging.basicConfig(
	filename="logs/main.log",
	level=logging.INFO,
	format="%(asctime)s - %(levelname)s - %(message)s",
	encoding="utf-8"
)

def generar_mensaje_mensual():
	"""
	Genera y envía la lista de cumpleaños del mes si hoy es el día 1.
	Ahora los ordena del primero al último y usa un formato más legible.
	"""
	hoy = datetime.date.today()
	mes_actual = hoy.strftime("%m")  # Formato MM
	nombres_meses = {
		"01": "enero", "02": "febrero", "03": "marzo", "04": "abril",
		"05": "mayo", "06": "junio", "07": "julio", "08": "agosto",
		"09": "septiembre", "10": "octubre", "11": "noviembre", "12": "diciembre"
	}

	cumpleaños_mes = [
		{"nombre": c["nombre"], "dia": int(c["fecha"].split("/")[1])}
		for c in cargar_cumpleaños()
		if c["fecha"].startswith(mes_actual)
	]

	# Ordenamos por día del mes
	cumpleaños_mes.sort(key=lambda x: x["dia"])

	if cumpleaños_mes:
		mensaje = "**📆 Cumpleaños de este mes:**\n" + "\n".join(
			[f"🎂 {c['nombre']}: {c['dia']} de {nombres_meses[mes_actual]}." for c in cumpleaños_mes]
		)
		enviar_mensaje(mensaje)
		logging.info("✅ Lista mensual de cumpleaños enviada.")
	else:
		logging.info("ℹ️ No hay cumpleaños en este mes.")

def ejecutar():
	"""
	Función principal que gestiona la ejecución diaria del sistema.
	"""
	logging.info("🚀 Inicio del proceso de notificaciones.")
	
	hoy = datetime.date.today()

	if hoy.day == 1:
		logging.info("📆 Hoy es el primer día del mes. Enviando lista mensual...")
		generar_mensaje_mensual()

	logging.info("🔍 Procesando notificaciones diarias...")
	procesar_notificaciones()

	logging.info("✅ Proceso de notificaciones finalizado.")

if __name__ == "__main__":
	ejecutar()
