import datetime
import yaml
import tomlkit
import tomllib
from pytz import timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, 
    filters, ContextTypes, Defaults, CallbackQueryHandler, PollAnswerHandler)
from unidecode import unidecode
from modulos.editor import EditorSheet
from modulos.respuestas import Respuestas
from modulos.decoradores import requiere_usuarix
from modulos.mensajes import Mensajes


##########################################################################
# Comandos
##########################################################################
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(Mensajes.START.value)

    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (Mensajes.HELP.value)

    await update.message.reply_text(mensaje)

async def registrarusuarix_command(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Necesito que me des como primera palabra la contraseña,"
                                    " y después cómo querés que te diga, en ese orden!\n"
                                "Por ejemplo: /registrarusuarix contraseña apodo de varias palabras")
        return
    contraseña = args.pop(0)
    alias = " ".join(args)
    first_name = str(update.message.from_user.first_name)
    id = str(update.message.from_user.id)

    async def chequear_duplicado(dicc_users, nick):
        for id in dicc_users:
            if nick == dicc_users[id]["alias"]:
                await update.message.reply_text("Disculpá, ese alias ya lo tiene otra persona!")
                return True

    if contraseña == PASSWD:
        with open("secretos/config.toml", "r") as file:
            config = tomlkit.load(file)
        if await chequear_duplicado(config["users"], alias):
            return
        config["users"][id] = {}
        config["users"][id]["first_name"] = first_name
        config["users"][id]["alias"] = alias
        with open("secretos/config.toml", "w") as file:
            tomlkit.dump(config, file)
        await update.message.reply_text(f"Registradx lx usuarix {update.message.from_user.first_name}"
                    f" de id {update.message.from_user.id} bajo el alias {alias}! 😺")
    else:
        mensaje = (
            "Alguien escribió la contraseña equivocada.\n"
            f"ID: {update.message.from_user.id}\n"
            f"Nick: {update.message.from_user.first_name}\n"
            f"Usuario: {update.message.from_user.username}\n"
            f"Es bot: {update.message.from_user.is_bot}\n"
            f"Código de lenguaje: {update.message.from_user.language_code}"
        )
        print(mensaje)
        await update.message.reply_text("La contraseña que escribiste es incorrecta!")


