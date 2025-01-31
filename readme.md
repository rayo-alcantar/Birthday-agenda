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
   - Envia un listado de todos los cumpleaños del mes cuando es día 1.  
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

- **Python 3.7+** (de preferencia una versión moderna de Python 3).
- **PIP** para instalar dependencias.
- Se recomienda contar con permisos de administrador (sudo) si va a utilizar `systemd` en su servidor.

## Instalación de dependencias

1. Clonar o descargar este repositorio.
2. Entrar a la carpeta `rayo-alcantar-birthday-agenda`.
3. Instalar los requerimientos:
   ```bash
   pip install -r r.txt
   ```

## Configuración

1. Edite el archivo `config.py` y reemplace los valores de:
   - `TELEGRAM_BOT_TOKEN` con el token de su bot de Telegram.
   - `TELEGRAM_CHAT_ID` con el **Chat ID** en donde se enviarán los mensajes.

#### sacar datos de telegram.

1.1. Inicia una combersación con @BotFather
1.2. Escribe el comando /newbot
1.3. Responde la pregunta que te hace.
1.4. Te dará tu key de bot.
1.5. Inicia el bot @userinfobot
1.6. Te dará tu user id.

2. Ajuste los umbrales de días en las lista
   - `IMPORTANCIA_1`
   - `IMPORTANCIA_2`
   - `IMPORTANCIA_3`  
   Si lo necesita, de acuerdo con sus preferencias de alertas.

3. Asegúrese de que el archivo `data/fechas.csv` contenga todos los nombres y fechas requeridos. Verifique que el formato sea `MM/DD` para la fecha y que la última columna sea la importancia (1, 2 o 3).

## Ejecución manual

Dentro de la carpeta principal, ejecute:

```bash
python main.py
```

De esta manera se correrá la lógica que:
- Si es primer día del mes, enviará la lista de cumpleaños del mes.
- Checará si algún cumpleaños entra en los umbrales para enviar notificaciones.

## Ejecución automática con systemd y timer (cada hora)

Para programar la ejecución automática cada hora en un servidor Ubuntu (o en sistemas que usen `systemd`), puede seguir estos pasos:

1. **Crear el servicio** (por ejemplo, `/etc/systemd/system/cumpleanios.service`):
   ```ini
   [Unit]
   Description=Servicio para notificaciones de cumpleaños

   [Service]
   Type=oneshot
   # Ajustar la ruta absoluta hacia main.py
   ExecStart=/usr/bin/python3 /ruta/absoluta/rayo-alcantar-birthday-agenda/main.py
   # Importante: si usa un entorno virtual, reemplace /usr/bin/python3 
   # con la ruta de su Python en el entorno virtual
   WorkingDirectory=/ruta/absoluta/rayo-alcantar-birthday-agenda
   # Opcional: si necesita variables de entorno, agregue:
   # Environment="VARIABLE=valor"

   [Install]
   WantedBy=multi-user.target
   ```

2. **Crear el timer** (por ejemplo, `/etc/systemd/system/cumpleanios.timer`):
   ```ini
   [Unit]
   Description=Timer para ejecutar notificaciones de cumpleaños cada hora

   [Timer]
   # Puede utilizar OnCalendar=hourly para cada hora en punto:
   OnCalendar=hourly

   # Opcional, si quiere un retardo aleatorio para no saturar a la hora en punto:
   # RandomizedDelaySec=300

   # Asocie el timer al servicio
   Unit=cumpleanios.service

   [Install]
   WantedBy=timers.target
   ```

3. **Recargar el daemon y activar el timer**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable cumpleanios.timer
   sudo systemctl start cumpleanios.timer
   ```

4. **Verificar que se esté ejecutando**:
   ```bash
   systemctl status cumpleanios.timer
   ```
   Debería mostrar que el timer está activo y marcará la próxima hora de ejecución.

5. **Revisar logs** (opcional):
   ```bash
   journalctl -u cumpleanios.service -f
   ```
   Con ello observará los mensajes de cada corrida de `main.py`.

> **Nota:** Si desea personalizar la frecuencia de ejecución, puede modificar `OnCalendar=`. Por ejemplo, para cada 30 minutos:
> ```
> OnCalendar=*:0/30
> ```
> Ajuste de acuerdo con sus necesidades.

## Notas finales

- Se ha incluido un archivo llamado `logs/` (carpeta generada automáticamente) donde el sistema almacenará registros (`main.log` y `notificaciones.log`).  
- El archivo `data/enviados.json` se utiliza para evitar notificaciones duplicadas en el mismo día y se crea/actualiza de manera automática.
- Para agregar o eliminar cumpleaños, simplemente actualice el archivo `data/fechas.csv` y verifique la columna de importancia.

Con esto, su sistema enviará mensajes de alerta cada que un cumpleaños se acerque según la configuración especificada, así como un listado mensual el primer día de cada mes.

¡Listo! Ahora cuenta con un sistema profesional y modular para la administración de notificaciones de cumpleaños, con soporte para ejecución automática en `systemd` y compatibilidad con bots de Telegram.
```