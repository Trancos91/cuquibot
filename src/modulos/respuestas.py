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
        for key in self.config_tareas:
            respuesta = self.chequear_presencia(self.config_tareas[key])
            if respuesta:
                break
        return respuesta if respuesta else "No entendí"

    def chequear_presencia(self, categoría):
        if any(word in self.texto_procesado for word in categoría[0]):
            try:
                iter(categoría[2])
                tupla_categoría = categoría[2]
            except TypeError:
                tupla_categoría = (categoría[2], )
            respuesta = categoría[1](*tupla_categoría)
            if respuesta:
                return respuesta
            else:
                return categoría[3]


    def diarias(self, _):
        supermercado = self.config_tareas["supermercado"]
        verduleria = self.config_tareas["verduleria"]
        supermercado_respuesta = supermercado[1](supermercado[2])
        verduleria_respuesta = verduleria[1](verduleria[2])
        respuesta = (supermercado_respuesta + "\n" + verduleria_respuesta)
        if supermercado_respuesta and verduleria_respuesta:
            return respuesta
        else:
            return ""

    def procesar_texto_registrada(self, palabras_clave, función):
        pronombres = ["el", "la", "los", "las"]
        texto_procesado_lista = self.texto_procesado.split()
        for palabra in texto_procesado_lista.copy():
            if palabra in palabras_clave:
                for x in range(texto_procesado_lista.index(palabra) + 1):
                    texto_procesado_lista.pop(0)
                break
        if texto_procesado_lista[0] in pronombres:
            texto_procesado_lista.pop(0)
        return función(" ".join(texto_procesado_lista))
    
    def procesar_texto_quehacer(self, nombre_usuario, categoría, función):
        try:
            _, flags = self.texto.split("-")
            flags = flags.strip()
        except ValueError:
            flags = None
        return función(nombre_usuario, categoría, flags)
