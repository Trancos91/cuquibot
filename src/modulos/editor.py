import gspread
import pandas as pd
from enum import Enum
from tabulate import tabulate

class EditorSheet:
    """Objeto para editar el sheet de la olla"""
    def __init__(self) -> None:
        self.gc = gspread.service_account(filename="secretos/credentials.json")
        with open("secretos/wskey.txt", "r", encoding="ascii") as file:
            self.workbook = self.gc.open_by_key(file.read().strip())
        #self.workbook = self.gc.open_by_key("15d6vM8x00PoIdLrWmKJpemxHimsU8R-wU1eYQ5cg9cs")
        #print("Variable workbook asignada")
        self.lista_compras = self.workbook.worksheet("Lista de compras")
        self.lista_tareas = self.workbook.worksheet("Tareas de la casa")
        self.quehaceres = self.workbook.worksheet("Registro de quehaceres")

    #Métodos setter

    def agregar_compras(self, categoría: Categoría, productos: list[str]):
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

    def despejar_compras(self, categoría: Categoría):
        self.workbook.values_clear(f"'Lista de compras'!{categoría.value[2]}2:")

    def despejar_compra(self, compra, categoría: Categoría):
        compra = compra.capitalize()
        compras = self.lista_compras.col_values(categoría.value[0] + 1)
        if compra in compras:
            compras.pop(0)
            compras.pop(compras.index(compra))
            self.workbook.values_clear(f"'Listas de compras'!{categoría.value[2]}2:")
            for item in compras:
                rows = self.lista_compras.col_values(categoría.value[0] + 1)
                self.lista_compras.update_cell(len(rows) + 1, 1 , item)
            return True
        else:
            return False
    
    def despejar_tareas(self):
        self.workbook.values_clear("'Tareas de la casa'!A2:")

    def despejar_tarea(self, tarea):
        tarea = tarea.capitalize()
        tareas = self.lista_tareas.col_values(1)
        if tarea in tareas:
            tareas.pop(0)
            tareas.pop(tareas.index(tarea))
            self.workbook.values_clear("'Tareas de la casa'!A2:")
            for item in tareas:
                rows = self.lista_tareas.col_values(1)
                self.lista_tareas.update_cell(len(rows) + 1, 1 , item)
            return True
        else:
            return False
############### HASTA ACÁ EDITADO ############################################################
    #Métodos getter

    def get_asistentes(self):
        asistentes = pd.DataFrame(self.asisten.get_all_values())
        return str(tabulate(asistentes, showindex=False, tablefmt="rounded_grid"))

    def get_prox_comida(self) -> str :
        prox_jueves = self.organización.find("Próximo Jueves")
        prox_comida = self.organización.cell(prox_jueves.row, 
                                              prox_jueves.col + 1)
        return f"La próxima comida que planeamos es: {prox_comida.value}"

    def get_faltantes(self):
        faltantes = self.organización.col_values(7)
        faltantes.pop(0)
        if faltantes:
            return f"<b>Falta:</b> \n• {"\n• ".join(faltantes)}"
        else:
            return

    def get_ideas_comida(self):
        comidas = self.ideas_comida.col_values(1)
        comidas.pop(0)
        return f"<b>La lista de comidas que tenemos es:</b> \n• {"\n• ".join(comidas)}"

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

    def get_menu_rotativo(self):
        prox_mes = self.organización.find("Menú del próximo mes")
        menu_rotativo = pd.DataFrame(self.organización.get(f"B{prox_mes.row + 1}:E"))
        menu_rotativo.columns = menu_rotativo.iloc[0]
        menu_rotativo = menu_rotativo[1:]
        #No sé cómo funciona la línea de abajo kjjjj
        menu_rotativo = menu_rotativo[menu_rotativo['Día'].isna().cumsum() == 0]
        mensaje = ""
        for index, row in menu_rotativo.iterrows():
            mensaje += f"<b>• Día {row["Día"]}</b>\n"
            mensaje += f"    {row["Menú"]}\n"
        print(mensaje)
        return mensaje

    def get_pendientes_jueves(self):
        pendientes = self.organización.col_values(6)
        pendientes.pop(0)
        if pendientes:
            return (f"<b><u>Tareas pendientes para el jueves próximo:</u></b> \n"
                    f"• {"\n• ".join(pendientes)}")
        else:
            return

    def get_pendientes_grales(self):
        pendientes = self.organización.col_values(2)
        for x in range(10):
            pendientes.pop(0)
        if pendientes:
            return (f"<b><u>Tareas pendientes generales:</u></b> \n"
                    f"• {"\n• ".join(pendientes)}")
        else:
            return


    class Categoría(Enum):
        DIARIAS = (0, "diarias", "A")
        MENSUALES = (1, "mensuales", "B")
        JUANITO = (2, "de juanito", "C")


def main():
    editor = EditorSheet()
    print(editor.get_prox_comida())
    print()
    print(editor.get_ideas_comida())
    print(editor.get_menu_rotativo())
    print(editor.get_asistentes())

if __name__ == "__main__":
    main()
