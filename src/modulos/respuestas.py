from enum import Enum
from modulos.editor import EditorSheet
from unidecode import unidecode
from telegram import Update

class Respuestas:
    def __init__(self, texto: str, update: Update):
        self.texto_procesado = unidecode(texto.lower())
        self.update = update
        self.editor = EditorSheet()
        self.nombre_usuario = update.message.from_user.first_name
        with open("secretos/bot_user.txt", "r", encoding="ascii") as file:
            self.BOT_USERNAME = str(file.read().strip())

        self.listas_palabras = {
        # Lista de tareas
        "tareas": (["tareas", "tarea", "pendientes", "pendiente"], self.editor.get_tareas_diarias,
        None, "No hay tareas pendientes! 🎉"),
        # Compras
        "juanito": (["juanito"], self.editor.get_lista_compras, 
        self.editor.CategoríaCompras.JUANITO, "No hay nada para comprar en esa lista! 🎉"),
        "diarias": (["diarias"], self.diarias, None, "No hay nada para comprar en las listas"
                                                " de supermercado ni verdulería! 🎉"),
        "mensuales": (["mensuales", "mensual", "coto", "mes"], self.editor.get_lista_compras,
        self.editor.CategoríaCompras.MENSUALES, "No hay nada para comprar en esa lista! 🎉"),
        "supermercado": (["super", "supermercado", "chino"], self.editor.get_lista_compras,
        self.editor.CategoríaCompras.SUPERMERCADO, "No hay nada para comprar en esa lista! 🎉"),
        "verdulería": (["verdulería", "verdu", "verduras"], self.editor.get_lista_compras,
        self.editor.CategoríaCompras.VERDULERIA, "No hay nada para comprar en esa lista! 🎉"),
            # Registro de víveres. Pasan la lista de palabras y el método el editor a llamar
        "regcompras_apertura": (["abri", "abrio", "abrimos"], self.procesar_texto_registrada, 
                                (["abri", "abrio", "abrimos"], self.editor.abrir_compra_registrada), 
                                "No encontré el ítem que mencionás 🙁"),
        "regcompras_agotado": (["termine", "termino", "terminamos", "acabe", "acabo", "acabamos",
                                "agote", "agoto", "agotamos"], self.procesar_texto_registrada, 
                               (["termine", "termino", "terminamos", "acabe", "acabo", "acabamos",
                                "agote", "agoto", "agotamos"], self.editor.agotar_compra_registrada),
                                "No encontré el ítem que mencionás 🙁"),
        #Quehaceres
        "caja_asiri": (["caja", "piedras"], 
                       self.editor.agregar_quehacer,
                       (self.nombre_usuario, self.editor.CategoríaQuehaceres.CAJA),
                        "Ya figura como que alguien más limpió la caja de asiri!"),
        "bebedero_asiri": (["bebedero", "fuente", "agua"], 
                           self.editor.agregar_quehacer,
                           (self.nombre_usuario, self.editor.CategoríaQuehaceres.BEBEDERO),
                        "Ya figura como que alguien más limpió el bebedero de asiri!"),
        "lavar_tachos": (["tacho", "tachos"], 
                         self.editor.agregar_quehacer,
                         (self.nombre_usuario, self.editor.CategoríaQuehaceres.TACHO),
                        "Ya figura como que alguien más lavó el/los tacho/s!"),
        "barrer": (["barri"], 
                   self.editor.agregar_quehacer, 
                   (self.nombre_usuario, self.editor.CategoríaQuehaceres.BARRER),
                   "Ya figura como que barrió alguien más!"),
        "trapear": (["trapee", "trape", "trapie"], 
                    self.editor.agregar_quehacer, 
                    (self.nombre_usuario, self.editor.CategoríaQuehaceres.TRAPEAR),
                    "Ya figura como que trapeó alguien más!"),
        "sacar_reciclables": (["reciclable", "reciclables"], 
                              self.editor.agregar_quehacer,
                              (self.nombre_usuario, self.editor.CategoríaQuehaceres.RECICLABLES),
                               "Ya figura como que alguien más sacó la basura reciclable!"),
        "sacar_basura": (["basura"], 
                         self.editor.agregar_quehacer, 
                         (self.nombre_usuario, self.editor.CategoríaQuehaceres.BASURA),
                        "Ya figura como que alguien más sacó la basura!"),
        "lavar_ropa": (["lavar", "lave", "ropa"], 
                       self.editor.agregar_quehacer,
                       (self.nombre_usuario, self.editor.CategoríaQuehaceres.LAVAR),
                        "Ya figura como que alguien más lavó la ropa!"),
        "colgar_ropa": (["colgar", "colgue", "seque", "secar", "tender"], 
                        self.editor.agregar_quehacer,
                        (self.nombre_usuario, self.editor.CategoríaQuehaceres.COLGAR),
                        "Ya figura como que alguien más colgó la ropa!"),
        "doblar_ropa": (["doblar", "doble", "guarde", "guardar"],
                        self.editor.agregar_quehacer,
                        (self.nombre_usuario, self.editor.CategoríaQuehaceres.DOBLAR),
                        "Ya figura como que alguien más dobló la ropa!"),
        "hacer_compras": (["compre", "compras", "comprar"], 
                          self.editor.agregar_quehacer,
                          (self.nombre_usuario, self.editor.CategoríaQuehaceres.COMPRAS),
                        "Ya figura como que alguien más hizo las compras hoy!"),
        "limpiar": (["limpie"], 
                    self.editor.agregar_quehacer, 
                    (self.nombre_usuario, self.editor.CategoríaQuehaceres.LIMPIAR),
                    "Ya figura como que limpió alguien más!"),
        }

    def método_vacío(self, _):
    # Placeholder hasta que arme los métodos que necesito
        pass

    def respuestas(self) -> str:
        for key in self.listas_palabras:
            respuesta = self.chequear_presencia(self.listas_palabras[key])
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
        supermercado = self.listas_palabras["supermercado"]
        verdulería = self.listas_palabras["verdulería"]
        supermercado_respuesta = supermercado[1](*supermercado[2])
        verdulería_respuesta = verdulería[1](*verdulería[2])
        respuesta = (supermercado_respuesta + "\n" + verdulería_respuesta)
        if supermercado_respuesta and verdulería_respuesta:
            return respuesta
        else:
            return ""

    def procesar_texto_registrada(self, info):
        print("Procesando texto registrada")
        palabras_clave, función = info
        pronombres = ["el", "la", "los", "las"]
        texto_procesado_lista = self.texto_procesado.split()
        for palabra in texto_procesado_lista.copy():
            if palabra in palabras_clave:
                for x in range(texto_procesado_lista.index(palabra) + 1):
                    texto_procesado_lista.pop(0)
                break
        if texto_procesado_lista[0] in pronombres:
            texto_procesado_lista.pop(0)
        print(f"Texto procesado: {texto_procesado_lista}")
        return función(" ".join(texto_procesado_lista))
