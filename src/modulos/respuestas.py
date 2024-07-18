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

    class ListasPalabras:
        submenu_compras =  ["compras", "compra"]
        tareas = ["tareas", "tarea", "pendientes", "pendiente"]
        juanito = ["juanito"]
        diarias = ["diarias", "supermercaro", "super", "chino"]
        mensuales = ["mensuales", "mensual", "coto", "mes"]

    def respuestas(self) -> str:
        if any(word in self.texto_procesado for word in self.ListasPalabras.submenu_compras):
            respuesta = self.submenu_compras(self.texto_procesado)
            if respuesta:
                return respuesta
            else:
                return "No hace falta comprar nada de esa lista! 🎉"
        if any(word in self.texto_procesado for word in self.ListasPalabras.tareas):
            respuesta = self.editor.get_tareas_diarias()
            if respuesta:
                return respuesta
            else:
                return "No hay tareas pendientes! 🎉"
        
        return "No entendí"

    def submenu_compras(self, texto_procesado: str):
        if any(word in texto_procesado for word in self.ListasPalabras.diarias):
            return self.editor.get_lista_compras(self.editor.CategoríaCompras.DIARIAS)
        if any(word in texto_procesado for word in self.ListasPalabras.mensuales):
            return self.editor.get_lista_compras(self.editor.CategoríaCompras.MENSUALES)
        if any(word in texto_procesado for word in self.ListasPalabras.juanito):
            return self.editor.get_lista_compras(self.editor.CategoríaCompras.JUANITO)
        elif "todo" in texto_procesado:
            return self.editor.get_lista_compras(self.editor.CategoríaCompras.DIARIAS) + "\n" + \
                    self.editor.get_lista_compras(self.editor.CategoríaCompras.MENSUALES) + "\n" + \
                    self.editor.get_lista_compras(self.editor.CategoríaCompras.JUANITO)
        else:
            return "No entendí qué lista querías ver :c"

