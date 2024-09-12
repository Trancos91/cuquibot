import re
from datetime import date, datetime
from enum import Enum
import gspread
import pandas as pd
import numpy as np
from unidecode import unidecode
#from tabulate import tabulate

class EditorSheet:
    """Objeto para editar el sheet"""
    def __init__(self) -> None:
        # Identificándose como cuenta de servicio
        self.gc = gspread.service_account(filename="secretos/credentials.json")
        # Abriendo el 'workbook'(colección de worksheets) con el que vamos a trabajar
        with open("secretos/wskey.txt", "r", encoding="ascii") as file:
            self.workbook = self.gc.open_by_key(file.read().strip())
        # Cargando las varias worksheets a variables
        self.lista_compras = self.workbook.worksheet("Listas de compras")
        self.lista_tareas = self.workbook.worksheet("Tareas de la casa")
        self.quehaceres = self.workbook.worksheet("Registro de quehaceres")
        self.registro_compras = self.workbook.worksheet("Registro de víveres")
        self.duración_víveres = self.workbook.worksheet("Duración de víveres")
        # Lista de flags de ubicaciones para los parámetros que lo requieren
        self.lista_flags_ubicaciones = (
            ("h", "la habitación"),
            ("B", "el baño grande"),
            ("b", "el baño chico"),
            ("p", "el pasillo"),
            ("e", "el estudio"),
            ("t", "la zona de la tele"),
            ("l", "el living"),
            ("c", "la cocina"),
            ("a", "el ambiente(tele+living+cocina)", 
             (5, 6, 7)), # Contiene tupla con índices de los flags asociados
            ("d", "todo menos la cocina y el estudio", 
             (0, 1, 2, 3, 5 ,6)),
            ("x", "todo", (0, 1, 2, 3, 4, 5, 6, 7)),
        )

    class CategoríaCompras(Enum):
        """
        Colección de las categorías de compras, cada una con su propia lista.
        La primera int refiere a la posición del ítem en la lista. El string
        refiere al verbo, y el string de letra a su columna en la sheet.
        """
        SUPERMERCADO = (0, "del súper", "A")
        VERDULERIA = (1, "de la verdu", "B")
        MENSUALES = (2, "mensuales", "C")
        JUANITO = (3, "de juanito", "D")
        FARMACIA = (4, "de la farmacia", "E")
        POTOSI = (5, "de potosí", "F")
        MODELO_JUANITO = (8, "modelo de compras de juanito", "I")
        MODELO_MENSUALES  = (9, "modelo de compras mensuales", "J")

    class CategoríaQuehaceres(Enum):
        """
        La primera int refiere a la posición del ítem en la lista,
        el string refiere al verbo, el string de letra a su columna en la sheet,
        y la última integer es:
        0 = incompatible con flags
        1 = compatible con flags de ubicación
        """
        DIA = (0, "día", "A", 0)
        BARRER = (1, "barrer", "B", 1)
        TRAPEAR = (2, "trapear", "C", 1)
        LIMPIAR = (3, "limpiar", "D", 1)
        BASURA = (4, "sacar la basura", "E", 0)
        CAJA = (5, "limpiar la caja de asiri", "F", 0)
        BEBEDERO = (6, "limpiar el bebedero de asiri", "G", 0)
        TACHO = (7, "limpiar el/los tacho/s", "H", 0)
        LAVAR = (8, "lavar la ropa", "I", 0)
        COLGAR = (9, "colgar la ropa lavada", "J", 0)
        DOBLAR = (10, "doblar la ropa seca", "K", 0)
        COMPRAS = (11, "hacer las compras", "L", 0)
        RECICLABLES = (12, "sacar la basura reciclable a la calle", "M", 0)
        PLATITO = (13, "lavarle el plato a asiri", "N", 0)
        REGAR = (14, "regar las plantas", "O", 0)


    ##########################################################################
    #Métodos setter
    ##########################################################################
    def agregar_ítems(self, productos: list[str], categoría: CategoríaCompras | int= 0):
        """
        Agrega ítems a una categoría de la lista de compras si recibe una categoría,
        a la lista de tareas si recibe 0(por defecto) como categoría o al registro de víveres
        si recibe 1
        """
        if type(categoría) == self.CategoríaCompras:
            columna = categoría.value[0] + 1
            sheet = self.lista_compras
            final_respuesta = f"a la lista de compras de {categoría.value[1]}"
        elif categoría == 0:
            columna = 1
            sheet = self.lista_tareas
            final_respuesta = "a la lista de tareas"
        elif categoría == 1:
            print("Categoría 1 seleccionada")
            columna = 1
            sheet = self.registro_compras
            final_respuesta = "al registro de víveres"
            procesado = self.procesar_registrados(productos)
            productos, cantidades = procesado
        else:
            columna = None
            sheet = None
            cantidades = None
            print(f"Parámetro incorrecto para agregar_items(): categoría={categoría}")
            return "Algo falló en el programa, Juan debería revisar los logs."
        rows = sheet.col_values(columna)
        respuesta = "✅ Agregado "
        productos_proc = [x.capitalize() for x in productos]
        fecha_hoy = date.today().strftime("%Y/%m/%d")
        for producto in productos_proc:
            print(producto)
            if producto in rows:
                continue
            elif producto == productos_proc[-1]:
                if len(productos_proc) == 1:
                    respuesta += f" {producto} "
                else:
                    respuesta += f"y {producto} "
            else:
                respuesta += f"{producto}, "
            rows = sheet.col_values(columna)
            sheet.update_cell(len(rows) + 1, columna , producto)
            if categoría == 1 and cantidades and cantidades[productos_proc.index(producto)]:
                    sheet.update_cell(len(rows) + 1, 2, cantidades[productos_proc.index(producto)])
        respuesta += final_respuesta
        return respuesta 

    def abrir_compra_registrada(self, compra):
        return self.datestamp_compra_registrada(compra, 0)

    def agotar_compra_registrada(self, compra):
        return self.datestamp_compra_registrada(compra, 1)

    def datestamp_compra_registrada(self, compra, modo):
        """
        Marca como abierta o agotada una compra del registro de víveres.
        modo(int):
        0: Abierta
        1: Agotada
        """
        match modo:
            case 0:
                columna = 3
            case 1:
                columna = 4
            case _:
                columna = None
                print("Se seleccionó un número inválido para el modo de la función")
                return "Algo falló, Juan debería revisar los logs."
        búsqueda = self.buscar_ítem(compra, self.registro_compras)
        if not búsqueda:
            return
        if isinstance(búsqueda, str):
            búsqueda += ("\nPor favor aclarame qué ítem querés que marque como "
                            f"{"abierto" if modo == 0 else "agotado"}!")
            return búsqueda
        else:
            celda_compra = búsqueda
        if self.registro_compras.cell(celda_compra.row, columna).value:
            return (f"❗ Parece que este ítem ya fue marcado como "
                f"{"abierto" if modo == 0 else "agotado"} :)")
        elif modo == 1 and not self.registro_compras.cell(celda_compra.row, columna -1).value:
            return (f"❗ Parece que este ítem no tiene todavía una fecha de "
            "apertura! No querés registrar eso primero, mejor?")
        fecha_hoy = date.today().strftime("%Y/%m/%d")
        self.registro_compras.update_cell(celda_compra.row, columna, fecha_hoy)
        mensaje = (f"✅ Ahí registré que hoy, {fecha_hoy}, se "
            f"{"abrió" if modo == 0 else "agotó"} el siguiente ítem: {celda_compra.value} 😊")
        if modo == 0:
            return mensaje
        if modo == 1:
            row = self.registro_compras.row_values(celda_compra.row)
            return mensaje + self.agregar_duración(row)

    def agregar_quehacer(self, nombre, categoría: CategoríaQuehaceres, flags=None, /):
        """
        Método que agrega un nuevo quehacer hecho (se barrió, sacó la basura, etc),
        con la posibilidad de incorporar flags al mismo (por ahora, únicamente para
        las acciones "barrer", "limpiar" y "trapear")
        """
        # Chequea que los flags sean válidos
        if error := self.chequear_flags(self.lista_flags_ubicaciones, flags):
            return error

        # Definiendo variables
        ultima_row = self.quehaceres.row_values(len(self.quehaceres.col_values(1)))
        num_ultima_row = len(self.quehaceres.col_values(1))
        col_categoría = categoría.value[0] + 1
        celda = self.quehaceres.cell(num_ultima_row, col_categoría).value
        
        presentes = self.procesar_presentes(celda)
        usuarix = [nombre]
        otrx = []
        
        respuesta = ""
        
        # Itera sobre las listas(nombre - flags) dentro de la lista de presentes
        # determina quién es usuarix y quién es otrx
        for presente in presentes:
            if nombre in presente[0]:
                usuarix = presente
                print("El usuario estaba en [presentes]")
            else:
                otrx = presente
        # Si el usuarix está entre lxs presentes(ya está anotadx) y no hay flags,
        # al no haber nada que agregar, devuelve que ya estaba anotadx.
        if usuarix in presentes and not flags:
            mensaje = f"⚠️ Ya había anotado que {usuarix[0]} se encargó de {categoría.value[1]} hoy!"
            if categoría.value[3] == 1:
                mensaje += ("\n\n💡 Acordate de que podés preguntarme por <i>flags</i> o <i>ubicaciones</i>"
                                " para revisar qué flags de ubiaciones hay, si querés ser más específicx! ;)")
            return mensaje
        # Intenta obtener la fecha de la columna, y si no lo consigue la deja vacía
        try:
            fecha_row = datetime.strptime(ultima_row[0], "%Y/%m/%d").date()
        except ValueError:
            fecha_row = None
        # Agrega row del día de hoy si no existía
        if fecha_row != date.today():
            fecha_hoy = date.today().strftime("%Y/%m/%d")
            self.quehaceres.update_cell(num_ultima_row + 1, 1, fecha_hoy)
        else:
            if fecha_row: fecha_hoy = fecha_row.strftime("%Y/%m/%d")
        # Chequea si hay flags, arma la string para el mensaje de respuesta 
        # y la secuencia de flags
        mensaje_flags, mensaje_preexistentes, string_celda = self.procesar_flags(flags, 
                                                            self.lista_flags_ubicaciones, usuarix, otrx)
        # Si hay flags ingresadas, pero no hay un mensaje de nuevas flags generado,
        # devuelve que ya hay alguien anotadx que hizo esa acción con esas flags.
        if flags and not mensaje_flags:
            return f"❗ Al parecer, alguien ya se anotó hoy haciendo eso en todas esas ubicaciones 😕"

        respuesta += (f"✅ Ahí anoté que {nombre} se encargó de {categoría.value[1]}"
                    f"{mensaje_flags if mensaje_flags else ""} hoy {fecha_hoy}.")
        if not flags and categoría.value[3] == 1:
            respuesta += ("\n\n💡 Acordate de que podés preguntarme por <i>flags</i> o <i>ubicaciones</i>"
                            " para revisar qué flags de ubiaciones hay, si querés ser más específicx! ;)")
        if mensaje_preexistentes and mensaje_flags:
            respuesta += (f"\nPor otro lado, figura como que alguien ya se"
                                " encargó de {mensaje_preexistentes}")
        self.quehaceres.update_cell(num_ultima_row, col_categoría, string_celda)
        return respuesta

    def agregar_duración(self, row):
        """
        Recibe una lista de 4 valores de la row del regístro de víveres
        """
        ítem, cantidad, fecha_apertura, fecha_agotado = row
        fecha_apertura = datetime.strptime(fecha_apertura, "%Y/%m/%d").date()
        fecha_agotado = datetime.strptime(fecha_agotado, "%Y/%m/%d").date()
        duración = f"{abs((fecha_agotado - fecha_apertura).days)} días"
        mensaje_comienzo = ("\n\nℹ️ Agregué cuánto nos duró en esta ocasión a la sheet"
        " de duración de víveres!")
        mensaje_final = (" Si querés, ahora podrías despejar las fechas del registro de este ítem"
            " con el comando /despejarregistrado y este mismo ítem :)")
        if cantidad:
            ítem += f"({cantidad})"
        búsqueda = self.duración_víveres.find(ítem)
        if not búsqueda:
            self.duración_víveres.append_row((ítem, duración))
            return (mensaje_comienzo +
            " Como no existía esta categoría todavía, la creé." + mensaje_final)
        else:
            columna = len(self.duración_víveres.row_values(búsqueda.row)) + 1
            self.duración_víveres.update_cell(búsqueda.row, columna, duración)
            return mensaje_comienzo + mensaje_final

    ##########################################################################
    #Métodos de despeje(también son setters)
    ##########################################################################
    def despejar_lista_compras(self, categoría: CategoríaCompras):
        self.workbook.values_clear(f"'Listas de compras'!{categoría.value[2]}2:{categoría.value[2]}")

    def despejar_compras(self, compras: list[str], categoría: CategoríaCompras = None):
        #self.workbook.values_clear(f"'Listas de compras'!{categoría.value[2]}2:{categoría.value[2]}")
        compras_original = [str(x) for x in self.lista_compras.col_values(categoría.value[0] + 1)]
        print(f"Compras original: {compras_original}")
        compras_lower = [x.lower() for x in compras_original]
        print(f"Compras lower: {compras_lower}")
        compras = [compra[0].lower() + compra[1:] for compra in compras.copy()]
        print(f"Compras: {compras}")
        print(f"{"true" if "👮‍♂️" in "👮‍♂️" else "false"}")
        índices_a_eliminar = []
        compras_a_eliminar = []
        compras_no_encontradas = []
        for compra in compras.copy():
            matches = []
            matches_cantidad = 0
            for compra_lower in compras_lower:
                if compra in compra_lower:
                    print(f"Encontrado {compra} in {compras_original[compras_lower.index(compra_lower)]}")
                    matches.append(compras_lower.index(compra_lower))
                    matches_cantidad += 1

            if not matches:
                for compra_lower in compras_lower:
                    if unidecode(compra) in unidecode(compra_lower):
                        print(f"Encontrado {compra} unidecodeada in {compras_original[compras_lower.index(compra_lower)]}")
                        matches.append(compras_lower.index(compra_lower))
                        matches_cantidad += 1
                if not matches:
                    compras_no_encontradas.append(compra)
            elif matches_cantidad > 1:
                mensaje = ("Parece que encontré varios ítems en la lista con"
                    f" el parámetro {compra}:")
                for match in matches:
                    mensaje += f"\n  • {compras_original[match]}"
                return mensaje
            else:
                índices_a_eliminar.append(matches[0])
        if not índices_a_eliminar:
            return False
        else:
            índices_a_eliminar.sort(reverse=True)
            for índice in índices_a_eliminar:
                compras_a_eliminar.append(compras_original.pop(índice))
            compras_original.pop(0)
            compras_original_matrix = [[compra] for compra in compras_original]
            self.lista_compras.batch_clear([f"{categoría.value[2]}2:{categoría.value[2]}"])
            self.lista_compras.batch_update([{'range': f"{categoría.value[2]}2", 'values': compras_original_matrix}])
            lista_ítems = ", ".join(list(reversed(compras_a_eliminar)))
            mensaje = (f"Eliminados los ítems {lista_ítems} de la"
                    f"lista de compras {categoría.value[1]}! 🎉")
            if compras_no_encontradas:
                mensaje += ("\nPor otro lado, los siguientes ítems no fueron encontrados:")
                for compra in compras_no_encontradas:
                    mensaje += f"\n  • {compra}"
            return mensaje
    
    def despejar_lista_tareas(self):
        self.workbook.values_clear("'Tareas de la casa'!A2:A")

    def despejar_tarea(self, tarea):
        tareas = [x for x in self.lista_tareas.col_values(1)]
        tarea = self.buscar_ítem(tarea, self.lista_tareas)
        if isinstance(tarea, str):
            return tarea
        if not tarea:
            return False
        else:
            tarea = tarea.value
            tareas.pop(0)
            tareas.pop(tareas.index(tarea))
            self.workbook.values_clear("'Tareas de la casa'!A2:A")
            for item in tareas:
                rows = self.lista_tareas.col_values(1)
                self.lista_tareas.update_cell(len(rows) + 1, 1 , item)
            return (f"Eliminada la tarea '{tarea}' de la "
            "lista de tareas pendientes para el jueves! 🎉")

    def despejar_registrado(self, ítem):
        búsqueda = self.buscar_ítem(ítem, self.registro_compras)
        if isinstance(búsqueda, str):
            return búsqueda
        elif not búsqueda:
            return ("❗ No encontré el ítem que me especificaste en la lista"
            " de ítems registrados! 🙁")
        elif isinstance(búsqueda, gspread.cell.Cell):
            row = búsqueda.row
            self.registro_compras.batch_clear([f"C{row}:D{row}"])
            return (f"✅ Ya despejé las fechas de apertura y vencimiento "
                f"del ítem {búsqueda.value} de la lista de ítems registrados")

    ##########################################################################
    #Métodos getter
    ##########################################################################
    def get_tareas_diarias(self, _):
        tareas = self.lista_tareas.col_values(1)
        tareas.pop(0)
        if tareas:
            return f"✔️ <b><u>Lista de tareas:</u></b> \n• {"\n• ".join(tareas)}"
        else:
            return ""

    def get_lista_compras(self, categoría: CategoríaCompras):
        columna = categoría.value[0] + 1
        compras = self.lista_compras.col_values(columna)
        compras.pop(0)
        if compras:
            return (f"🛒 <b><u>Lista de compras {categoría.value[1]}:</u></b> \n"
                            f"• {"\n• ".join(compras)}")
        else:
            return ""

    def get_flags_ubicaciones(self, _):
        mensaje = "ℹ️ <b><u>Lista de flags de ubicaciones:</u></b>\n"
        # Me gustó esta list comprehension así que la guardo aunque no me sirva :(
        #mensaje += f"• {"\n• ".join([": ".join(item for item in par) for par in self.lista_flags_ubicaciones])}"
        mensaje += f"• {"\n• ".join(f"<b>{x[0]}</b>: {x[1]}" for x in self.lista_flags_ubicaciones)}"
        return mensaje.strip()

    def get_compras_registradas(self, _):
        mensaje = "📋 <b><u>Lista de compras registradas(para ver cuánto nos duran):</u></b>\n"
        compras_registradas = self.registro_compras.col_values(1)
        compras_registradas.pop(0)
        if compras_registradas:
            mensaje += f"• {"\n• ".join(compras_registradas)}"
        else:
            mensaje = "No habían compras registradas!"
        return mensaje

    def get_duración_registrada(self, compra):
        """
        Devuelve un string enlistando las últimas 5 duraciones de un cierto ítem, y su
        duración promedio
        """
        búsqueda = self.buscar_ítem(compra, self.duración_víveres)
        if isinstance(búsqueda, str):
            return búsqueda
        elif not búsqueda:
            return
        valores = self.duración_víveres.row_values(búsqueda.row)
        ítem = valores.pop(0)
        valores = [valor.split()[0] for valor in valores]
        valores = [int(valor) for valor in valores]
        try:
            últimos = valores[-5:]
        except IndexError:
            últimos = valores
        respuesta = (f"ℹ️ El ítem {ítem} nos duró "
        f"{", ".join([str(item) for item in últimos])} días "
        "las últimas veces que compramos, y contando todas las veces nos duró "
        f"un promedio de {sum(valores) / len(valores)} días.")
        return respuesta

    def get_duraciones_registrada(self, _):
        """
        Devuelve las últimas duraciones de todos los ítems registrados
        """
        df = pd.DataFrame(self.duración_víveres.get_all_values(), columns=None)
        ítems = df.iloc[:,0].tolist()
        traspuesto = df.transpose()
        duraciones = traspuesto.replace('', np.nan).ffill().iloc[-1].tolist()
        mensaje = ("📋 <b><u>Últimas duraciones de todos los ítems registrados:</u></b>")
        for x in range(len(ítems)):
            mensaje += f"\n• {ítems[x]}: {duraciones[x]}"
        return mensaje

    def get_estado_registradas(self, _):
        productos = self.registro_compras.col_values(1)
        cantidades = self.registro_compras.range(f"B2:B{len(productos)}")
        abiertos = self.registro_compras.range(f"C2:C{len(productos)}")
        agotados = self.registro_compras.range(f"D2:D{len(productos)}")
        productos.pop(0)
        print(productos)
        if not productos:
            return "Al parecer, no hay productos registrados!"
        mensaje = ("<b><u>Lista de ítems registrados y el estado en el que se "
            "encuentran:</u></b>\n"
            "<i>🟢: Abierto</i> | 🔴: <i>Agotado</i> | ⚪: <i>Sin abrir</i>\n")
        for producto in productos:
            mensaje += (f"  • <b>{producto}</b>{"("+cantidades[productos.index(producto)].value+")" if
            cantidades[productos.index(producto)].value else ""}: ")
            abierto = abiertos[productos.index(producto)]
            agotado = agotados[productos.index(producto)]
            if abierto.value and agotado.value:
                mensaje += "🔴\n"
            elif abierto.value and not agotado.value:
                mensaje += "🟢\n"
            else:
                mensaje += "⚪\n"
        return mensaje

    def get_último_quehacer(self, quehacer):
        """
        Obtiene la última fecha en la que se hizo un quehacer y la devuelve
        como un objeto datetime. Si falla, devuelve un string de error
        para enviarle al usuarix
        """
        columna = self.quehaceres.find(quehacer, case_sensitive=False)
        rows = self.quehaceres.col_values(columna.col)
        celda = self.quehaceres.cell(len(rows), 1)
        try:
            fecha = datetime.strptime(celda.value, "%Y/%m/%d")
        except ValueError:
            return f"Parece que no hay ninguna instancia del quehacer '{quehacer}' :/"
        return fecha


    ##########################################################################
    # Métodos de procesamiento de texto
    ##########################################################################
    def eliminar_emojis(self, texto):
        emoji_pattern = re.compile("["
                                       u"\U0001F600-\U0001F64F"  # emoticons
                                       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                       u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                       u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                       u"\U00002500-\U00002BEF"  # chinese char
                                       u"\U00002702-\U000027B0"
                                       u"\U00002702-\U000027B0"
                                       u"\U000024C2-\U0001F251"
                                       u"\U0001f926-\U0001f937"
                                       u"\U00010000-\U0010ffff"
                                       u"\u2640-\u2642"
                                       u"\u2600-\u2B55"
                                       u"\u200d"
                                       u"\u23cf"
                                       u"\u23e9"
                                       u"\u231a"
                                       u"\ufe0f"  # dingbats
                                       u"\u3030"
                                       "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', texto)

    def procesar_texto(self, texto: str | list[str]):
        """
        Elimina emojis y capitaliza el string o los ítems en la lista de strings.
        """
        if isinstance(texto, str):
            return self.eliminar_emojis(texto).capitalize().strip()
        else:
            return [self.eliminar_emojis(x).capitalize().strip() for x in texto]


    def procesar_registrados(self, registrados: list[str]):
        """
        Extrae los nombres de productos a registrar y sus cantidades
        (indicadas entre paréntesis) y las devuelve por separado.
        """
        productos = []
        cantidades = []
        for ítem in registrados:
            if "(" in ítem:
                producto, cantidad = ítem.split("(")
                productos.append(producto.strip().capitalize())
                cantidad = cantidad.strip()
                if cantidad.endswith(")"):
                    cantidad = cantidad[:-1]
                cantidades.append(cantidad.strip())
            else:
                productos.append(ítem.strip().capitalize())
                cantidades.append(None)
        return (productos, cantidades)

    def chequear_flags(self, lista_flags, flags=None):
        """
        Revisa que las flags incluídas en una tarea realizada estén dentro
        de la lista de flags de ubicaciones.
        """
        ch_flags = [x[0] for x in lista_flags]
        if not flags:
            return
        for ch in flags:
            if ch not in ch_flags:
                return ("Ingresaste un flag inválido. Preguntame sobre <i>flags</i> o <i> ubicaciones</i> "
                    "para ver la lista de ubicaciones y sus respectivos flags ;)")
        print(f"Recibidos los siguientes flags: {flags}")

    def procesar_presentes(self, celda):
        """
        Procesa el contenido de una celda y devuelve una lista de 'presentes',
        con listas individuales consistentes en el nombre y los flags asociados
        """
        if isinstance(celda, str):
            print("Detectada celda como str")
            presentes = [x.strip() for x in celda.split(",")]
            presentes = [x.split("(") for x in presentes.copy()]
            for presente in presentes:
                if len(presente) > 1:
                    presente[1] = presente.copy()[1][:-1]
            print(presentes)
            return presentes
        else:
            return []

    def procesar_flags(self, flags, lista_flags, usuarix, otrx):
        """
        Procesa flags recibidos y arma un str de mensaje para lx usuarix y uno
        para actualizar la celda.
        """
        # Extrae tuplas de lista_flags que corresponden a los flags pasados.
        flags_tuplas = [flag for flag in lista_flags if flags and flag[0] in flags]
        for flag in flags_tuplas:
            print(flag)
            if len(flag) > 2:
                flags_tuplas.pop(flags_tuplas.index(flag))
                for subflag in flag[2]:
                    if lista_flags[subflag] not in flags_tuplas: flags_tuplas.append(lista_flags[subflag])
                print(flags_tuplas)
        flags_nuevas = flags_tuplas.copy()
        mensaje_flags = "" 
        mensaje_preexistentes = ""
        string_celda = ""
        flags_compuestas = ""
        flags_restantes = ""
        usuarixs = (usuarix, otrx)

        for persona in usuarixs:
            flags_nuevas = self.procesar_flags_por_persona(persona, flags_nuevas)
        if otrx:
            string_celda += f"{otrx[0]}({otrx[1] if len(otrx) == 2 else ""}), "
        if flags_tuplas:
            if flags_nuevas: flags_restantes = "".join([flag[0] for flag in flags_nuevas])
            flags_compuestas = (f"({usuarix[1] if usuarix and len(usuarix) == 2 else ""}"
                            f"{flags_restantes if flags_restantes else ""})")
        string_celda += usuarix[0] + (flags_compuestas if flags_compuestas else "")
        if flags: 
            flags_preexistentes = "".join(flag for flag in flags if flag not in flags_restantes)
            if flags_restantes: mensaje_flags += self.construir_mensaje_flags(flags_restantes, flags_tuplas)
            if flags_preexistentes: mensaje_preexistentes += self.construir_mensaje_flags(flags_preexistentes, flags_tuplas)
        return (mensaje_flags, mensaje_preexistentes, string_celda)
    
    def procesar_flags_por_persona(self, usuarix, flags_tuplas):
        """
        Itera sobre las flags recibidas. Si la flag ya está presente en lx usuarix,
        o en lx otrx, la elimina de la lista de flags (flags_tuplas). Devuelve
        flags_tuplas actualizado
        """

        if not flags_tuplas:
            return flags_tuplas
        if not usuarix or len(usuarix) == 1:
            return flags_tuplas
        for flag in flags_tuplas.copy():
            if usuarix[1] and flag[0] in usuarix[1]:
                for objetivo in flags_tuplas:
                    if objetivo[0] == flag[0]:
                        flags_tuplas.pop(flags_tuplas.index(objetivo))
                # flags_tuplas.pop(flags_tuplas.index(flag[0]))
                if not flags_tuplas: break
        return flags_tuplas

    def construir_mensaje_flags(self, flags, flags_tuplas):
        mensaje = ""
        mensaje_agregado = ""

        def agregar_final(módulo):
            módulo = " y" + módulo[:-1]
            return módulo

        if not flags_tuplas:
            return mensaje
        for flag in flags_tuplas:
            if flag[0] in flags: 
                mensaje_agregado = f" {flag[1]},"
            if flag[0] in flags[-1]: mensaje_agregado = agregar_final(mensaje_agregado)
            mensaje += mensaje_agregado
            mensaje_agregado = ""
        return mensaje

    ##########################################################################
    # Misceláneos
    ##########################################################################
    def buscar_ítem(self, ítem: str, sheet: gspread.worksheet.Worksheet, columna=None):
        """
        Busca un ítem en un worksheet específico, y devuelve una string enlistando los ítems
        si encuentra varios, o el ítem en sí (un objeto Cell) si encontró uno solo.
        Si no encuentra nada, devuelve la lista vacía.
        """
        ítem = self.procesar_texto(ítem)
        ítem_regex = re.compile(r".*" + f"{ítem}" + r".*", re.IGNORECASE)
        # Da como resultado un objeto Cell o varios, sea como sea es una lista de Cell
        if columna:
            búsqueda = sheet.findall(ítem_regex, in_column=columna)
        else:
            búsqueda = sheet.findall(ítem_regex)
        if len(búsqueda) > 1:
            respuesta = "❗ Encontré varios ítems que contienen lo que enviaste: "
            for elemento in búsqueda:
                respuesta += f"\n• {elemento.value}"
            return respuesta
        elif not búsqueda:
            return búsqueda
        else:
            return búsqueda[0]

def main():
    editor = EditorSheet()
    editor.get_duraciones_registrada(None)

if __name__ == "__main__":
    main()
