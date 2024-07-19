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
        "tareas": (["tareas", "tarea", "pendientes", "pendiente"], self.editor.get_tareas_diarias,
        None, "No hay tareas pendientes! 🎉"),
        "juanito": (["juanito"], self.editor.get_lista_compras, 
        self.editor.CategoríaCompras.JUANITO, "No hay nada para comprar en esa lista! 🎉"),
        "diarias": (["diarias"], self.diarias, None, "No hay nada para comprar en las "
        "listas de supermercado ni verdulería! 🎉"),
        "mensuales": (["mensuales", "mensual", "coto", "mes"], self.editor.get_lista_compras,
        self.editor.CategoríaCompras.MENSUALES, "No hay nada para comprar en esa lista! 🎉"),
        "supermercado": (["super", "supermercado", "chino"], self.editor.get_lista_compras,
        self.editor.CategoríaCompras.SUPERMERCADO, "No hay nada para comprar en esa lista! 🎉"),
        "verdulería": (["verdulería", "verdu", "verduras"], self.editor.get_lista_compras,
        self.editor.CategoríaCompras.VERDULERIA, "No hay nada para comprar en esa lista! 🎉"),
        }


    def respuestas(self) -> str:
        for key in self.listas_palabras:
            respuesta = self.chequear_presencia(self.listas_palabras[key])
            if respuesta:
                break
        return respuesta if respuesta else "No entendí"

    def chequear_presencia(self, categoría):
        if any(word in self.texto_procesado for word in categoría[0]):
            respuesta = categoría[1](categoría[2])
            if respuesta:
                return respuesta
            else:
                return categoría[3]


    def diarias(self, _):
        supermercado = self.listas_palabras["supermercado"]
        verdulería = self.listas_palabras["verdulería"]
        respuesta = (supermercado[1](supermercado[2]) + "\n" +
                verdulería[1](verdulería[2]))
        if respuesta:
            return respuesta
        else:
            return ""
