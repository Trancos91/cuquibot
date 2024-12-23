from enum import Enum

class Mensajes(Enum):
    START = (
        'Holi, soy el Cuquibot, miau!'
        ' Escribí "/help" para ver los comandos disponibles :3\n'
        'Si querés usarme, tenés que registrarte! Procurá hablar con mi humano'
        '(la persona que me administre)!'
    )
    HELP = (
        'Hola, nya! Soy la cuquibot 😺\n'
        'Si querés usarme, tenés que registrarte con el comando: \n'
        '<pre>/registrarusuarix contraseña alias</pre>\n'
        'Asegurate de que la primera "palabra" después del comando sea la contraseña, y el resto como querés que te diga!\n'
        'Te paso la lista de comandos(instrucciones que empiezan con "/") y '
        'de palabras clave :)\n\n'
        '📋 <b><u>Lista de comandos:</u></b>\n'
        '  • <b>/agregartareas:</b> Agregar tareas a la lista de tareas. Separalas con comas!\n'
        '  • <b>/agregarcompras:</b> Agregar ítems a una lista de compras específica. Escribí'
        ' la primera palabra refiriendo a la lista, y después ingresá las compras separadas por comas.'
        ' Por ejemplo: \n'
        '<pre>/agregarcompras super arroz, bicarbonato de sodio, azúcar morena</pre>\n'
        '  • <b>/agregarfactura:</b> Agregar una factura al registro de facturas. Escribí'
        ' la primera palabra refiriendo al tipo de factura, y después ingresá el valor.'
        ' Por ejemplo: \n'
        '<pre>/agregarfactura expensas 80.123,54</pre>\n'
        '  • <b>/registrarviveres:</b> Agregar un ítem al registro de víveres, a donde anotamos'
        ' las fechas de apertura y agotamiento de las cosas que compramos. Los ítems pueden '
        'contener la cantidad de ese ítem que se registra <i>entre paréntesis</i>. Por ejemplo:\n'
        '<pre>/registrarviveres Arroz(1kg), Lentejas(2kg), Leche de coco, Shampoo(500ml)</pre>\n'
        '  • <b>/despejarlistatareas:</b> Despeja por completo la lista de tareas.\n'
        '  • <b>/despejarlistacompras:</b> Despeja por completo una lista de compras. Por ejemplo:\n'
        '<pre>/despejarlistacompras juanito</pre>\n'
        '  • <b>/despejarcompras:</b> Despeja compras de la lista de compras. Escribí la primera'
        ' palabra refiriendo a la lista, y después ingresá las compras separadas por comas. Por ejemplo:\n'
        '<pre>/despejarcompras super leche de coco, maní, chocolate</pre>\n'
        '  • <b>/despejarunatarea:</b> Despeja una tarea de la lista de tareas.\n'
        '  • <b>/despejarregistrado:</b> Despeja <i>las fechas de apertura y agotamiento</i> '
        'de un elemento del registro de víveres, dejándolo listo para volver a registrar. '
        '<b>No</b> despeja el elemento en sí de la lista.\n'
        '  • <b>/activarrecordatorio:</b> Activa un recordatorio de la lista. Escribí la primera palabra'
        ' refiriendo al tipo de recordatorio(los tipos se encuentran en la refe),'
        ' y después ingresá el recordatorio en sí. Por ejemplo:\n'
        '<pre>/activarrecordatorio recurrentes aire acondicionado</pre>\n'
        '  • <b>/desactivarrecordatorio:</b> Desactiva un recordatorio de la lista. Escribí la primera palabra'
        ' refiriendo al tipo de recordatorio(los tipos se encuentran en la refe),'
        ' y después ingresá el recordatorio en sí. Por ejemplo:\n'
        '<pre>/desactivarrecordatorio quehaceres caja asiri</pre>\n'
        '📋 <b><u>Listas de compras:</u></b>\n'
        '  • Supermercado(o "super", o "chino")\n'
        '  • Verdulería(o "verdu")\n'
        '  • Mensuales(compras del coto mensuales)\n'
        '  • Juanito\n'
        '  • Farmacia\n'
        '  • Diarias(<i>sólo se puede utilizar para acceder a la lista, no para agregar ítems. '
        'Combina las listas de Supermercado, Verdulería y Varias</i>)\n\n'
        '💡 Por último, para acceder a la lista de palabras clave a las que respondo, '
        'que por lo general apuntan a pedidos de información o a anotar cosas más cotidianas '
        'como los quehaceres, tageame y escribí <i>referencia</i> o <i>refe</i>'
        '(también sirve <i>palabras</i>).'
    )
    REFE = (
        '📕 <b><u>Lista de palabras clave a las que respondo (con sus alternativas entre paréntesis):</u></b>\n'
        '<u>Contenido en listas:</u>\n'
        '  • <b><i>Supermercado</i></b>(<i>super, chino</i>)\n'
        '  • <b><i>Verdulería</i></b>(<i>verdu, verduras</i>)\n'
        '  • <b><i>Varias</i></b>(<i>verdu, verduras</i>)\n'
        '  • <b><i>Diarias</i></b>\n'
        '  • <b><i>Mensuales</i></b>(<i>mensual, coto, mes</i>)\n'
        '  • <b><i>Juanito</i></b>\n'
        '  • <b><i>Modelo Juanito</i></b>(puede ir sin separación o con guión o guión bajo, o si no <i>mjuanito</i>)\n'
        '  • <b><i>Modelo Mensuales</i></b>(<i>modelo mensual, modelo coto, modelo mes</i>. Puede ir sin separación o con guión o guión bajo, o si no <i>mmensuales</i>, <i>mcoto</i>, etc.)\n'
        '  • <b><i>Farmacia</i></b>(<i>farmacity, farma</i>)\n'
        '  • <b><i>Tareas</i></b>(<i>tarea, pendientes, pendiente</i>)\n'
        '  • <b><i>Registradas</i></b>(<i>registrados, registro</i>)\n'
        '  • <b><i>Estado</i></b>(<i>estados, estatus, status</i>): Muestra en qué estado'
        '  • <b><i>Recordatorios</i></b>(<i>recordatorio</i>): Lista los recordatorios y en qué'
        ' estado se encuentran. Se puede filtrar agregando la categoría(<b>recurrentes</b>(recurrente,'
        ' diario, diarios, frecuente, frecuentes), <b>quehaceres</b>(quehacer)).\n'
        '  • <b><i>Flags</i></b>(<i>ubicaciones, lugares, flag, ubicación, lugar</i>)\n'
        '<u>Acciones sobre el registro de víveres:</u>\n'
        '  • <b><i>Abrí</i></b>(<i>abrió, abrimos</i>): Marca la fecha de apertura de <b>un</b> elemento\n'
        '  • <b><i>Terminé</i></b>(<i>terminó, terminamos, agoté, agotó, agotamos, acabé, acabó, acabamos</i>): '
        'Marca la fecha de agotamiento de <b>un</b> elemento\n'
        '  • <b><i>Duración</i></b>(<i>dura, duró, duraron, agotarse, acabarse</i>): Responde cuánto tiempo '
        'tardó en agotarse(en días) <b>un</b> elemento\n'
        '  • <b><i>Duraciones</i></b>: Muestra las últimas duraciones de todos'
        'los ítems registrados.\n'
        '<u>Quehaceres para indicar su cumplimiento:</u>\n'
        '  • <b><i>Barrer</i></b>(<i>barrí, escoba, escobillón</i>)\n'
        '  • <b><i>Trapear</i></b>(<i>trapeé, trapé, trapié, trapo</i>)\n'
        '  • <b><i>Limpiar</i></b>(<i>limpié, limpió</i>)\n'
        '  • <b><i>Tacho</i></b>(<i>tachos, tachito, tachitos</i>: Indica que limpiaste '
        'un tacho, no que sacaste la basura)\n'
        '  • <b><i>Basura</i></b>: Indica que sacaste la basura común al pasillo\n'
        '  • <b><i>Reciclables</i></b>(<i>reciclable</i>): Indica que sacaste la basura reciclable '
        'al container en la calle\n'
        '  • <b><i>Lavar</i></b>(<i>lavé, ropa</i>): Indica que lavaste la ropa\n'
        '  • <b><i>Colgar</i></b>(<i>colgué, sequé, secar, tender</i>): Indica que colgaste la ropa '
        'a secar en el tender\n'
        '  • <b><i>Doblar</i></b>(<i>doblé, guardé, guardar</i>): Indica que doblaste la ropa y'
        '(opcionalmente) la guardaste en el armario\n'
        '  • <b><i>Compras</i></b>(<i>compré, comprar</i>): Indica que saliste a hacer las compras\n'
        '  • <b><i>Bebedero</i></b>(<i>fuente, agua</i>): Indica que <i>limpiaste</i> el bebedero de asiri\n'
        '  • <b><i>Caja</i></b>(<i>piedras</i>): Indica que limpiaste la caja de asiri(hayas sacado la'
        ' caca y el aserrín o le hayas cambiado las piedras, directamente)\n'
        '  • <b><i>Plato</i></b>:(<i>platito</i>): Indica que limpiaste el plato de comida de asiri\n\n'
        '⚠️ <b>Nota importante</b>: Aunque algunas de las palabras usen conjugaciones en segunda o tercera persona, '
        'el bot da por sentado que fue quien mandó el mensaje quien hizo las cosas en donde es relevante'
        '(por ejemplo, cuando se trata de cumplir quehaceres)'
    )
