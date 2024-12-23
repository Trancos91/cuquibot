import datetime
import yaml
import tomllib
from pytz import timezone
from telegram import Update
from telegram.ext import (Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, Defaults, CallbackQueryHandler)
import modulos.comandos as comandos
import modulos.config as config
from modulos.editor import EditorSheet
from modulos.respuestas import Respuestas
from modulos.decoradores import requiere_usuarix, logea

##########################################################################
# Respuestas a mensajes
##########################################################################
def handle_message(texto: str, update: Update):

    respuesta = Respuestas(texto, update).respuestas()
    return respuesta

@requiere_usuarix
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Procesa los mensajes que no atraparon las funciones de comandos. En caso
    de ser un mensaje enviado en un grupo, revisa si el bot fue tageado para responder,
    y elimina el tag del bot del mensaje para enviar a procesarlo. Registra los mensajes
    sólo si el bot fue tageado o le hablaron por privado.
    """
    message_type: str = update.message.chat.type
    texto: str = update.message.text

    if message_type == "group" or message_type == "supergroup":
        if config.BOT_USERNAME in texto:
            if config.LOG:
                print(f'Usuario {update.effective_user.id}(@{update.effective_user.username}) en {update.message.chat_id}: {texto}')
            texto:str = texto.replace(config.BOT_USERNAME, "").strip()
            respuesta: str = handle_message(texto, update)
        else:
            return
    else:
        if config.LOG:
            print(f'Usuario {update.effective_user.id}(@{update.effective_user.username}) en {update.message.chat_id}: {texto}')
        respuesta: str = handle_message(texto, update)
    
    print(f'Bot: {respuesta}')
    await update.message.reply_text(respuesta)

##########################################################################
# Métodos pasivos
##########################################################################
async def enviar_mensaje_jobs(context: ContextTypes.DEFAULT_TYPE):
    """Enviar un mensaje desde un Job"""
    if context.job.data[1]["activo"]:
        await context.bot.send_message(chat_id=context.job.chat_id, text=str(context.job.data[1]["mensaje"]).strip())


async def recordatorios_quehaceres(context: ContextTypes.DEFAULT_TYPE):
    """
    Revisa si pasó el tiempo apropiado en el recordatorio, y si sí, envía un mensaje
    recordándolo y registra la fecha. También revisa si pasó el tiempo 'snooze'
    desde la última vez que lo hizo.
    """
    recordatorio_key = context.job.data[0]
    recordatorio_value = context.job.data[1]

    if not recordatorio_value["activo"]: return

    editor = EditorSheet()
    hoy = datetime.datetime.today().date()
    último = editor.get_último_quehacer(recordatorio_value["quehacer"])
    último_aviso = recordatorio_value["último_aviso"]
    último_aviso = datetime.datetime.strptime(último_aviso, "%Y/%m/%d").date() if último_aviso else None
    días_espera = int(recordatorio_value["días_espera"])
    snooze = int(recordatorio_value["snooze"])
    mensaje = (f"Parece que pasaron más de {días_espera} días desde la última vez"
        f" que {recordatorio_value["mensaje"]}. Quizás convendría hacerlo hoy :)")

    def actualizar_último_aviso():
        recordatorio_value["último_aviso"] = hoy.strftime("%Y/%m/%d")
        # Actualiza el el campo de "último_aviso" al día de hoy, y lo escribe en el yaml
        config.RECORDATORIOS["recordatorios quehaceres"][recordatorio_key] = recordatorio_value
        config.actualizar_recordatorios()

    if isinstance(último, str):
        if (not último_aviso or 
            (hoy - último_aviso).days > snooze):
            await context.bot.send_message(chat_id=context.job.chat_id, text=último)
            actualizar_último_aviso()
        return
    else:
        último = último.date()
    if ((hoy - último).days > días_espera and 
            ((hoy - último_aviso).days > snooze if último_aviso else not último_aviso)):
        await context.bot.send_message(chat_id=context.job.chat_id, text=mensaje)
        actualizar_último_aviso()
        return

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} causó el siguiente error: \n{context.error}")
    if "Timed out" in str(context.error):
        await update.message.reply_text("⚠️ Uy! Recibí un error de 'Timed out'. "
            "Esto normalmente pasa cuando no pude conectar con el servidor de Telegram, "
            "pero después de haber realizado las operaciones que me solicitaste.\n"
            "ℹ️ Las acciones que pediste que haga probablemente se hicieron, pero si querés asegurarte, "
            "podés enviarme el mismo mensaje de nuevo!")
    if update is not None:
        await update.message.reply_text("Uy! Tuve un error corriendo este código.")

##########################################################################
#Métodos de inicialización
##########################################################################
def inicializar_jobs(app):
    """Inicializa todos los Jobs"""

    inicializar_jobs_mensajes_diarios(app)
    inicializar_jobs_recordatorios(app)

    joblist = [x.name for x in app.job_queue.jobs()]
    print(f"Inicializado Jobqueues: {joblist}")

def inicializar_jobs_mensajes_diarios(app):
    """
    Itera sobre los mensajes recurrentes en el yaml recordatorios.yaml bajo 
    la categoría "recordatorios_diarios" y los registra en jobs con los parámetros
    apropiados.
    """
    if not config.RECORDATORIOS["recordatorios diarios"]: return

    for recordatorio in config.RECORDATORIOS["recordatorios diarios"].items():
        app.job_queue.run_daily(enviar_mensaje_jobs, datetime.time(*recordatorio[1]["horario"]),
                                name=recordatorio[0], chat_id=config.CHAT_ID, days=[*recordatorio[1]["días_semana"]],
                                data=recordatorio, job_kwargs={"misfire_grace_time": None})

def inicializar_jobs_recordatorios(app):
    """
    Itera sobre los recordatorios registrados en el yaml recordatorios.yaml bajo
    la categoría "recordatorios_quehaceres" y los registra en jobs con los parámetros
    apropiados.
    """
    if not config.RECORDATORIOS["recordatorios quehaceres"]: return

    for recordatorio in config.RECORDATORIOS["recordatorios quehaceres"].items():
        app.job_queue.run_daily(recordatorios_quehaceres, datetime.time(12, 0, 0),
                                name=recordatorio[0], chat_id=config.CHAT_ID,
                                data=recordatorio, job_kwargs={"misfire_grace_time": None})


if __name__ == '__main__':

    # Cargando valores a config
    config.cargar_config()
    config.cargar_recordatorios()

    #Definiendo configuración por defecto del bot
    defaults = Defaults(parse_mode="HTML", tzinfo=timezone("America/Argentina/Buenos_Aires"))
    print("Inicializando bot...")
    print(f"Hora actual: {datetime.datetime.now(timezone("America/Argentina/Buenos_Aires"))}")
    app = Application.builder().token(config.TOKEN).defaults(defaults).build()

    #Inicializando Jobs
    inicializar_jobs(app)

    # Comandos
    app.add_handler(CommandHandler('start', comandos.start_command))
    app.add_handler(CommandHandler('help', comandos.help_command))
    app.add_handler(CommandHandler('agregartareas', comandos.agregartareas_command))
    app.add_handler(CommandHandler('agregarcompras', comandos.agregarcompras_command))
    app.add_handler(CommandHandler('despejarcompras', comandos.despejarcompras_command))
    app.add_handler(CommandHandler('despejarlistatareas', comandos.despejarlistatareas_command))
    app.add_handler(CommandHandler('despejarunatarea', comandos.despejarunatarea_command))
    app.add_handler(CommandHandler('despejarlistacompras', comandos.despejarlistacompras_command))
    app.add_handler(CommandHandler('registrarviveres', comandos.registrarviveres_command))
    app.add_handler(CommandHandler('despejarregistrado', comandos.despejarregistrado_command))
    app.add_handler(CommandHandler('desactivarrecordatorio', comandos.desactivarrecordatorio_command))
    app.add_handler(CommandHandler('activarrecordatorio', comandos.activarrecordatorio_command))
    app.add_handler(CommandHandler('agregarfactura', comandos.agregarfactura_command))

    # Comandos "secretos"(no figuran en la lista de comandos del bot)
    app.add_handler(CommandHandler('registrarusuarix', comandos.registrarusuarix_command))
    app.add_handler(CommandHandler('chatid', comandos.chatid_command))


    #Callbacks(botones apretados y demás)
    app.add_handler(CallbackQueryHandler(comandos.procesar_boton_despejar))
    
    # Mensajes comunes
    app.add_handler(MessageHandler(filters.TEXT, check_message))

    # Error
    app.add_error_handler(error)

    #Inicializando polling (chequeo de updates)
    print("Polleando...")
    app.run_polling(poll_interval=1)
