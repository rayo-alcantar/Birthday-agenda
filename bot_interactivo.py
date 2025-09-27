# bot_interactivo.py
"""
Bot de Telegram para consultar cumpleaños con soporte de:
- Comandos: /start, /mes, /cumple <nombre>
- Botones persistentes (ReplyKeyboard) que envían /mes y /cumple
- Flujo guiado cuando /cumple no recibe nombre (conversación)

Arquitectura:
- UI: mensajes y teclados (_teclado_principal)
- Orquestación: handlers y conversación
- Dominio: funciones importar de 'procesamiento'

Accesibilidad:
- Textos claros, sin emojis.
"""

import logging
from datetime import date
from typing import List, Dict, Tuple, Optional

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Importar funciones y configuración
from config import TELEGRAM_BOT_TOKEN
from procesamiento import obtener_cumpleanos_mes_actual, buscar_persona_por_nombre

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------
# Constantes y estados
# ---------------------------
NOMBRES_MESES = {
    "01": "Enero", "02": "Febrero", "03": "Marzo", "04": "Abril",
    "05": "Mayo", "06": "Junio", "07": "Julio", "08": "Agosto",
    "09": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre",
}

ASK_NAME = 1  # estado de conversación para pedir el nombre cuando /cumple viene vacío

# ---------------------------
# Utilidades de fecha
# ---------------------------
def _nombre_mes(mes_num: int) -> str:
    return NOMBRES_MESES.get(f"{int(mes_num):02d}", "Mes desconocido")

def _parse_mm_dd(fecha: str) -> Optional[Tuple[int, int]]:
    """
    Soporta 'MM/DD', 'DD/MM' y separadores '/' o '-'.
    Devuelve (mes, dia) como enteros o None si no se puede parsear.
    """
    if not fecha:
        return None
    txt = str(fecha).strip().replace("-", "/")
    parts = txt.split("/")
    if len(parts) != 2:
        return None
    try:
        a = int(parts[0])
        b = int(parts[1])
    except ValueError:
        return None

    # Heurística: preferimos MM/DD si es válida; si no, intentamos DD/MM.
    if 1 <= a <= 12 and 1 <= b <= 31:
        return a, b  # MM/DD
    if 1 <= a <= 31 and 1 <= b <= 12:
        return b, a  # DD/MM
    return None

def _formatear_fecha_legible(persona: dict, mes_predeterminado: Optional[int] = None) -> str:
    """
    Reglas de compatibilidad con el bot original:
    1) Si existe persona['dia'], usarlo y tomar mes_predeterminado (mes actual) -> "Día X de <mes>"
    2) Si existe persona['fecha'] (MM/DD o DD/MM), formatear esa fecha.
    3) Si existen persona['mes'] y persona['dia'], usarlos.
    4) Si nada funciona, devolver "(fecha no disponible)".
    """
    # 1) Compatibilidad original: 'dia' + mes actual
    if persona.get("dia") is not None:
        try:
            dia = int(persona["dia"])
            mes = mes_predeterminado or date.today().month
            return f"{dia} de {_nombre_mes(mes)}"
        except Exception:
            pass

    # 2) 'fecha' parseable
    md = _parse_mm_dd(persona.get("fecha"))
    if md:
        mes, dia = md
        return f"{dia} de {_nombre_mes(mes)}"

    # 3) 'mes' + 'dia'
    if persona.get("mes") is not None and persona.get("dia") is not None:
        try:
            mes = int(persona["mes"])
            dia = int(persona["dia"])
            return f"{dia} de {_nombre_mes(mes)}"
        except Exception:
            pass

    # 4) Sin datos válidos
    return "(fecha no disponible)"

# ---------------------------
# Presentación
# ---------------------------
def _listar_cumples(matriz_personas: List[Dict[str, str]], mes_predeterminado: Optional[int] = None) -> str:
    if not matriz_personas:
        return "No hay registros de cumpleaños."
    lineas = []
    for persona in matriz_personas:
        fecha_legible = _formatear_fecha_legible(persona, mes_predeterminado=mes_predeterminado)
        nombre = persona.get("nombre", "Sin nombre")
        lineas.append(f"- {nombre} — {fecha_legible}")
    return "\n".join(lineas)