async def groupid_command(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando de configuración para obtener fácilmente el group ID"""
    message_type: str = update.message.chat.type

    if message_type == "group" or message_type == "supergroup":
        await update.message.reply_text(f"El ID de tu grupo es:\n{update.message.chat_id}")
    else:
        await update.message.reply_text("Parece que este comando no lo escribiste en el grupo! 😿")

@requiere_usuarix
async def agregartareas_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

    editor = EditorSheet()
    args = context.args
    tareas = procesar_parámetros(args, 1)
    if error := chequear_contenido_parámetros(tareas, 1):
        await update.message.reply_text(error)
    else:
        await update.message.reply_text(editor.agregar_ítems(tareas))

@requiere_usuarix
async def agregarcompras_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

    editor = EditorSheet()
    args = context.args
    procesados = procesar_parámetros(args, 2)
    if error := chequear_contenido_parámetros(procesados, 2):
        await update.message.reply_text(error)
        return
    else:
        categoría, compras = procesados

    if categoría_obj := chequear_categoría_compras(categoría):
        categoría_compras = categoría_obj
    else:
        await update.message.reply_text("No encontré la lista :(")
        return

    await update.message.reply_text(editor.agregar_ítems(compras, categoría=categoría_compras))

@requiere_usuarix
async def registrarviveres_command(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE) -> None:
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

    editor = EditorSheet()
    args = context.args
    ítems = procesar_parámetros(args, 1)
    if error := chequear_contenido_parámetros(ítems, 1):
        await update.message.reply_text(error)
        return
    else:
        await update.message.reply_text(editor.agregar_ítems(ítems, 1))


@requiere_usuarix
async def despejarlistatareas_command(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

    """Confirma si borrar asistentes de la hoja"""
    keyboard = [
    [InlineKeyboardButton("🚧 Despejar 🚧", callback_data=("tareas 1"))],
    [InlineKeyboardButton("Cancelar", callback_data=("tareas 0"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("⚠️ Segurx querés despejar la lista de tareas? ⚠️", 
                                    reply_markup=reply_markup)

@requiere_usuarix
async def despejarcompras_command(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

    editor = EditorSheet()
    args = context.args
    procesados = procesar_parámetros(args, 2)
    if error := chequear_contenido_parámetros(procesados, 2):
        await update.message.reply_text(error)
        return
    else:
        categoría, compras = procesados

    if categoría_obj := chequear_categoría_compras(categoría):
        categoría_compras = categoría_obj
    else:
        await update.message.reply_text("No encontré la lista :(")
        return

    mensaje = editor.despejar_compras(compras, categoría=categoría_compras)
    if not mensaje:
        mensaje = f"Disculpame, no encontré los ítems "
        mensaje += ", ".join(compras)
        mensaje += " en la lista seleccionada 🙁"

    await update.message.reply_text(mensaje)

@requiere_usuarix
async def despejarlistacompras_command(update:Update,
                                       context: ContextTypes.DEFAULT_TYPE) -> None:
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

    args = context.args
    compra = procesar_parámetros(args, 0)
    if error := chequear_contenido_parámetros(compra, 0):
        await update.message.reply_text(error)
        return
    lista_respuestas = Respuestas("nada", update).lista_compras
    lista_compuesta = [palabra for lista in lista_respuestas.values() for palabra in lista]
    lista_compuesta.append("diarias")
    if not any(compra == palabra for palabra in lista_compuesta):
        await update.message.reply_text("Por favor aclará 'diarias', "
                                        "'mensuales', 'super', 'juanito', 'varias', 'verdulería' o 'farmacia' "
                                        "para definir la lista a despejar :)")
        return

    """Confirma si borrar asistentes de la hoja"""
    keyboard = [
    [InlineKeyboardButton("🚧 Despejar 🚧", callback_data=(f"{compra} 1"))],
    [InlineKeyboardButton("Cancelar", callback_data=(f"{compra} 0"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(f"⚠️ Segurx querés despejar la lista de compras? ⚠️", 
                                    reply_markup=reply_markup)

@requiere_usuarix
async def despejarunatarea_command(update:Update,
                                    context: ContextTypes.DEFAULT_TYPE) -> None:
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

    args = context.args
    tarea = procesar_parámetros(args, 4)
    if error := chequear_contenido_parámetros(tarea, 1):
        await update.message.reply_text(error)
        return
    if mensaje := EditorSheet().despejar_tarea(tarea):
        await update.message.reply_text(mensaje)
    else:
        await update.message.reply_text(f"Disculpame, no encontré la tarea '{tarea}' "
                                        "en la lista de tareas 🙁")

@requiere_usuarix
async def despejarunacompra_command(update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

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
        mensaje = editor.despejar_compra(ítem, categoría_diarias)
        if mensaje:
            await update.message.reply_text(mensaje)
            return
        else:
            categoría_diarias = editor.CategoríaCompras.VERDULERIA
            mensaje = editor.despejar_compra(ítem, categoría_diarias)
            if mensaje:
                await update.message.reply_text(mensaje)
                return
            else:
                await update.message.reply_text(f"Disculpame, no encontré el ítem '{ítem}' "
                                                f"en la lista de compras {categoría_diarias.value[1]} 🙁")
                return

    if categoría == "diarias":
        await procesar_diarias()
        return
    elif categoría_obj := chequear_categoría_compras(categoría):
        categoría_compras = categoría_obj
    else:
        categoría_compras = None
        await update.message.reply_text("Por favor aclará 'diarias', 'supermercado', "
                                        "'verdulería', 'mensuales', 'varias' o 'juanito para definir "
                                        "la lista a despejar :)")
        return

    mensaje = editor.despejar_compra(ítem, categoría_compras)
    if mensaje:
        await update.message.reply_text(mensaje)
    else:
        await update.message.reply_text(f"Disculpame, no encontré el ítem '{ítem}"
                                        "en la lista seleccionada 🙁")
        
@requiere_usuarix
async def despejarregistrado_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    await update.message.reply_text(error)
    #    return

    args = context.args
    procesado = procesar_parámetros(args, 4)
    mensaje = EditorSheet().despejar_registrado(procesado)
    await update.message.reply_text(mensaje)

##########################################################################
# Respuestas
##########################################################################
def handle_message(texto: str, update: Update):
    #Chequea si usó el comando un usuarix registradx
    #if error := chequear_usuarix(update):
    #    return error

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
        if BOT_USERNAME in texto:
            print(f'Usuario {update.effective_user.id} en {update.message.chat_id}: {texto}')
            texto:str = texto.replace(BOT_USERNAME, "").strip()
            respuesta: str = handle_message(texto, update)
        else:
            return
    else:
        print(f'Usuario {update.effective_user.id} en {update.message.chat_id}: {texto}')
        respuesta: str = handle_message(texto, update)
    
    print(f'Bot: {respuesta}')
    await update.message.reply_text(respuesta)

##########################################################################
# Métodos pasivos
##########################################################################
async def enviar_mensaje_jobs(context: ContextTypes.DEFAULT_TYPE):
    """Enviar un mensaje desde un Job"""
    await context.bot.send_message(chat_id=context.job.chat_id, text=str(context.job.data).strip())


async def recordatorios_quehaceres(context: ContextTypes.DEFAULT_TYPE):
    """
    Revisa si pasó el tiempo apropiado en el recordatorio, y si sí, envía un mensaje
    recordándolo y registra la fecha. También revisa si pasó el tiempo 'snooze'
    desde la última vez que lo hizo.
    """
    recordatorio_key = context.job.data[0]
    recordatorio_value = context.job.data[1]
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
        RECORDATORIOS["recordatorios_quehaceres"][recordatorio_key] = recordatorio_value
        with open("secretos/recordatorios.yaml", "w") as file:
            yaml.safe_dump(RECORDATORIOS, file, indent=2, allow_unicode=True)

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

async def procesar_boton_despejar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Función que recibe un string de argumentos enviado por los Inline Keyboards (en este bot,
    particularmente, los de confirmación de despejar listas) y llama a la función adecuada.
    """
    query = update.callback_query
    args = [x.strip() for x in query.data.split()]
    categoría = args[0]
    respuesta = args[1]

    if "0" == respuesta:
        mensaje = "Ok, dejo la lista como está :)"
    elif "1" == respuesta:
        # Si es diarias, que combina varias categorías y por lo tanto no funciona con los algoritmos
        # comunes:
        if "diarias" == categoría:
            editor = EditorSheet()
            editor.despejar_lista_compras(editor.CategoríaCompras.SUPERMERCADO)
            editor.despejar_lista_compras(editor.CategoríaCompras.VERDULERIA)
            mensaje = "Dale, ahí despejé las listas!"
        # Si es cualquier categoría de la lista de categorías, obtiene su objeto de categoría
        # de CategoríaCompras
        elif categoría_obj := chequear_categoría_compras(categoría):
            EditorSheet().despejar_lista_compras(categoría_obj)
            mensaje = "Dale, ahí despejé la lista!"
        elif "tareas" == categoría:
            EditorSheet().despejar_lista_tareas()
            mensaje = "Despejada la lista de tareas! 🙂"
        else:
            mensaje = "Algo falló, no recibí una categoría apropiada. Pedile a Juan que se fije"
    else:
        mensaje = "Algo falló, no recibí una categoría apropiada. Pedile a Juan que se fije"

    await query.answer()
    await query.edit_message_text(text = mensaje)


##########################################################################
# Métodos auxiliares
##########################################################################
def procesar_parámetros(args, modo: int):
    """
    Toma la lista args del contexto y la parsea
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
                return unidecode(args[0]).strip().lower()
        case 1:
            if not args:
                return None
            else:
                return [x.strip().capitalize() for x in " ".join(args).split(",")]
        case 2:
            if len(args) < 2 or not args:
                return None
            else:
                categoría = unidecode(args.pop(0)).strip().lower()
                lista = [x.strip().capitalize() for x in " ".join(args).split(",")]
                return (categoría, lista)
        case 3:
            if len(args) < 2 or not args:
                return None
            else:
                categoría = unidecode(args.pop(0)).strip().lower()
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

def chequear_categoría_compras(categoría: str):
    """Itera sobre  las listas de palabras de cada categoría clave(presentes en listas_compras
    del módulo de Respuestas) y extrae la CategoríaCompras correspondiente"""
    lista_palabras = Respuestas("", None).lista_compras
    categoría = categoría.strip()
    for key in lista_palabras:
        if categoría in lista_palabras[key]:
            categoría = key.upper()
            categoría_obj = getattr(EditorSheet.CategoríaCompras, categoría)
            return categoría_obj

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} causó el siguiente error: \n{context.error}")

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
    #if Mensajes.mensajes:
    #    for key, value in Mensajes.mensajes.items():
    #        name = key
    #        time, day, msg = value
    #        app.job_queue.run_daily(enviar_mensaje_jobs, time, day, name=name,
    #                                chat_id=GROUP_ID, data=msg)

    for recordatorio in RECORDATORIOS["recordatorios_diarios"].items():
        app.job_queue.run_daily(enviar_mensaje_jobs, datetime.time(*recordatorio[1]["horario"]),
                                name=recordatorio[0], chat_id=GROUP_ID,
                                data=recordatorio[1]["mensaje"], job_kwargs={"misfire_grace_time": None})

def inicializar_jobs_recordatorios(app):
    """
    Itera sobre los recordatorios registrados en el yaml recordatorios.yaml bajo
    la categoría "recordatorios_quehaceres" y los registra en jobs con los parámetros
    apropiados.
    """
    for recordatorio in RECORDATORIOS["recordatorios_quehaceres"].items():
        app.job_queue.run_daily(recordatorios_quehaceres, datetime.time(12, 0, 0),
                                name=recordatorio[0], chat_id=GROUP_ID,
                                data=recordatorio, job_kwargs={"misfire_grace_time": None})

#class Mensajes :
#    """Colección de mensajes a ser asignados a jobs al inicializar
#    el bot. Inicializados mediante 'inicializar_jobs_mensajes_diarios()'"""
#    editor = EditorSheet()
#    mensajes = {
#        #"nombre_referencia": (datetime.time(18, 0, 0), (4, ),
#        #    "Texto de referencia"),
#    }

if __name__ == '__main__':

    #Definiendo constantes
    with open("secretos/config.toml", "rb") as file:
        config = tomllib.load(file)
        TOKEN = config["telegram"]["tg_api"]
        BOT_USERNAME = config["telegram"]["bot_user"]
        GROUP_ID = config["telegram"]["group_id"]
        PASSWD = config["telegram"]["passwd"]
    with open("secretos/recordatorios.yaml", "rb") as file:
        RECORDATORIOS = yaml.safe_load(file)

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
    app.add_handler(CommandHandler('registrarusuarix', registrarusuarix_command))
    app.add_handler(CommandHandler('groupid', groupid_command))
    app.add_handler(CommandHandler('agregartareas', agregartareas_command))
    app.add_handler(CommandHandler('agregarcompras', agregarcompras_command))
    app.add_handler(CommandHandler('despejarcompras', despejarcompras_command))
    app.add_handler(CommandHandler('despejarlistatareas', despejarlistatareas_command))
    app.add_handler(CommandHandler('despejarunatarea', despejarunatarea_command))
    app.add_handler(CommandHandler('despejarunacompra', despejarunacompra_command))
    app.add_handler(CommandHandler('despejarlistacompras', despejarlistacompras_command))
    app.add_handler(CommandHandler('registrarviveres', registrarviveres_command))
    app.add_handler(CommandHandler('despejarregistrado', despejarregistrado_command))

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
