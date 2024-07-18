import gspread
#import pandas as pd
from enum import Enum
#from tabulate import tabulate

class EditorSheet:
    """Objeto para editar el sheet de la olla"""
    def __init__(self) -> None:
        self.gc = gspread.service_account(filename="secretos/credentials.json")
        with open("secretos/wskey.txt", "r", encoding="ascii") as file:
            self.workbook = self.gc.open_by_key(file.read().strip())
        #self.workbook = self.gc.open_by_key("15d6vM8x00PoIdLrWmKJpemxHimsU8R-wU1eYQ5cg9cs")
        #print("Variable workbook asignada")
        self.lista_compras = self.workbook.worksheet("Listas de compras")
        self.lista_tareas = self.workbook.worksheet("Tareas de la casa")
        self.quehaceres = self.workbook.worksheet("Registro de quehaceres")

    class CategoríaCompras(Enum):
        DIARIAS = (0, "diarias", "A")
        MENSUALES = (1, "mensuales", "B")
        JUANITO = (2, "de juanito", "C")

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

    #Métodos setter

    def agregar_compras(self, categoría: CategoríaCompras, productos: list[str]):
        columna = categoría.value[0] + 1
        rows = self.lista_compras.col_values(columna)
        respuesta = "✅ Agregado "
        productos_proc = [x.capitalize() for x in productos]
        for producto in productos_proc:
            if producto in rows:
                continue
            elif producto == productos_proc[-1]:
                respuesta += f"y {producto} "
            else:
                respuesta += f"{producto}, "
            rows = self.lista_compras.col_values(columna)
            self.lista_compras.update_cell(len(rows) + 1, columna , producto)
        respuesta += f"a la lista de compras de {categoría.value[1]}"
        return respuesta 

    def agregar_tareas(self, tareas: list[str]):
        rows = self.lista_tareas.col_values(1)
        respuesta = "✅ Agregado "
        tareas_proc = [x.capitalize() for x in tareas]
        for tarea in tareas_proc:
            if tarea in rows:
                continue
            elif tarea == tareas_proc[-1]:
                respuesta += f"y {tarea} "
            else:
                respuesta += f"{tarea}, "
            rows = self.lista_tareas.col_values(1)
            self.lista_tareas.update_cell(len(rows) + 1, 1 , tarea)
        respuesta += "a la lista de tareas."
        return respuesta 

    #Métodos de despeje(también son setters)

    def despejar_compras(self, categoría: CategoríaCompras):
        self.workbook.values_clear(f"'Listas de compras'!{categoría.value[2]}2:{categoría.value[2]}")

    def despejar_compra(self, compra, categoría: CategoríaCompras):
        compra = compra.capitalize()
        compras = self.lista_compras.col_values(categoría.value[0] + 1)
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
        tarea = tarea.capitalize()
        tareas = self.lista_tareas.col_values(1)
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

    def get_tareas_diarias(self):
        tareas = self.lista_tareas.col_values(1)
        tareas.pop(0)
        if tareas:
            return f"<b><u>Lista de tareas:</u></b> \n• {"\n• ".join(tareas)}"
        else:
            return

    def get_lista_compras(self, categoría: CategoríaCompras):
        columna = categoría.value[0] + 1
        compras = self.lista_compras.col_values(columna)
        compras.pop(0)
        if compras:
            return f"<b><u>Lista de compras {categoría.value[1]}:</u></b> \n• {"\n• ".join(compras)}"
        else:
            return

############### HASTA ACÁ EDITADO ############################################################

    def get_info(self, categoría):
        categoría = categoría.capitalize()
        print(f"categoría: {categoría}")
        col = self.info_útil.find(categoría)
        info = self.info_útil.col_values(col.col) if col else None
        if info:
            info.pop(0)
            return f"<b>Info útil sobre {categoría}:</b> \n• {"\n• ".join(info)}"
        else:
            return ("No encontré info útil guardada sobre esa categoría :(\n"
                "Si querés agregar info, podés usar el comando /agregar_info! Por ejemplo:\n"
                "<pre>/agregar_info arroz \"Una taza de agua por cada taza de arroz\"</pre>")


    def get_pendientes_jueves(self):
        pendientes = self.organización.col_values(6)
        pendientes.pop(0)
        if pendientes:
            return (f"<b><u>Tareas pendientes para el jueves próximo:</u></b> \n"
                    f"• {"\n• ".join(pendientes)}")
        else:
            return


def main():
    editor = EditorSheet()
    print(editor.get_tareas_diarias())
    print()
    print(editor.get_lista_compras(editor.CategoríaCompras.DIARIAS))
    print(editor.get_lista_compras(editor.CategoríaCompras.MENSUALES))
    print(editor.get_lista_compras(editor.CategoríaCompras.JUANITO))

if __name__ == "__main__":
    main()
