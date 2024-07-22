import datetime
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, Defaults, CallbackQueryHandler, PollAnswerHandler)
from unidecode import unidecode
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
    args = context.args
    tareas = procesar_parámetros(args, 1)
    error = chequear_contenido_parámetros(tareas, 1)
    if error:
        await update.message.reply_text(error)
    else:
        await update.message.reply_text(editor.agregar_ítems(tareas))

async def agregarcompras_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    #texto = update.message.text
    #texto_procesado = texto.replace("/agregarcompras", "").replace(BOT_USERNAME, "").strip().lower()
    #if not texto_procesado:
    #    await update.message.reply_text("⚠️No recibí una lista de compras ni una categoría 🙁⚠️ \nAcordate "
    #                                    "de escribir las compras separadas por comas!"
    #                                    " Si usaste este comando tocando del menú, "
    #                                    "procurá tocar la flechita \u2199 a la derecha"
    #                                    " del comando en vez "
    #                                    "del comando en sí :)")
    #    return
    #texto_lista = texto_procesado.split()
    #categoría = unidecode(texto_lista.pop(0))
    #texto_procesado = " ".join(texto_lista)
    #compras = [compra.strip() for compra in texto_procesado.split(",")]
    #if not compras:
    #    await update.message.reply_text("⚠️No recibí una lista de compras 🙁⚠️ \nAcordate "
    #                                    "de escribir las compras separadas por comas!"
    #                                    " Si usaste este comando tocando del menú, "
    #                                    "procurá tocar la flechita \u2199 a la derecha"
    #                                    " del comando en vez "
    #                                    "del comando en sí :)")
    #    return
    args = context.args
    procesados = procesar_parámetros(args, 2)
    error = chequear_contenido_parámetros(procesados, 2)
    if error:
        print("Hay error")
        await update.message.reply_text(error)
        return
    if procesados:
        categoría, compras = procesados
    match categoría:
        case "supermercado":
            categoría_compras = editor.CategoríaCompras.SUPERMERCADO
        case "verduleria":
            categoría_compras = editor.CategoríaCompras.VERDULERIA
        case "mensuales":
            categoría_compras = editor.CategoríaCompras.MENSUALES
        case "juanito":
            categoría_compras = editor.CategoríaCompras.JUANITO
        case _:
            await update.message.reply_text("No encontré la lista :(")
            return

    await update.message.reply_text(editor.agregar_ítems(compras, categoría=categoría_compras))

