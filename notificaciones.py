# notificaciones.py
"""
Módulo encargado de enviar notificaciones a Telegram.
Utiliza la API de Telegram para enviar mensajes y maneja errores de conexión.
"""
import os
import requests
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# Crear el directorio logs si no existe
LOGS_DIR = "logs"
LOG_FILE = os.path.join(LOGS_DIR, "notificaciones.log")

if not os.path.exists(LOGS_DIR):
	os.makedirs(LOGS_DIR)

# Configuración del logging
logging.basicConfig(
	filename="logs/notificaciones.log",
	level=logging.INFO,
	format="%(asctime)s - %(levelname)s - %(message)s",
	encoding="utf-8"
)

# URL base de la API de Telegram
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def enviar_mensaje(mensaje):
	"""
	Envía un mensaje a Telegram usando el bot configurado.
	
	Parámetros:
	- mensaje (str): Texto a enviar al chat.

	Retorna:
	- True si el mensaje se envió con éxito, False en caso de error.
	"""
	datos = {
		"chat_id": TELEGRAM_CHAT_ID,
		"text": mensaje,
		"parse_mode": "Markdown"  # Permite formateo básico
	}

	try:
		response = requests.post(TELEGRAM_API_URL, data=datos, timeout=10)

		if response.status_code == 200:
			logging.info(f"✅ Mensaje enviado con éxito: {mensaje}")
			return True
		else:
			logging.error(f"❌ Error al enviar mensaje. Código: {response.status_code} - Respuesta: {response.text}")
			return False

	except requests.exceptions.RequestException as e:
		logging.error(f"❌ ERROR DE CONEXIÓN: No se pudo enviar el mensaje a Telegram. Detalle: {e}")
		return False