def _mensaje_cumples_mes_actual() -> str:
    cumpleanos_del_mes = obtener_cumpleanos_mes_actual()
    if not cumpleanos_del_mes:
        return "No hay ningún cumpleaños registrado para este mes."
    mes_actual_num = date.today().month
    nombre_mes = _nombre_mes(mes_actual_num)
    cuerpo = _listar_cumples(cumpleanos_del_mes, mes_predeterminado=mes_actual_num)
    return f"Cumpleaños de {nombre_mes}:\n\n{cuerpo}"

def _teclado_principal() -> ReplyKeyboardMarkup:
    """
    Teclado de respuesta persistente que envía texto como si fuera escrito por el usuario.
    """
    botones = [
        [KeyboardButton("/mes"), KeyboardButton("/cumple")],
    ]
    return ReplyKeyboardMarkup(botones, resize_keyboard=True, one_time_keyboard=False)

# ---------------------------
# Handlers de comandos
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    texto = (
        "Bot de cumpleaños listo.\n\n"
        "Comandos disponibles:\n"
        "- /mes  → lista de cumpleaños del mes actual.\n"
        "- /cumple <nombre>  → busca por nombre.\n\n"
        "También puedes usar los botones de la parte inferior."
    )
    await update.message.reply_text(texto, reply_markup=_teclado_principal())

async def mes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_mensaje_cumples_mes_actual(), reply_markup=_teclado_principal())

# ---------------------------
# Flujo conversacional para /cumple
# ---------------------------
async def cumple_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entry point del ConversationHandler para /cumple:
    - Si el usuario ya puso argumentos: resuelve directo y termina.
    - Si no hay argumentos (o vino como texto plano "/cumple" desde el botón): pide el nombre.
    """
    # Caso 1: si esto vino como comando (/cumple ...) con argumentos
    if update.message and update.message.text and update.message.text.startswith("/cumple"):
        # Extraer argumentos del comando si existen
        parts = update.message.text.split(maxsplit=1)
        if len(parts) > 1:
            nombre = parts[1].strip()
            await _resolver_busqueda_y_responder(update, context, nombre)
            return ConversationHandler.END

    # Caso 2: sin argumentos -> pedir nombre
    await update.message.reply_text("Escribe el nombre a buscar.", reply_markup=_teclado_principal())
    return ASK_NAME

async def recibir_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    nombre = (update.message.text or "").strip()
    if not nombre:
        await update.message.reply_text("No recibí un nombre. Intenta nuevamente o usa /cancel.", reply_markup=_teclado_principal())
        return ASK_NAME

    await _resolver_busqueda_y_responder(update, context, nombre)
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Búsqueda cancelada.", reply_markup=_teclado_principal())
    return ConversationHandler.END

# ---------------------------
# Lógica de búsqueda reutilizable
# ---------------------------
async def _resolver_busqueda_y_responder(update: Update, context: ContextTypes.DEFAULT_TYPE, nombre: str) -> None:
    coincidencias = buscar_persona_por_nombre(nombre)
    if not coincidencias:
        await update.message.reply_text(f'No encontré a nadie con el nombre "{nombre}".', reply_markup=_teclado_principal())
        return

    partes = ["Resultados:"]
    for persona in coincidencias:
        fecha_legible = _formatear_fecha_legible(persona)
        partes.append(f"- {persona.get('nombre', 'Sin nombre')} — {fecha_legible}")

    await update.message.reply_text("\n".join(partes), reply_markup=_teclado_principal())

# ---------------------------
# Arranque de la app
# ---------------------------
def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Falta TELEGRAM_BOT_TOKEN en config.")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # /start y /mes normales
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mes", mes))

    # ConversationHandler para /cumple:
    # - Entry points: cuando el usuario escribe /cumple con o sin args,
    #   y cuando pulsa el botón que envía exactamente "/cumple".
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("cumple", cumple_entry),                            # /cumple [args...]
            MessageHandler(filters.TEXT & filters.Regex(r"^/cumple$"), cumple_entry),  # botón "/cumple"
        ],
        states={
            ASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancelar)],
        allow_reentry=True,
    )
    app.add_handler(conv)

    # Además, si el usuario pulsa el botón "/mes" (texto literal)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^/mes$"), mes))

    logger.info("Iniciando bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
