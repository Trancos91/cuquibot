from collections.abc import Sequence
import tomllib
from modulos.editor import EditorSheet
from unidecode import unidecode
from telegram import Update
from modulos.mensajes import Mensajes

class Respuestas:
    """Objeto que se encarga de procesar todo el texto que no es un comando
    y de llamar los métodos apropiados. Utiliza diccionarios para almacenar
    las palabras claves y los métodos asociados."""
    def __init__(self, texto: str, update: Update | None = None):
        self.texto = texto
        self.texto_procesado = unidecode(texto.lower())
        self.update = update
        self.editor = EditorSheet()
        if update: 
            self.id = str(update.message.from_user.id)
            with open("secretos/config.toml", "rb") as file:
                config = tomllib.load(file)
            try:
                self.nombre_usuario = config["users"][self.id]["alias"]
                self.BOT_USERNAME = config["telegram"]["bot_user"]
            except KeyError:
                print("Alguien más está usando el bot! :O")
                print(f"Usuarix: {update.message.from_user.first_name}")
                print(f"ID: {update.message.from_user.id}")
                self.usuarix_desconocidx()
        else:
            self.nombre_usuario = "Nadie"
        self.lista_flags_ubicaciones = self.editor.lista_flags_ubicaciones

        # Lista que contiene las keys de las listas de compras que pertenecen a "diarias"
        self.lista_diarias = ["supermercado", "verduleria", "varias"]

        # Lista de palabras que procesaría el bot en un mensaje
        self.listas_palabras = {
            "tareas": ["tareas", "tarea", "pendientes", "pendiente"],
            "diarias": ["diarias", "del dia", "diaria"],
            "regcompras_apertura": ["abri", "abrio", "abrimos"],
            "regcompras_agotado": ["termine", "termino", "terminamos", "acabe", 
                                   "acabo", "acabamos", "agote", "agoto", "agotamos"],
            "lista_flags_ubicaciones": ["flags", "ubicaciones", "lugares", "flag",
                                        "ubicacion", "lugar"],
            "regcompras_lista": ["registradas", "registrados", "regsitro"],
            "regcompras_duración": ["duracion", "dura", "duro", "duraron", "agotarse", "acabarse"],
            "regcompras_duraciones": ["duraciones"],
            "regcompras_estados": ["estado", "estatus", "status", "estados"],
            "referencia": ["referencia", "refe", "palabras"]
        }
        # Lista_palabras de quehaceres, pero contiene también mensajes de la tarea realizada
        self.lista_quehaceres = {
            "caja": (["caja", "piedras"], "limpió la caja de asiri"),
            "bebedero": (["bebedero", "fuente", "agua"], "limpió el bebedero de asiri"),
            "tacho": (["tacho", "tachos", "tachito", "tachitos"], "limpió el/los tacho/s"),
            "platito": (["plato", "platito"], "lavó el plato de la comida de asiri"),
            "barrer": (["barri", "escoba", "escobillon"], "barrió"),
            "trapear": (["trapee", "trape", "trapie", "trapo"], "pasó el trapo"),
            "reciclables": (["reciclable", "reciclables"], "sacó los reciclables"),
            "basura": (["basura"], "sacó la basura"),
            "colgar": (["colgar", "colgue", "seque", "secar", "tender"], "colgó la ropa"),
            "doblar": (["doblar", "doble", "guarde", "guardar"], "dobló la ropa"),
            "lavar": (["lavar", "lave", "ropa"], "puso a lavar la ropa"),
            "compras": (["compre", "compras", "comprar"], "salió a hacer las compras"),
            "limpiar": (["limpie", "limpió"], "limpió"),
            "regar": (["regue", "rego", "regar", "plantas"], "regó las plantas"),
        }
        # Lista_palabras de compras. No necesita mensajes específicos, el mismo para
        # todas funciona
        self.lista_compras = {
            "modelo_juanito": ["modelo juanito", "modelo-juanito", "modelo_juanito", 
                               "modelojuanito", "mjuanito"],
            "modelo_mensuales": ["modelo mensuales", "modelo mensual", "modelo coto", "modelo mes",
                                 "modelo-mensuales", "modelo-mensual", "modelo-coto", "modelo-mes",
                                 "modelo_mensuales", "modelo_mensual", "modelo_coto", "modelo_mes",
                                 "modelomensuales", "modelomensual", "modelocoto", "modelomes",
                                 "mmensuales", "mmensual", "mcoto", "mmes"],
            "juanito": ["juanito", "dietetica"],
            "mensuales": ["mensuales", "mensual", "coto", "mes"],
            "supermercado": ["super", "supermercado", "chino"],
            "verduleria": ["verdulería", "verdu", "verduras"],
            "farmacia": ["farmacia", "farmacity", "farma"],
            "varias": ["varias", "varios"]
        }
        # Diccionario que asocia funciones, argumentos, y las listas de palabras que
        # llamarían a dichas funciones
        # FORMATO: (lista de palabras clave, función a llamar, argumento a pasar,
        #           mensaje de error si recibe None como return)
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
        "regcompras_duraciones": (self.listas_palabras["regcompras_duraciones"], self.editor.get_duraciones_registrada,
                                  None, "Parece que no hay ninguna compra en el registro de duraciones!"),
        "regcompras_estados": (self.listas_palabras["regcompras_estados"], self.editor.get_estado_registradas,
                               None, "Parece que no hay ninguna compra en la lista de registradas!"),
        "regcompras_duración": (self.listas_palabras["regcompras_duración"], self.procesar_texto_registrada, 
                               (self.listas_palabras["regcompras_duración"], self.editor.get_duración_registrada),
                                "No encontré el ítem que mencionás 🙁"),
        "regcompras_lista": (self.listas_palabras["regcompras_lista"], self.editor.get_compras_registradas,
                             None, "Parece que no hay ninguna compra en la lista de registradas!"),
        "lista_flags_ubicaciones": (self.listas_palabras["lista_flags_ubicaciones"],
                                    self.editor.get_flags_ubicaciones, None,
                                    "Algo anda mal, no conseguí la lista de ubicaciones! 🙁"),
        "referencia": (self.listas_palabras["referencia"], self.mensaje_simple,
                       (Mensajes.REFE.value, ), "El mensaje de referencia no debería dar error")
        }
        # Lista de inicialización con función de parseo y lista de palabras para parsear
        lista_inicialización = ((self.tupla_quehaceres, self.lista_quehaceres),
                                 (self.tupla_compras, self.lista_compras))
        #Inicializado listas para el diccionario
        for tupla in lista_inicialización:
            dicc_lista = {k: tupla[0](k) for k in tupla[1]}
            self.config_tareas.update(dicc_lista)

    def usuarix_desconocidx(self):
        return "Alguien no autorizadx está usando el bot!"

    def tupla_quehaceres(self, key: str):
        """
        Genera la tupla de quehaceres (con sus palabras claves, función a llamar, 
        e información) formateada para ser agregada a config_tareas.
        """
        upperkey = key.upper().strip()
        categoría_obj = getattr(self.editor.CategoríaQuehaceres, upperkey)
        return (self.lista_quehaceres[key][0], self.procesar_texto_quehacer,
                 (self.nombre_usuario, categoría_obj, self.editor.agregar_quehacer),
                 "Ya figura como que alguien más " + self.lista_quehaceres[key][1] + "!")

    def tupla_compras(self, key: str):
        """
        Genera la tupla de listas de compras (con sus palabras claves, función a llamar, 
        e información) formateada para ser agregada a config_tareas.
        """
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
        print(respuesta)
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
        respuestas = []
        for key in self.lista_diarias:
            x = self.config_tareas[key]
            respuestas.append(x[1](x[2]))
        respuesta = "\n".join(respuestas)
        if respuesta.strip():
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
        # Elimina todas las palabras anteriores a las palabras clave presentes en el texto,
        # para lidiar con mensajes del estilo 'el otro día se abrió x'
        for palabra in texto_procesado_lista.copy():
            if palabra in palabras_clave:
                for x in range(texto_procesado_lista.index(palabra) + 1):
                    texto_procesado_lista.pop(0)
                break
        if not texto_procesado_lista:
            return "Este comando necesita un parámetro, pero no recibió nada :("
        # Elimina los posibles pronombres que queden sueltos para casos de la índole
        # de 'Abrimos la yerba mate'
        if texto_procesado_lista[0] in pronombres:
            texto_procesado_lista.pop(0)
        return función(" ".join(texto_procesado_lista))
    
    def procesar_texto_quehacer(self, nombre_usuario, categoría, función):
        """
        Extrae las flags en los comandos que las usan y llama a la función  recibida
        pasándoselas.
        """
        try:
            _, flags = self.texto.split("-")
            flags = flags.strip()
        except ValueError:
            flags = None
        return función(nombre_usuario, categoría, flags)
