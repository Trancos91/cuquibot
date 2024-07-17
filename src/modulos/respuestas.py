from src.pysolidaridad import EditorSheet
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
        prox_comida = ["toca", "preparar", "preparamos", "proxima", "proximo", "que viene"]
        menu_rotativo = ["rotativo"]
        asistentes = ["quienes", "somos", "van", "vamos", "asistentes", "asisten"]
        turno_cocina = ["cocina", "cocinar", "temprano"]
        turno_recorrida = ["recorrida", "reco", "noche"]
        turno_limpieza = ["limpieza", "limpiar", "ordenar", "orden"]
        faltantes = ["falta", "faltan", "faltantes"]
        info_comida = ["info", "informacion", "data"]
        baja = ["me bajo"]
        submenu_pendientes = ["pendiente", "pendientes", "tarea", "tareas"]
        pendientes_jueves = ["jueves"]
        pendientes_grales = ["general", "generales", "grales", "gral"]

    def respuestas(self) -> str:
        if "voy" in self.texto_procesado:
        #and date.today().weekday() == 3:
            return self.submenu_voy(self.texto_procesado)
        if any(word in self.texto_procesado for word in self.ListasPalabras.prox_comida):
            if not any(word in self.texto_procesado for word in self.ListasPalabras.submenu_pendientes):
                return self.editor.get_prox_comida()
        if any(word in self.texto_procesado for word in self.ListasPalabras.menu_rotativo):
            return self.editor.get_menu_rotativo()
        if any(word in self.texto_procesado for word in self.ListasPalabras.asistentes):
            return f"<pre>{self.editor.get_asistentes()}</pre>"
        if any(word in self.texto_procesado for word in self.ListasPalabras.faltantes):
            respuesta = self.editor.get_faltantes()
            if respuesta:
                return respuesta
            else:
                return "No hay faltantes! 💜"
        if any(word in self.texto_procesado for word in self.ListasPalabras.baja):
            return self.baja_asistente()
        if any(word in self.texto_procesado for word in self.ListasPalabras.info_comida):
            texto_subcomando = self.texto_procesado
            for palabra in self.ListasPalabras.info_comida:
                texto_subcomando = texto_subcomando.replace(palabra, "")
            return self.editor.get_info(texto_subcomando.strip())
        if any(word in self.texto_procesado for word in self.ListasPalabras.submenu_pendientes):
            respuesta = self.submenu_pendientes(self.texto_procesado)
            if respuesta:
                return respuesta
            else:
                return "No hay tareas pendientes! 🎉"
        
        
        return "No entendí"

    def submenu_voy(self, texto_procesado: str):
        if any(word in texto_procesado for word in self.ListasPalabras.turno_cocina):
            return self.chequear_duplicados_asistentes(self.editor.Turno.COCINA)
        elif any(word in texto_procesado for word in self.ListasPalabras.turno_recorrida):
            return self.chequear_duplicados_asistentes(self.editor.Turno.RECORRIDA)
        elif any(word in texto_procesado for word in self.ListasPalabras.turno_limpieza):
            return self.chequear_duplicados_asistentes(self.editor.Turno.LIMPIEZA)
        elif "todo" in texto_procesado:
            return self.chequear_duplicados_asistentes(self.editor.Turno.COCINA) + "\n" + \
                    self.chequear_duplicados_asistentes(self.editor.Turno.RECORRIDA) + "\n" + \
                    self.chequear_duplicados_asistentes(self.editor.Turno.LIMPIEZA)
        else:
            return "No entendí a qué turno querías que te sume :c"

    def submenu_pendientes(self, texto_procesado: str):
        if any(word in texto_procesado for word in self.ListasPalabras.pendientes_jueves):
            return self.editor.get_pendientes_jueves()
        if any(word in texto_procesado for word in self.ListasPalabras.pendientes_grales):
            return self.editor.get_pendientes_grales()
        else:
            return ("Por favor aclará si querés la lista de tareas pendientes "
                    "de los jueves o general")

    def chequear_duplicados_asistentes(self, turno):
        if self.editor.agregar_asistente(self.nombre_usuario, turno):
            return f"Agregadx {self.nombre_usuario} al turno de {turno.value[1]}"
        else:
            return f"{self.nombre_usuario} ya está en el turno {turno.value[1]}!"

    def baja_asistente(self):
        self.editor.despejar_asistente(self.nombre_usuario, self.editor.Turno.COCINA)
        self.editor.despejar_asistente(self.nombre_usuario, self.editor.Turno.RECORRIDA)
        self.editor.despejar_asistente(self.nombre_usuario, self.editor.Turno.LIMPIEZA)
        return f"Ahí te quité de la lista de asistentes, {self.nombre_usuario}! Nos vemos la próxima :)"

    

