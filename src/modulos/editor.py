import re
from datetime import date
from enum import Enum
import gspread
#import pandas as pd
#from tabulate import tabulate

class EditorSheet:
    """Objeto para editar el sheet de la olla"""
    def __init__(self) -> None:
        self.gc = gspread.service_account(filename="secretos/credentials.json")
        with open("secretos/wskey.txt", "r", encoding="ascii") as file:
            self.workbook = self.gc.open_by_key(file.read().strip())
        self.lista_compras = self.workbook.worksheet("Listas de compras")
        self.lista_tareas = self.workbook.worksheet("Tareas de la casa")
        self.quehaceres = self.workbook.worksheet("Registro de quehaceres")
        self.registro_compras = self.workbook.worksheet("Registro de víveres")

    class CategoríaCompras(Enum):
        SUPERMERCADO = (0, "del súper", "A")
        VERDULERIA = (1, "de la verdu", "B")
        MENSUALES = (2, "mensuales", "C")
        JUANITO = (3, "de juanito", "D")

    class CategoríaQuehaceres(Enum):
        DIA = (0, "día", "A")
        BARRER = (1, "barrer", "B")
        TRAPEAR = (2, "trapear", "C")
        LIMPIAR = (3, "limpiar", "D")
        BASURA = (4, "sacar la basura", "E")
        CAJA = (5, "limpiar la caja de asiri", "F")
        BEBEDERO = (6, "limpiar el bebedero de asiri", "G")
        TACHO = (7, "limpiar el/los tacho/s", "H")
        LAVAR = (8, "lavar la ropa", "I")
        COLGAR = (9, "colgar la ropa lavada", "J")
        DOBLAR = (10, "doblar la ropa seca", "K")
        COMPRAS = (11, "hacer las compras", "L")
        RECICLABLES = (12, "sacar la basura reciclable a la calle", "M")

    #Métodos setter

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
            columna = 2
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
            if categoría == 1:
                sheet.update_cell(len(rows) + 1, 1, fecha_hoy)
                if cantidades and cantidades[productos_proc.index(producto)]:
                    sheet.update_cell(len(rows) + 1, 3, cantidades[productos_proc.index(producto)])
        respuesta += final_respuesta
        return respuesta 

    def agregar_compras_registradas(self, compras: list[str]):
        sheet = self.registro_compras
        rows = sheet.col_values(1)
        respuesta = "✅ Agregado "
        compras_proc = [x.capitalize() for x in compras]
        fecha_hoy = date.today().strftime("%Y/%m/%d")
        for compra in compras_proc:
            if compra in rows:
                continue
            elif compra == compras_proc[-1]:
                if len(compras_proc) == 1:
                    respuesta += f" {compra} "
                else:
                    respuesta += f"y {compra} "
            else:
                respuesta += f"{compra}, "
            rows = sheet.col_values(1)
            sheet.update_cell(len(rows) + 1, 1 , compra)
            sheet.update_cell
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
        compra = self.procesar_texto(compra)
        compra_regex = re.compile(compra)
        match modo:
            case 0:
                columna = 4
            case 1:
                columna = 5
            case _:
                columna = None
                print("Se seleccionó un número inválido para el modo de la función")
                return "Algo falló, Juan debería revisar los logs."
        compras = self.registro_compras.findall(compra_regex, in_column=2, case_sensitive=False)
        if len(compras) > 1:
            respuesta = "Encontré varios ítems que contienen lo que enviaste: \n"
            for ítem in compras:
                respuesta += f"• {ítem.value}\n"
            respuesta += "Por favor aclarame qué ítem querés que marque como abierto :)"
            return respuesta
        if compras:
            celda_compra = compras[0]
        else:
            return
        if self.registro_compras.cell(celda_compra.row, columna).value:
            return (f"❗ Parece que este ítem ya fue marcado como "
                f"{"abierto" if columna == 4 else "agotado"}!")
        fecha_hoy = date.today().strftime("%Y/%m/%d")
        self.registro_compras.update_cell(celda_compra.row, columna, fecha_hoy)
        return (f"Ahí registré que hoy, {fecha_hoy}, se "
            f"{"abrió" if columna == 4 else "agotó"} el siguiente ítem: {celda_compra.value} 😊")

    #Métodos de despeje(también son setters)

    def despejar_compras(self, categoría: CategoríaCompras):
        self.workbook.values_clear(f"'Listas de compras'!{categoría.value[2]}2:{categoría.value[2]}")

    def despejar_compra(self, compra, categoría: CategoríaCompras):
        compra = self.procesar_texto(compra)
        compras = [self.procesar_texto(x) for x in self.lista_compras.col_values(categoría.value[0] + 1)]
        print(compras)
        if compra in compras:
            compras.pop(0)
            compras.pop(compras.index(compra))
            self.workbook.values_clear(f"'Listas de compras'!{categoría.value[2]}2:{categoría.value[2]}")
            for item in compras:
                rows = self.lista_compras.col_values(categoría.value[0] + 1)
                self.lista_compras.update_cell(len(rows) + 1, 1 , item)
            return True
        else:
            return False
    
    def despejar_tareas(self):
        self.workbook.values_clear("'Tareas de la casa'!A2:A")

    def despejar_tarea(self, tarea):
        tarea = self.procesar_texto(tarea)
        tareas = [self.procesar_texto(x) for x in self.lista_tareas.col_values(1)]
        if tarea in tareas:
            tareas.pop(0)
            tareas.pop(tareas.index(tarea))
            self.workbook.values_clear("'Tareas de la casa'!A2:A")
            for item in tareas:
                rows = self.lista_tareas.col_values(1)
                self.lista_tareas.update_cell(len(rows) + 1, 1 , item)
            return True
        else:
            return False
    #Métodos getter

    def get_tareas_diarias(self, _):
        tareas = self.lista_tareas.col_values(1)
        tareas.pop(0)
        if tareas:
            return f"<b><u>Lista de tareas:</u></b> \n• {"\n• ".join(tareas)}"
        else:
            return ""

    def get_lista_compras(self, categoría: CategoríaCompras):
        columna = categoría.value[0] + 1
        compras = self.lista_compras.col_values(columna)
        compras.pop(0)
        if compras:
            return f"<b><u>Lista de compras {categoría.value[1]}:</u></b> \n• {"\n• ".join(compras)}"
        else:
            return ""

    # Métodos de procesamiento de texto

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

    def procesar_texto(self, texto):
        return self.eliminar_emojis(texto).capitalize().strip()

    def procesar_registrados(self, registrados: list[str]):
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


def main():
    editor = EditorSheet()
    print(editor.get_tareas_diarias())
    print()
    print(editor.get_lista_compras(editor.CategoríaCompras.SUPERMERCADO))
    print(editor.get_lista_compras(editor.CategoríaCompras.VERDULERÍA))
    print(editor.get_lista_compras(editor.CategoríaCompras.MENSUALES))
    print(editor.get_lista_compras(editor.CategoríaCompras.JUANITO))

if __name__ == "__main__":
    main()
