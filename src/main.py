import datetime
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, Defaults, CallbackQueryHandler, PollAnswerHandler)
from modulos.editor import EditorSheet
from modulos.respuestas import Respuestas


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text('Holi, soy el Cuquibot, miau!'
        ' Escribí "/help" para ver los comandos disponibles :3')
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = ('A implementar nya')

    await update.message.reply_text(mensaje)

async def agregartareas_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    texto = update.message.text
    texto_procesado = texto.replace("/agregartareas", "").strip()
    tareas = texto_procesado.split(", ")
    if not texto_procesado:
        await update.message.reply_text("⚠️No recibí una lista de tareas 🙁⚠️ \nAcordate "
                                        "de escribir las tareas separadas por comas!"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return

    await update.message.reply_text(editor.agregar_tareas(tareas))

async def agregarcompras_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    texto = update.message.text
    texto_procesado = texto.replace("/agregarcompras", "").strip()
    texto_lista = texto_procesado.split()
    categoría = texto_lista.pop(0)
    texto_procesado = " ".join(texto_lista)
    compras = [compra.strip() for compra in texto_procesado.split(",")]
    if not compras:
        await update.message.reply_text("⚠️No recibí una lista de compras 🙁⚠️ \nAcordate "
                                        "de escribir las compras separadas por comas!"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return
    match categoría:
        case "diarias":
            categoría = editor.CategoríaCompras.DIARIAS
        case "mensuales":
            categoría = editor.CategoríaCompras.MENSUALES
        case "juanito":
            categoría = editor.CategoríaCompras.JUANITO

    await update.message.reply_text(editor.agregar_compras(categoría, compras))

async def despejartareas_command(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirma si borrar asistentes de la hoja"""
    keyboard = [
    [InlineKeyboardButton("🚧 Despejar 🚧", callback_data=("tareas 1"))],
    [InlineKeyboardButton("Cancelar", callback_data=("tareas 0"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("⚠️ Segurx querés despejar la lista de tareas? ⚠️", 
                                    reply_markup=reply_markup)

async def despejarcompras_command(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) > 1:
        await update.message.reply_text("Por favor ingresá 'diarias', 'mensuales' o 'juanito'"
                                        " para indicar qué lista querés despejar.\n"
                                        "Sólo se puede despejar una por vez.")
    compra = context.args[0].strip().lower()
    match compra:
        case ("diarias" | "mensuales" | "juanito"):
            pass
        case _:
            await update.message.reply_text("Por favor aclará 'diarias', "
                                            "'mensuales' o 'juanito para definir "
                                            "la lista a despejar :)")
            return

    """Confirma si borrar asistentes de la hoja"""
    keyboard = [
    [InlineKeyboardButton("🚧 Despejar 🚧", callback_data=(f"{compra} 1"))],
    [InlineKeyboardButton("Cancelar", callback_data=(f"{compra} 0"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f"⚠️ Segurx querés despejar la lista de compras? ⚠️", 
                                    reply_markup=reply_markup)

async def despejarunatarea_command(update:Update,
                                    context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    args = ' '.join(context.args).replace('/despejarunatarea', '').strip()
    if not args:
        await update.message.reply_text("⚠️Por favor asegurate de haber incluído una tarea!⚠️\n"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return
    if editor.despejar_tarea(args):
        await update.message.reply_text(f"Eliminada la tarea '{args}' de la "
            "lista de tareas pendientes para el jueves! 🎉")
    else:
        await update.message.reply_text(f"Disculpame, no encontré la tarea '{args}"
                                        "en la lista de tareas para el jueves 🙁")

async def despejarunacompra_command(update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):
    editor = EditorSheet()
    categoría = context.args.pop(0)
    args = ' '.join(context.args).replace('/despejarunacompra', '').strip()
    match categoría:
        case "diarias":
            categoría = editor.CategoríaCompras.DIARIAS
        case "mensuales":
            categoría = editor.CategoríaCompras.MENSUALES
        case "juanito":
            categoría = editor.CategoríaCompras.JUANITO
        case _:
            await update.message.reply_text("Por favor aclará 'diarias', "
                                            "'mensuales' o 'juanito para definir "
                                            "la lista a despejar :)")
            return
    if not args:
        await update.message.reply_text("⚠️Por favor asegurate de haber incluído un ítem a comprar!⚠️\n"
                                        " Si usaste este comando tocando del menú, "
                                        "procurá tocar la flechita \u2199 a la derecha"
                                        " del comando en vez "
                                        "del comando en sí :)")
        return
    if editor.despejar_compra(args, categoría):
        await update.message.reply_text(f"Eliminado el ítem '{args}' de la "
            "lista de tareas pendientes para el jueves! 🎉")
    else:
        await update.message.reply_text(f"Disculpame, no encontré el ítem '{args}"
                                        "en la lista de tareas para el jueves 🙁")

# Respuestas
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

# Métodos pasivos

async def enviar_mensaje(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=context.job.chat_id, text=str(context.job.data).strip())

async def recordatorio_pendientes(context: ContextTypes.DEFAULT_TYPE):
    editor = EditorSheet()
    mensaje = (
            "Holi, cómo viene ese viernes? Parece que quedaron algunas tareas pendientes"
            " en la lista de tareas de la semana pasada. Son cosas que necesitemos hacer aún?"
            " Si no es así, pueden escribir /despejarlistatareas para eliminar la lista "
            "y arrancar la semana que viene con la hoja en blanco 🙂")
    if editor.get_pendientes_jueves:
        await context.bot.send_message(chat_id=context.job.chat_id, text=mensaje)
    else:
        return

async def procesar_boton_despejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    editor = EditorSheet()
    await query.answer()

    if "diarias" in query.data:
        if "0" in query.data:
            await query.edit_message_text(text="Ok, dejo la lista como está :)")
        elif "1" in query.data:
            editor.despejar_compras(editor.CategoríaCompras.DIARIAS)
            await query.edit_message_text(text="Dale, ahí despejé la lista!")
    if "mensuales" in query.data:
        if "0" in query.data:
            await query.edit_message_text(text="Ok, dejo la lista como está :)")
        elif "1" in query.data:
            editor.despejar_compras(editor.CategoríaCompras.MENSUALES)
            await query.edit_message_text(text="Dale, ahí despejé la lista!")
    elif "juanito" in query.data:
        if "0" in query.data:
            await query.edit_message_text(text="Ok, dejo la lista como está :)")
        if "1" in query.data:
            editor.despejar_compras(editor.CategoríaCompras.JUANITO)
            await query.edit_message_text(text="Dale, ahí despejé la lista!")
    elif "tareas" in query.data:
        if "0" in query.data:
            await query.edit_message_text(text="Ok, dejo la lista como está :)")
        if "1" in query.data:
            editor.despejar_tareas()
            await query.edit_message_text(text="Despejada la lista de tareas! 🙂")


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} causó error {context.error}")

#Métodos de inicialización

def inicializar_jobs(app):
    """Inicializa todos los Jobs"""

    app.job_queue.run_daily(recordatorio_pendientes,
                            datetime.time(12, 0, 0),
                            (4, ), name="recordatorio_pendientes",
                            chat_id=GROUP_ID)

    inicializar_jobs_mensajes(app)

    joblist = [x.name for x in app.job_queue.jobs()]
    print(f"Inicializado Jobqueues: {joblist}")

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
        "nombre_referencia": (datetime.time(18, 0, 0), (4, ),
            "Texto de referencia"),
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
    app.add_handler(CommandHandler('agregartareas', agregartareas_command))
    app.add_handler(CommandHandler('agregarcompras', agregarcompras_command))
    app.add_handler(CommandHandler('despejarcompras', despejarcompras_command))
    app.add_handler(CommandHandler('despejartareas', despejartareas_command))
    app.add_handler(CommandHandler('despejarunatarea', despejarunatarea_command))
    app.add_handler(CommandHandler('despejarunacompra', despejarunacompra_command))

    #COMANDOS DE DEBUG


    #Callbacks(botones apretados y demás)
    app.add_handler(CallbackQueryHandler(procesar_boton_despejar))
    
    # Mensajes comunes
    app.add_handler(MessageHandler(filters.TEXT, check_message))

    # Error
    app.add_error_handler(error)

    #Inicializando polling (chequeo de updates)
    print("Polleando...")
    app.run_polling(poll_interval=1)
