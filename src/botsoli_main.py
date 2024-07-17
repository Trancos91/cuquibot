import datetime
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, Defaults, CallbackQueryHandler, PollAnswerHandler)
from src.respuestas import Respuestas
from src.pysolidaridad import EditorSheet

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text('Holi, soy el Cuquibot, miau!'
        ' Escribí "/help" para ver los comandos disponibles :3')
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = ('A implementar nya')

    await update.message.reply_text(mensaje)

async def arrancar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función de debug para probar el run_repeating.
    Esto se podría borrar"""
    due = 2
    chat_id = update.effective_message.chat_id
    context.application.job_queue.run_repeating(enviar_mensaje, due, first=2, last=12, chat_id=chat_id, name=str(chat_id), data="mensaje de prueba")
    await update.effective_message.reply_text('Arrancando mensajitos')

async def encuesta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función de debug para crear artificialmente una encuesta y
    probar los updates relacionados a la misma"""
    context.application.job_queue.run_once(crearencuesta, 2, chat_id=update.message.chat_id)

async def cerrar_encuesta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función de debug para cerrar la encuesta creada artificialmente"""
    context.application.job_queue.run_once(cerrar_encuesta, 2, chat_id=update.message.chat_id)

async def despejarasistentes_command(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirma si borrar asistentes de la hoja"""
    keyboard = [
    [InlineKeyboardButton("🚧 Despejar 🚧", callback_data=("asistentes 1"))],
    [InlineKeyboardButton("Cancelar", callback_data=("asistentes 0"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("⚠️ Segurx querés despejar la lista de asistentes? ⚠️", 
                                    reply_markup=reply_markup)

async def despejarpendientejueves_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para despejar una tarea del jueves específica"""
    editor = EditorSheet()
    args = ' '.join(context.args).replace('/despejarpendientejueves', '').strip()
    if not args:
        await update.message.reply_text("⚠️Por favor asegurate de haber incluído una tarea!⚠️\n"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return
    if editor.despejar_pendiente_jueves(args):
        await update.message.reply_text(f"Eliminada la tarea '{args}' de la "
            "lista de tareas pendientes para el jueves! 🎉")
    else:
        await update.message.reply_text(f"Disculpame, no encontré la tarea '{args}"
                                        "en la lista de tareas para el jueves 🙁")

async def despejarlistajueves_command(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirma si borrar las tareas pendientes de los jueves de la hoja"""
    keyboard = [
    [InlineKeyboardButton("🚧 Despejar 🚧", callback_data=("pendientes_jueves 1"))],
    [InlineKeyboardButton("Cancelar", callback_data=("pendientes_jueves 0"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("⚠️ Segurx querés despejar la lista de tareas pendientes del jueves? ⚠️", 
                                    reply_markup=reply_markup)

async def agregarinfo_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando para agregar información a la base de datos del sheets"""
    editor = EditorSheet()
    args = context.args
    print(f"lista_texto = {args}")
    categoría = ""
    info = args.copy()

    for palabra in args:
        if any(char in palabra for char in ["'", '"', "‘", "’", '“', '”']) :
            break
        categoría += " " + info.pop(0)
    categoría = categoría.strip()
    info = " ".join(info).strip()
    if not categoría.strip():
        await update.message.reply_text("⚠️Por favor asegurate de haber incluído una categoría!⚠️\n"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return
    elif not info.strip():
        await update.message.reply_text("⚠️Acordate de incluír la info entre comillas!⚠️\n"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return
    else:
        print(categoría)
        print(info)
        await update.message.reply_text(editor.agregarinfo(categoría, info))

async def agregarfaltantes_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    texto = update.message.text
    texto_procesado = texto.replace("/agregarfaltantes", "").strip()
    faltantes = texto_procesado.split(", ")
    if not texto_procesado:
        await update.message.reply_text("⚠️No recibí una lista de faltantes 🙁⚠️ \nAcordate "
                                        "de escribir los faltantes separados por comas!"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return

    await update.message.reply_text(editor.agregarfaltantes(faltantes))

async def agregarpendientesjueves_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    editor = EditorSheet()
    texto = update.message.text
    texto_procesado = texto.replace("/agregarpendientesjueves", "").strip()
    pendientes = texto_procesado.split(", ")
    if not texto_procesado:
        await update.message.reply_text("⚠️No recibí una lista de tareas pendientes 🙁⚠️ \nAcordate "
                                        "de escribir las tareas <em>separados por comas</em>!"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return
    await update.message.reply_text(editor.agregar_pendientes_jueves(pendientes))
     
async def definirproxima_command(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    texto = update.message.text
    comida = texto.replace("/definirproxima", "").strip()
    if not comida:
        await update.message.reply_text("⚠️No recibí ninguna comida!⚠️\n"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return

    await update.message.reply_text(editor.set_prox_comida(comida))

# Responses
def handle_message(texto: str, update: Update):
    respuesta = Respuestas(texto, update).respuestas()

    if respuesta:
        return respuesta
    else:
        print("No hubo respuesta generada")

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    texto: str = update.message.text

    print(f'Usuario {update.message.chat.id} en {message_type}: {texto}')
    if message_type == "group" or message_type == "supergroup":
        if BOT_USERNAME in texto:
            texto:str = texto.replace(BOT_USERNAME, "").strip()
            respuesta: str = handle_message(texto, update)
        else:
            return
    else:
        respuesta: str = handle_message(texto, update)
    
    print(f'Bot: {respuesta}')
    await update.message.reply_text(respuesta)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} causó error {context.error}")

# Métodos de commands

async def crearjob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función de debug para crear jobs y probar sus mensajes"""
    name = context.args[0]
    time, day, msg = Mensajes.mensajes[name]
    job = context.job_queue.run_daily(enviar_mensaje, time, day, name=name,
                            chat_id=GROUP_ID, data=msg)
    print(f"Creado el job {name}, info:")
    print(job)
    print(f"El mensaje es: {msg}")
    await update.message.reply_text(msg)

async def procesar_boton_despejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    editor = EditorSheet()
    await query.answer()

    if "asistentes" in query.data:
        if "0" in query.data:
            await query.edit_message_text(text="Ok, dejo la lista como está :)")
        elif "1" in query.data:
            despejar_asistentes(context)
            await query.edit_message_text(text="Dale, ahí despejé la lista!")
    elif "pendientes_jueves" in query.data:
        if "0" in query.data:
            await query.edit_message_text(text="Ok, dejo la lista como está :)")
        if "1" in query.data:
            despejar_pendientes_jueves(context)
            await query.edit_message_text(text="Despejada la lista de tareas pendientes de los jueves! 🙂")

#Métodos rutinarios(de Jobs)

async def crearencuesta(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Crea la encuesta de asistentes, funciona en un Job"""
    opciones = ["A cocinar de 17:00 a 20:00", "A recorrida de 20:00 a 21:30", "A ordenar y limpiar de 20:00 a 21:30"]
    mensaje = await context.bot.send_poll(context.job.chat_id, "Voy hoy a la olla:", 
                                opciones,
                                is_anonymous=False, allows_multiple_answers=True)

    payload = {
        datetime.date.today(): {
            "poll_id": mensaje.poll.id,
            "opciones": opciones,
            "id_mensaje": mensaje.message_id,
            "chat_id": context.job.chat_id
        }
    }
    context.bot_data.update(payload)

async def cerrar_encuesta(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cierra la encuesta, funciona en un Job"""
    encuesta = context.bot_data[datetime.date.today()]
    if encuesta:
        await context.bot.stop_poll(encuesta["chat_id"], encuesta["id_mensaje"])
        context.bot_data.pop(datetime.date.today())

def despejar_asistentes(context: ContextTypes.DEFAULT_TYPE):
    """Función de uso privado, no aparece en la los comandos principales.
    También está en Job semanal"""
    editor = EditorSheet()
    editor.despejar_asistentes()
    print("Despejada la lista de asistentes")

def despejar_pendientes_jueves(context: ContextTypes.DEFAULT_TYPE):
    editor = EditorSheet()
    editor.despejar_pendientes_jueves()
    print("Despejadas todas las tareas pendientes")

#Métodos generales y pasivos

async def recibir_respuesta_encuesta(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    """Recibe respuestas a la encuesta y las procesa en
    google sheets."""
    answer = update.poll_answer
    #LÍNEA DEL ERROR ABAJO
    print(answer)
    answered_poll = context.bot_data[datetime.date.today()]
    try:
        questions = answered_poll["opciones"]
    # this means this poll answer update is from an old poll, we can't do our answering then
    except KeyError:
        print("-------Pintó el error-------")
        return
    selected_options = answer.option_ids
    print(f"Las opciones votadas son: {selected_options}")
    if selected_options:
        if 0 in selected_options:
            print(f"{update.effective_user.first_name} se anotó al turno cocina")
            editor.agregarasistente(update.effective_user.first_name, editor.Turno.COCINA)
        else:
            editor.despejar_asistente(update.effective_user.first_name, editor.Turno.COCINA)
        if 1 in selected_options:
            editor.agregarasistente(update.effective_user.first_name, editor.Turno.RECORRIDA)
            print(f"{update.effective_user.first_name} se anotó al turno de recorrida")
        else:
            editor.despejar_asistente(update.effective_user.first_name, editor.Turno.RECORRIDA)
        if 2 in selected_options:
            editor.agregarasistente(update.effective_user.first_name, editor.Turno.LIMPIEZA)
            print(f"{update.effective_user.first_name} se anotó al turno de limpieza")
        else:
            editor.despejar_asistente(update.effective_user.first_name, editor.Turno.LIMPIEZA)
    else:
        editor.despejar_asistente(update.effective_user.first_name, editor.Turno.COCINA)
        editor.despejar_asistente(update.effective_user.first_name, editor.Turno.RECORRIDA)
        editor.despejar_asistente(update.effective_user.first_name, editor.Turno.LIMPIEZA)

async def enviar_mensaje(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=context.job.chat_id, text=str(context.job.data).strip())

async def recordatorio_pendientes(context: ContextTypes.DEFAULT_TYPE):
    editor = EditorSheet()
    mensaje = (
            "Holi, cómo viene ese viernes? Parece que quedaron algunas tareas pendientes"
            " en la lista de tareas para ayer. Son cosas que necesitemos hacer aún?"
            " Si no es así, pueden escribir /despejarlistajueves para eliminar la lista "
            "y arrancar la semana que viene con la hoja en blanco 🙂")
    if editor.get_pendientes_jueves:
        await context.bot.send_message(chat_id=context.job.chat_id, text=mensaje)
    else:
        return

#Métodos de inicialización

def inicializar_jobs(app):
    """Inicializa todos los Jobs"""

    app.job_queue.run_daily(crearencuesta, 
                            datetime.time(12, 30, 2),
                            (3, ), name="encuesta_semanal",
                            chat_id=GROUP_ID)

    app.job_queue.run_daily(cerrar_encuesta, 
                            datetime.time(23, 30, 0),
                            (4, ), name="cerrar_encuesta_semanal",
                            chat_id=GROUP_ID)

    app.job_queue.run_daily(despejar_asistentes, 
                            datetime.time(23, 31, 0),
                            (4, ), name="despejar_asistentes",
                            chat_id=GROUP_ID)
    
    app.job_queue.run_daily(despejar_pendientes_jueves, 
                            datetime.time(23, 31, 0),
                            (4, ), name="despejar_pendientes_jueves",
                            chat_id=GROUP_ID)

    app.job_queue.run_daily(recordatorio_pendientes,
                            datetime.time(12, 0, 0),
                            (4, ), name="recordatorio_pendientes",
                            chat_id=GROUP_ID)

    inicializar_jobs_mensajes(app)

    joblist = [x.name for x in app.job_queue.jobs()]
    print(f"Inicializado Jobqueues: {joblist}")
    print(f"Chat_id de jobqueue(1): {app.job_queue.get_jobs_by_name("encuesta_semanal")[0].chat_id}")

def inicializar_jobs_mensajes(app):
    for key, value in Mensajes.mensajes.items():
        name = key
        time, day, msg = value
        app.job_queue.run_daily(enviar_mensaje, time, day, name=name,
                                chat_id=GROUP_ID, data=msg)

class Mensajes :
    """Colección de mensajes a ser asignados a jobs al inicializar
    el bot. Inicializados mediante 'inicializar_jobs_mensajes()'"""
    editor = EditorSheet()
    mensajes = {
        "recordatorio_cocina": (datetime.time(18, 0, 0), (4, ),
            "Holi! No se olivden de definir qué vamos a cocinar la semana que viene!"
            "Cuando lo hagan, si les parece, escriban /definirproxima y la comida para dejar"
            " definido qué preparamos la semana que viene. Gracias! :)"),

        "mensaje_encuesta": (datetime.time(12, 30, 0), (3, ),
            "Hola pipis, acá les mando la encuesta de la semana para ir"
            " definiendo quiénes somos en qué turnos mañana 🧑‍🍳"),

        "jueves_mañana": (datetime.time(11, 0, 0), (4, ), 
            "Wendi! Feliz jueves! Recuerden avisar en la encuesta si vienen hoy, si no lo hicieron."
            " Si no, también pueden enviar un mensaje etiquetándome(con la @)"
            " y escribiendo algo como 'voy cocina', 'voy reco' o 'voy limpieza' :)\n"
            f"No olviden de que hoy nos toca cocinar {editor.get_prox_comida()}. " 
            "Tenemos todo lo que necesitamos?"),

        "recordatorio_cierre": (datetime.time(19, 45, 0), (4, ),
            "Chiques que se hayan quedado a limpiar, les alcanzo una lista "
            "de tareas comunes a la hora de dejar ordenada La Ronda, "
            "así no colgamos por error con nada :) \n" + editor.get_info("cierre")),
    }

if __name__ == '__main__':

    #Definiendo constantes
    with open("secretos/tg_API.txt", "r", encoding="ascii") as file:
        TOKEN = str(file.read().strip())
    with open("secretos/bot_user.txt", "r", encoding="ascii") as file:
        BOT_USERNAME = str(file.read().strip())
    with open("secretos/group_id.txt", "r", encoding="ascii") as file:
        GROUP_ID = int(file.read().strip())

    #Definiendo configuración por defecto del bot
    defaults = Defaults(parse_mode="HTML", tzinfo=timezone("America/Argentina/Buenos_Aires"))
    print("Inicializando bot")
    print(f"Hora actual: {datetime.datetime.now(timezone("America/Argentina/Buenos_Aires"))}")
    app = Application.builder().token(TOKEN).defaults(defaults).build()

    #Inicializando Jobs
    inicializar_jobs(app)

    # Comandos
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler(('despejar', 'despejarasistentes'), despejarasistentes_command))
    app.add_handler(CommandHandler('agregarinfo', agregarinfo_command))
    app.add_handler(CommandHandler('agregarfaltantes', agregarfaltantes_command))
    app.add_handler(CommandHandler('definirproxima', definirproxima_command))
    app.add_handler(CommandHandler('despejarpendientejueves', despejarpendientejueves_command))
    app.add_handler(CommandHandler('despejarlistajueves', despejarlistajueves_command))
    app.add_handler(CommandHandler('agregarpendientesjueves', agregarpendientesjueves_command))

    #COMANDOS DE DEBUG
    app.add_handler(CommandHandler('arrancar', arrancar_command))
    app.add_handler(CommandHandler('encuesta', encuesta_command))
    app.add_handler(CommandHandler('cerrar_encuesta', cerrar_encuesta_command))
    app.add_handler(CommandHandler('crearjob', crearjob))


    #Callbacks(botones apretados y demás)
    app.add_handler(CallbackQueryHandler(procesar_boton_despejar))
    
    #Respuesta a encuesta
    app.add_handler(PollAnswerHandler(recibir_respuesta_encuesta))
    
    # Mensajes comunes
    app.add_handler(MessageHandler(filters.TEXT, check_message))

    # Error
    app.add_error_handler(error)

    #Inicializando polling (chequeo de updates)
    print("Polleando...")
    app.run_polling(poll_interval=1)
