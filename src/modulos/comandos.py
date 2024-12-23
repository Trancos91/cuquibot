import tomlkit
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from unidecode import unidecode
import modulos.config as config
from modulos.editor import EditorSheet
from modulos.respuestas import Respuestas
from modulos.decoradores import requiere_usuarix, logea
from modulos.mensajes import Mensajes


##########################################################################
# Comandos
##########################################################################
@logea
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(Mensajes.START.value)

    
@logea
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (Mensajes.HELP.value)

    await update.message.reply_text(mensaje)

@logea
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

    with open("secretos/config.toml", "r") as file:
        config = tomlkit.load(file)
    PASSWD = config["telegram"]["passwd"]
    if contraseña == PASSWD:
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


@logea
async def chatid_command(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando de configuración para obtener fácilmente el ID del chat"""
    message_type: str = update.message.chat.type

    if message_type == "group" or message_type == "supergroup":
        await update.message.reply_text(f"El ID de tu grupo es:\n{update.message.chat_id}")
    else:
        await update.message.reply_text(f"El ID del chat es:\n{update.message.chat_id}")

@requiere_usuarix
@logea
async def agregartareas_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    args = context.args
    tareas = procesar_parámetros(args, 1)
    if error := chequear_contenido_parámetros(tareas, 1):
        await update.message.reply_text(error)
    else:
        await update.message.reply_text(editor.agregar_ítems(tareas))

@requiere_usuarix
@logea
async def agregarcompras_command(update: Update,
                              context: ContextTypes.DEFAULT_TYPE) -> None:
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
@logea
async def registrarviveres_command(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE) -> None:
    editor = EditorSheet()
    args = context.args
    ítems = procesar_parámetros(args, 1)
    if error := chequear_contenido_parámetros(ítems, 1):
        await update.message.reply_text(error)
        return
    else:
        await update.message.reply_text(editor.agregar_ítems(ítems, 1))


@requiere_usuarix
@logea
async def despejarlistatareas_command(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirma si borrar asistentes de la hoja"""
    keyboard = [
    [InlineKeyboardButton("🚧 Despejar 🚧", callback_data=("tareas 1"))],
    [InlineKeyboardButton("Cancelar", callback_data=("tareas 0"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("⚠️ Segurx querés despejar la lista de tareas? ⚠️", 
                                    reply_markup=reply_markup)

@requiere_usuarix
@logea
async def despejarcompras_command(update: Update, 
                                      context: ContextTypes.DEFAULT_TYPE) -> None:
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
@logea
async def despejarlistacompras_command(update:Update,
                                       context: ContextTypes.DEFAULT_TYPE) -> None:
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
@logea
async def despejarunatarea_command(update:Update,
                                    context: ContextTypes.DEFAULT_TYPE) -> None:
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
@logea
async def despejarregistrado_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    procesado = procesar_parámetros(args, 4)
    mensaje = EditorSheet().despejar_registrado(procesado)
    await update.message.reply_text(mensaje)

@requiere_usuarix
@logea
async def desactivarrecordatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lista_recordatorios = Respuestas("", None).lista_recordatorios
    categoría_recordatorio = ""
    if context.args:
        args = " ".join(context.args)
    else:
        await update.message.reply_text("Por favor indicá a qué categoría"
            " de recordatorios pertenece el que querés desactivar!")
        return

    for categoría in lista_recordatorios.items():
        if any(palabra in args for palabra in categoría[1]):
            for palabra in categoría[1]:
                args_split = args.split(palabra)
                args = args_split[-1]
            args = args.strip()
            categoría_recordatorio = categoría[0]
    if categoría_recordatorio:
        for recordatorio in config.RECORDATORIOS[categoría_recordatorio]:
            if args in recordatorio:
                config.RECORDATORIOS[categoría_recordatorio][recordatorio]["activo"] = False
                config.actualizar_recordatorios()
                await update.message.reply_text(f"Desactivado el recordatorio {recordatorio}!")
                break
        else:
            await update.message.reply_text("No encontré elrecordatorio que buscaste!")
    else:
        await update.message.reply_text("No encontré la categoría que indicaste de recordatorio!"
            " En la refe podés encontrar las categorías :)")

@requiere_usuarix
@logea
async def activarrecordatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lista_recordatorios = Respuestas("", None).lista_recordatorios
    categoría_recordatorio = ""
    if context.args:
        args = " ".join(context.args)
    else:
        await update.message.reply_text("Por favor indicá a qué categoría"
            " de recordatorios pertenece el que querés desactivar!")
        return

    for categoría in lista_recordatorios.items():
        if any(palabra in args for palabra in categoría[1]):
            for palabra in categoría[1]:
                args_split = args.split(palabra)
                args = args_split[-1]
            args = args.strip()
            categoría_recordatorio = categoría[0]
    if categoría_recordatorio:
        for recordatorio in config.RECORDATORIOS[categoría_recordatorio]:
            if args in recordatorio:
                config.RECORDATORIOS[categoría_recordatorio][recordatorio]["activo"] = True
                config.actualizar_recordatorios()
                await update.message.reply_text(f"Activado el recordatorio {recordatorio}!")
                break
        else:
            await update.message.reply_text("No encontré elrecordatorio que buscaste!")
    else:
        await update.message.reply_text("No encontré la categoría que indicaste de recordatorio!"
            " En la refe podés encontrar las categorías :)")

@requiere_usuarix
@logea
async def agregarfactura_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    editor = EditorSheet()
    args = context.args
    procesados = procesar_parámetros(args, 3)
    if error := chequear_contenido_parámetros(procesados, 2):
        await update.message.reply_text(error)
        return
    else:
        categoría, valor = procesados

    if categoría_obj := chequear_categoría_facturas(categoría):
        categoría_facturas = categoría_obj
    else:
        await update.message.reply_text("No encontré la lista :(")
        return

    await update.message.reply_text(editor.agregar_factura(valor, categoría=categoría_facturas))

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


def chequear_categoría_facturas(categoría: str):
    """Itera sobre  las listas de palabras de cada categoría clave(presentes en listas_compras
    del módulo de Respuestas) y extrae la CategoríaCompras correspondiente"""
    lista_palabras = Respuestas("", None).lista_facturas
    categoría = categoría.strip()
    for key in lista_palabras:
        if categoría in lista_palabras[key]:
            categoría = key.upper()
            categoría_obj = getattr(EditorSheet.CategoríaFacturas, categoría)
            return categoría_obj

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
