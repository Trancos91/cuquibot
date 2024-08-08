from collections.abc import Sequence
import json
from enum import Enum
from modulos.editor import EditorSheet
from unidecode import unidecode
from telegram import Update

class Respuestas:
    def __init__(self, texto: str, update: Update):
        self.texto = texto
        self.texto_procesado = unidecode(texto.lower())
        self.update = update
        self.editor = EditorSheet()
        self.first_name = update.message.from_user.first_name
        self.lista_flags_ubicaciones = self.editor.lista_flags_ubicaciones
        with open("secretos/alias.json", "r", encoding="ascii") as file:
            alias = json.load(file)
        try:
            self.nombre_usuario = alias[self.first_name]
        except KeyError:
            print("Alguien más está usando el bot! :O")
            self.nombre_usuario = "Desconocidx o.o"
        with open("secretos/bot_user.txt", "r", encoding="ascii") as file:
            self.BOT_USERNAME = str(file.read().strip())

        # Lista de palabras que procesaría el bot en un mensaje
        self.listas_palabras = {
            "tareas": ["tareas", "tarea", "pendientes", "pendiente"],
            "diarias": ["diarias"],
            "regcompras_apertura": ["abri", "abrio", "abrimos"],
            "regcompras_agotado": ["termine", "termino", "terminamos", "acabe", 
                                   "acabo", "acabamos", "agote", "agoto", "agotamos"],
            "lista_flags_ubicaciones": ["flags", "ubicaciones", "lugares", "flag",
                                        "ubicacion", "lugar"],
            "regcompras_lista": ["registradas", "registrados", "regsitro"],
            "regcompras_duración": ["duracion", "dura", "duro", "duraron", "agotarse", "acabarse"],
            "regcompras_duraciones": ["duraciones"],
            "referencia": ["referencia", "refe", "palabras"]
        }
        # Lista_palabras de quehaceres, pero contiene también mensajes de fallo
        self.lista_quehaceres = {
            "caja": (["caja", "piedras"], "limpió la caja de asiri"),
            "bebedero": (["bebedero", "fuente", "agua"], "limpió el bebedero de asiri"),
            "tacho": (["tacho", "tachos", "tachito", "tachitos"], "limpió el/los tacho/s"),
            "barrer": (["barri", "escoba", "escobillon"], "barrió"),
            "trapear": (["trapee", "trape", "trapie", "trapo"], "pasó el trapo"),
            "reciclables": (["reciclable", "reciclables"], "sacó los reciclables"),
            "basura": (["basura"], "sacó la basura"),
            "colgar": (["colgar", "colgue", "seque", "secar", "tender"], "colgó la ropa"),
            "doblar": (["doblar", "doble", "guarde", "guardar"], "dobló la ropa"),
            "lavar": (["lavar", "lave", "ropa"], "puso a lavar la ropa"),
            "compras": (["compre", "compras", "comprar"], "salió a hacer las compras"),
            "limpiar": (["limpie"], "limpió"),
        }
        # Lista_palabras de compras. No necesita mensajes de fallo, el mismo para
        # todas funciona
        self.lista_compras = {
            "juanito": ["juanito"],
            "mensuales": ["mensuales", "mensual", "coto", "mes"],
            "supermercado": ["super", "supermercado", "chino"],
            "verduleria": ["verdulería", "verdu", "verduras"],
        }
        # Mensaje de referencia de palabras:
        self.mensaje_refe = (
            '📕 <b><u>Lista de palabras clave a las que respondo (con sus alternativas entre paréntesis):</u></b>\n'
            '<u>Contenido en listas:</u>\n'
            '  • <b><i>Supermercado</i></b>(<i>super, chino</i>)\n'
            '  • <b><i>Verdulería</i></b>(<i>verdu, verduras</i>)\n'
            '  • <b><i>Diarias</i></b>\n'
            '  • <b><i>Mensuales</i></b>(<i>mensual, coto, mes</i>)\n'
            '  • <b><i>Juanito</i></b>\n'
            '  • <b><i>Tareas</i></b>(<i>tarea, pendientes, pendiente</i>)\n'
            '  • <b><i>Registradas</i></b>(<i>registrados, registro</i>)\n'
            '  • <b><i>Flags</i></b>(<i>ubicaciones, lugares, flag, ubicación, lugar</i>)\n'
            '<u>Acciones sobre el registro de víveres:</u>\n'
            '  • <b><i>Abrí</i></b>(<i>abrió, abrimos</i>): Marca la fecha de apertura de <b>un</b> elemento\n'
            '  • <b><i>Terminé</i></b>(<i>terminó, terminamos, agoté, agotó, agotamos, acabé, acabó, acabamos</i>): '
            'Marca la fecha de agotamiento de <b>un</b> elemento\n'
            '  • <b><i>Duración</i></b>(<i>dura, duró, duraron, agotarse, acabarse</i>): Responde cuánto tiempo '
            'tardó en agotarse(en días) <b>un</b> elemento\n'
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
            ' caca y el aserrín o le hayas cambiado las piedras, directamente)\n\n'
            '⚠️ <b>Nota importante</b>: Aunque algunas de las palabras usen conjugaciones en segunda o tercera persona, '
            'el bot da por sentado que fue quien mandó el mensaje quien hizo las cosas en donde es relevante'
            '(por ejemplo, cuando se trata de cumplir quehaceres)'
        )
        self.config_tareas = {
        # Lista de tareas
        "tareas": (self.listas_palabras["tareas"], self.editor.get_tareas_diarias,
        None, "No hay tareas pendientes! 🎉"),
        # Compras
        "diarias": (self.listas_palabras["diarias"], self.diarias, None,
                    "No hay nada para comprar en las listas de supermercado ni verdulería! 🎉"),
        # Registro de víveres. Pasan la lista de palabras y el método el editor a llamar
        "regcompras_apertura": (self.listas_palabras["regcompras_apertura"], self.procesar_texto_registrada, 
                                (self.listas_palabras["regcompras_apertura"], self.editor.abrir_compra_registrada), 
                                "No encontré el ítem que mencionás 🙁"),
        "regcompras_agotado": (self.listas_palabras["regcompras_agotado"], self.procesar_texto_registrada, 
                               (self.listas_palabras["regcompras_agotado"], self.editor.agotar_compra_registrada),
                                "No encontré el ítem que mencionás 🙁"),
        "regcompras_duraciones": (self.listas_palabras["regcompras_duraciones"], self.procesar_texto_registrada,
                                  (self.listas_palabras["regcompras_duraciones"], self.editor.get_duraciones_registrada),
                                  "parafernalia"),
        "regcompras_duración": (self.listas_palabras["regcompras_duración"], self.procesar_texto_registrada, 
                               (self.listas_palabras["regcompras_duración"], self.editor.get_duración_registrada),
                                "No encontré el ítem que mencionás 🙁"),
        "regcompras_lista": (self.listas_palabras["regcompras_lista"], self.editor.get_compras_registradas,
                             None, "Parece que no hay ninguna compra en la lista de registradas!"),
        "lista_flags_ubicaciones": (self.listas_palabras["lista_flags_ubicaciones"],
                                    self.editor.get_flags_ubicaciones, None,
                                    "Algo anda mal, no conseguí la lista de ubicaciones! 🙁"),
        "referencia": (self.listas_palabras["referencia"], self.mensaje_simple,
                       (self.mensaje_refe, ), "El mensaje de referencia no debería dar error")
        }
        lista_inicialización = ((self.tupla_quehaceres, self.lista_quehaceres),
                                 (self.tupla_compras, self.lista_compras))
        #Inicializado listas para el diccionario
        for tupla in lista_inicialización:
            dicc_lista = {k: tupla[0](k) for k in tupla[1]}
            self.config_tareas.update(dicc_lista)

    def tupla_quehaceres(self, key: str):
        upperkey = key.upper().strip()
        categoría_obj = getattr(self.editor.CategoríaQuehaceres, upperkey)
        return (self.lista_quehaceres[key][0], self.procesar_texto_quehacer,
                 (self.nombre_usuario, categoría_obj, self.editor.agregar_quehacer),
                 "Ya figura como que alguien más " + self.lista_quehaceres[key][1] + "!")

    def tupla_compras(self, key: str):
        upperkey = key.upper().strip()
        categoría_obj = getattr(self.editor.CategoríaCompras, upperkey)
        return (self.lista_compras[key], self.editor.get_lista_compras,
                 categoría_obj, "No hay nada para comprar en esa lista! 🎉")

    def respuestas(self) -> str:
        """
        Itera sobre cada tarea y chequea si llamó alguna función.
        """
        for key in self.config_tareas:
            respuesta = self.chequear_presencia(self.config_tareas[key])
            if respuesta:
                break
        return respuesta if respuesta else "No entendí"

    def chequear_presencia(self, categoría):
        """
        Chequea la presencia de las palabras clave en las palabras del mensaje.
        Si están, agrupa los argumentos en una tupla(en caso de que no estuviesen
        agrupados ya) y llama la función indicada pasándole los argumentos. Si
        la función devuelve algo, lo devuelve, y si no, devuelve el mensaje de error.
        """
        if any(word in self.texto_procesado for word in categoría[0]):
            if isinstance(categoría[2], Sequence):
                tupla_categoría = categoría[2]
            else:
                tupla_categoría = (categoría[2], )
                #try:
                #    iter(categoría[2])
                #    tupla_categoría = categoría[2]
                #except TypeError:
                #    tupla_categoría = (categoría[2], )
            respuesta = categoría[1](*tupla_categoría)
            if respuesta:
                return respuesta
            else:
                return categoría[3]

    def mensaje_simple(self, mensaje):
        return mensaje

    def diarias(self, _):
        """
        Función especial para el chequeo de compras diarias(combina dos listas)
        """
        supermercado = self.config_tareas["supermercado"]
        verduleria = self.config_tareas["verduleria"]
        supermercado_respuesta = supermercado[1](supermercado[2])
        verduleria_respuesta = verduleria[1](verduleria[2])
        respuesta = (supermercado_respuesta + "\n" + verduleria_respuesta)
        if supermercado_respuesta or verduleria_respuesta:
            return respuesta
        else:
            return ""

    def procesar_texto_registrada(self, palabras_clave, función):
        """
        Procesa el texto de los mensajes del estilo "abrí"o "se agotó", extrayendo
        las palabras después del "comando" como argumentos.
        """
        pronombres = ["el", "la", "los", "las"]
        texto_procesado_lista = self.texto_procesado.split()
        for palabra in texto_procesado_lista.copy():
            if palabra in palabras_clave:
                for x in range(texto_procesado_lista.index(palabra) + 1):
                    texto_procesado_lista.pop(0)
                break
        if texto_procesado_lista[0] in pronombres:
            texto_procesado_lista.pop(0)
        print(f"texto_procesado_lista = {texto_procesado_lista}")
        return función(" ".join(texto_procesado_lista))
    
    def procesar_texto_quehacer(self, nombre_usuario, categoría, función):
        try:
            _, flags = self.texto.split("-")
            flags = flags.strip()
        except ValueError:
            flags = None
        return función(nombre_usuario, categoría, flags)
