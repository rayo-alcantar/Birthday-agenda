# Rayo Alcantar Birthday Agenda

Este proyecto tiene como propósito enviar notificaciones automáticas de cumpleaños y alertas escalonadas en función de la importancia de cada evento, así como generar un resumen mensual el primer día de cada mes.

## Estructura de directorios

```
rayo-alcantar-birthday-agenda/
├── config.py
├── main.py
├── notificaciones.py
├── procesamiento.py
├── r.txt
└── data/
    └── fechas.csv
```

A continuación, se describe la función de cada archivo:

1. **config.py**  
   Contiene las variables de configuración:
   - `IMPORTANCIA_1`, `IMPORTANCIA_2`, `IMPORTANCIA_3`: Arreglos con los días de antelación para enviar notificaciones, según la importancia.  
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`: Credenciales para interactuar con la API de Telegram.

2. **main.py**  
   Archivo principal del sistema. Ejecuta los siguientes pasos:  
   - Envía un listado de todos los cumpleaños del mes cuando es día 1.  
   - Llama a la función que procesa y envía notificaciones diarias según la fecha y la importancia de los cumpleaños.

3. **notificaciones.py**  
   Define la función para enviar mensajes a un chat de Telegram a través de su API. Maneja la comunicación y captura errores de conexión.

4. **procesamiento.py**  
   Contiene toda la lógica para:
   - Leer y cargar los cumpleaños desde `data/fechas.csv`.  
   - Calcular los días restantes para cada cumpleaños.  
   - Filtrar y construir un listado de a quién notificar según la importancia y la cercanía de la fecha.  
   - Registrar en `data/enviados.json` la notificación enviada para evitar envíos duplicados el mismo día.

5. **r.txt**  
   Archivo de requerimientos de Python (paquetes a instalar).

6. **data/fechas.csv**  
   Archivo CSV con las columnas:
   - **Nombre**  
   - **Fecha** (formato `MM/DD`, por ejemplo `02/29`)  
   - **Importancia** (valor numérico 1, 2 o 3)  

   Un ejemplo podría ser:
   ```
   Nombre,Fecha,Importancia
   UsuarioEjemplo,12/25,1
   ```
   Donde:
   - 1 es importancia alta.
   - 2 es importancia media.
   - 3 es importancia baja.

## Requerimientos previos

- **Python 3.12 (recomendado)**
- **PIP** para instalar dependencias.
- Se recomienda contar con permisos de administrador (sudo) si vas a utilizar `systemd` en tu servidor.

## Instalación de dependencias

1. Clona o descarga este repositorio.
2. Entra a la carpeta `rayo-alcantar-birthday-agenda`.
3. Instala los requerimientos:
   ```
   pip install -r r.txt
   ```

## Configuración

1. Edita el archivo `config.py` y reemplaza los valores de:
   - `TELEGRAM_BOT_TOKEN` con el token de tu bot de Telegram.
   - `TELEGRAM_CHAT_ID` con el **Chat ID** en donde se enviarán los mensajes.

#### Obtener datos de Telegram

- Inicia una conversación con **@BotFather**.  
- Escribe el comando `/newbot`.  
- Responde las preguntas que te haga.  
- Te dará la key de tu bot.  
- Inicia el bot **@userinfobot**.  
- Te dará tu user ID.

2. Ajusta los umbrales de días en las listas
   - `IMPORTANCIA_1`
   - `IMPORTANCIA_2`
   - `IMPORTANCIA_3`  
   Si lo necesitas, de acuerdo con tus preferencias de alertas.

3. Asegúrate de que el archivo `data/fechas.csv` contenga todos los nombres y fechas requeridos. Verifica que el formato sea `MM/DD` para la fecha y que la última columna sea la importancia (1, 2 o 3).

## Ejecución manual

Dentro de la carpeta principal, ejecuta:

```
python main.py
```

De esta manera se correrá la lógica que:
- Si es primer día del mes, enviará la lista de cumpleaños del mes.
- Checará si algún cumpleaños entra en los umbrales para enviar notificaciones.

## Ejecución automática con systemd y timer (cada hora)

Para programar la ejecución automática cada hora en un servidor Ubuntu (o en sistemas que usen `systemd`), puedes seguir estos pasos:

1. **Crear el servicio** (por ejemplo, `/etc/systemd/system/cumpleanios.service`):
   ```ini
   [Unit]
   Description=Servicio para notificaciones de cumpleaños

   [Service]
   Type=oneshot
   # Ajusta la ruta absoluta hacia main.py
   ExecStart=/usr/bin/python3 /ruta/absoluta/rayo-alcantar-birthday-agenda/main.py
   # Importante: si usas un entorno virtual, reemplaza /usr/bin/python3
   # con la ruta de tu Python en el entorno virtual
   WorkingDirectory=/ruta/absoluta/rayo-alcantar-birthday-agenda
   # Opcional: si necesitas variables de entorno, agrega:
   # Environment="VARIABLE=valor"

   [Install]
   WantedBy=multi-user.target
   ```

2. **Crear el timer** (por ejemplo, `/etc/systemd/system/cumpleanios.timer`):
   ```ini
   [Unit]
   Description=Timer para ejecutar notificaciones de cumpleaños cada hora

   [Timer]
   # Puedes utilizar OnCalendar=hourly para cada hora en punto:
   OnCalendar=hourly

   # Opcional, si quieres un retardo aleatorio para no saturar a la hora en punto:
   # RandomizedDelaySec=300

   # Asocia el timer al servicio
   Unit=cumpleanios.service

   [Install]
   WantedBy=timers.target
   ```

3. **Recarga el daemon y activa el timer**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable cumpleanios.timer
   sudo systemctl start cumpleanios.timer
   ```

4. **Verifica que se esté ejecutando**:
   ```bash
   systemctl status cumpleanios.timer
   ```
   Debería mostrar que el timer está activo y la próxima hora de ejecución.

5. **Revisar logs** (opcional):
   ```
   journalctl -u cumpleanios.service -f
   ```
   Con ello observarás los mensajes de cada corrida de `main.py`.

> **Nota:** Si deseas personalizar la frecuencia de ejecución, puedes modificar `OnCalendar=`. Por ejemplo, para cada 30 minutos:
> ```
> OnCalendar=*:0/30
> ```
> Ajústalo de acuerdo con tus necesidades.

## Notas finales

- Se ha incluido (o se incluirá) un directorio `logs/` donde el sistema almacenará registros (`main.log` y `notificaciones.log`).  
- El archivo `data/enviados.json` se utiliza para evitar notificaciones duplicadas en el mismo día y se crea/actualiza de manera automática.
- Para agregar o eliminar cumpleaños, simplemente actualiza el archivo `data/fechas.csv` y verifica la columna de importancia.

¡Listo! Ahora cuentas con un sistema profesional y modular para la administración de notificaciones de cumpleaños, con soporte para ejecución automática en `systemd` y compatibilidad con bots de Telegram.

## ¿Te gustó la herramienta?

Si te gustó la herramienta, podrías considerar ̀[hacerme una donación](https://www.paypal.com/paypalme/rayoalcantar?country.x=MX&locale.x=es_XC)