async def registrarviveres_command(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    args = context.args
    ítems = procesar_parámetros(args, 1)
    error = chequear_contenido_parámetros(ítems, 1)
    if error:
        print("Hay error")
        await update.message.reply_text(error)
        return
    else:
        await update.message.reply_text(editor.agregar_ítems(ítems, 1))


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
    args = context.args
    compra = procesar_parámetros(args, 0)
    error = chequear_contenido_parámetros(compra, 0)
    if error:
        await update.message.reply_text(error)
        return
    match compra:
        case ("diarias" | "verduleria" | "supermercado"| "mensuales" | "juanito"):
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
    args = context.args
    tarea = procesar_parámetros(args, 4)
    error = chequear_contenido_parámetros(tarea, 1)
    if error:
        await update.message.reply_text(error)
        return
    if editor.despejar_tarea(tarea):
        await update.message.reply_text(f"Eliminada la tarea '{tarea}' de la "
            "lista de tareas pendientes para el jueves! 🎉")
    else:
        await update.message.reply_text(f"Disculpame, no encontré la tarea '{tarea}"
                                        "en la lista de tareas para el jueves 🙁")

async def despejarunacompra_command(update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):
    editor = EditorSheet()
    args = context.args
    procesado = procesar_parámetros(args, 3)
    error = chequear_contenido_parámetros(procesado, 2)
    if error:
        await update.message.reply_text(error)
        return
    categoría, ítem = procesado
    async def procesar_diarias():
        categoría_diarias = editor.CategoríaCompras.SUPERMERCADO
        if editor.despejar_compra(ítem, categoría_diarias):
            await update.message.reply_text(f"Eliminado el ítem '{ítem}' de la "
                f"lista de compras {categoría_diarias.value[1]}! 🎉")
            return
        else:
            categoría_diarias = editor.CategoríaCompras.VERDULERIA
            if editor.despejar_compra(args, categoría_diarias):
                await update.message.reply_text(f"Eliminado el ítem '{ítem}' de la "
                    f"lista de compras {categoría_diarias.value[1]}! 🎉")
                return
            else:
                await update.message.reply_text(f"Disculpame, no encontré el ítem '{ítem}' "
                                                f"en la lista de compras {categoría_diarias.value[1]} 🙁")
                return

    match categoría:
        case "diarias":
            print("Categoría matcheó con 'diarias'")
            await procesar_diarias()
            return
        case ("super" | "supermercado" | "chino"):
            categoría_compras = editor.CategoríaCompras.SUPERMERCADO
        case ("verdu" | "verdulería" | "verduras" | "frutas"):
            categoría_compras = editor.CategoríaCompras.VERDULERIA
        case "mensuales":
            categoría_compras = editor.CategoríaCompras.MENSUALES
        case "juanito":
            categoría_compras = editor.CategoríaCompras.JUANITO
        case _:
            categoría_compras = None
            await update.message.reply_text("Por favor aclará 'diarias', 'supermercado', "
                                            "'verdulería', mensuales' o 'juanito para definir "
                                            "la lista a despejar :)")
            return
    if editor.despejar_compra(ítem, categoría_compras):
        await update.message.reply_text(f"Eliminado el ítem '{ítem}' de la "
            "lista seleccionada! 🎉")
    else:
        await update.message.reply_text(f"Disculpame, no encontré el ítem '{ítem}"
                                        "en la lista seleccionada 🙁")
        
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
            editor.despejar_compras(editor.CategoríaCompras.SUPERMERCADO)
            editor.despejar_compras(editor.CategoríaCompras.VERDULERIA)
            await query.edit_message_text(text="Dale, ahí despejé las listas!")
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
    if "supermercado" in query.data:
        if "0" in query.data:
            await query.edit_message_text(text="Ok, dejo la lista como está :)")
        elif "1" in query.data:
            editor.despejar_compras(editor.CategoríaCompras.SUPERMERCADO)
            await query.edit_message_text(text="Dale, ahí despejé la lista!")
    if "verduleria" in query.data:
        if "0" in query.data:
            await query.edit_message_text(text="Ok, dejo la lista como está :)")
        elif "1" in query.data:
            editor.despejar_compras(editor.CategoríaCompras.VERDULERIA)
            await query.edit_message_text(text="Dale, ahí despejé la lista!")

def procesar_parámetros(args, modo: int):
    """Toma la lista args del contexto y la parsea
    :arg modo: 
    0: sólo categoría, sin args
    1: sólo args, sin categoría
    2: categoría y args
    3: categoría y un sólo ítem
    4: un sólo ítem, sin categoría
    """
    match modo:
        case 0:
            if len(args) > 1 or not args:
                return None
            else:
                return unidecode(args[0].strip().lower())
        case 1:
            if not args:
                return None
            else:
                return [x.strip().capitalize() for x in " ".join(args).split(",")]
        case 2:
            if len(args) < 2 or not args:
                return None
            else:
                categoría = unidecode(args.pop(0).strip().lower())
                lista = [x.strip().capitalize() for x in " ".join(args).split(",")]
                return (categoría, lista)
        case 3:
            if len(args) < 2 or not args:
                return None
            else:
                categoría = unidecode(args.pop(0).strip().lower())
                ítem = " ".join(args).strip().capitalize()
                return (categoría, ítem)
        case 4:
            if not args:
                return None
            else:
                return " ".join(args).strip().capitalize()

def chequear_contenido_parámetros(parámetros, modo):
    """
    Chequea si se recibieron los argumentos apropiados y, si no, genera mensaje de error.
    :arg modo:
    0: con categoría, sin elemento/s
    1: con elemento/s, sin categoría
    2: con cateogría y elemento/s
    """
    final_genérico = (" Si usaste este comando tocando del menú, "
                        "procurá tocar la flechita \u2199 a la derecha"
                        " del comando en vez "
                        "del comando en sí :)")
    match modo:
        case 0:
            if not parámetros:
                return ("⚠️No recibí una categoría para este comando 🙁⚠️ \n" +
                        final_genérico)
        case 1:
            if not parámetros:
                return ("⚠️No recibí una lista de elementos 🙁⚠️ \nAcordate "
                        "de escribir los elementos separadas por comas!\n" + 
                        final_genérico)
        case 2:
            if not parámetros:
                return ("⚠️Me faltó recibir o una categoría o una lista de elementos 🙁⚠️ \nAcordate "
                        "de escribir una sola palabra como categoría y, después, \n"
                        "los elementos separadas por comas!\n" +
                        final_genérico)


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
    app.add_handler(CommandHandler('registrarviveres', registrarviveres_command))

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
