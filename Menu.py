import tkinter as tk
from tkinter import font
from Adicion_Edicion import Adicion_Edicion
from Ubicacion_Asignacion import Ubicacion_Asignacion
from Mantenimiento_Estado import Mantenimiento_Estado
from Consultas import Consultas

class Menu:
    def __init__(self, root, login_window):
        self.root = root
        self.login_window = login_window
        self.window = tk.Toplevel(root)
        self.window.title("Menú")
        self.window.geometry("600x600")
        self.window.configure(bg = "white")

        self.fuente_titulo = font.Font(family = "Decotura ICG inline", size = 50)
        self.fuente_general = font.Font(family = "Decotura ICG", size = 25)

        frame = tk.Frame(self.window, bg = "white")
        frame.pack(expand = True, padx = 10, pady = 10)

        self.etiqueta_titulo = tk.Label(frame, text = "Menú", font = self.fuente_titulo, bg = "white")
        self.etiqueta_titulo.grid(row = 0, column = 0, padx = 10, pady = 10)

        self.boton1 = tk.Button(frame, text = "Adición y edición de activos", font = self.fuente_general, bg = "blue", fg = "white", width = 30, command = self.abrir_adicion_edicion)
        self.boton1.grid(row = 1, column = 0, padx = 10, pady = 10)

        self.boton2 = tk.Button(frame, text = "Ubicación y asignación de activos", font = self.fuente_general, bg = "blue", fg = "white", width = 30, command = self.abrir_ubicacion_asignacion)
        self.boton2.grid(row = 2, column = 0, padx = 10, pady = 10)

        self.boton3 = tk.Button(frame, text = "Mantenimiento y estado de activos", font = self.fuente_general, bg = "blue", fg = "white", width = 30, command = self.abrir_mantenimiento_estado)
        self.boton3.grid(row = 3, column = 0, padx = 10, pady = 10)

        self.boton4 = tk.Button(frame, text = "Consultas de activos", font = self.fuente_general, bg = "blue", fg = "white", width = 30, command = self.abrir_consultas)
        self.boton4.grid(row = 4, column = 0, padx = 10, pady = 10)

        self.boton_regresar = tk.Button(frame, text = "Cerrar sesión", font = self.fuente_general, bg = "red", fg = "white", width = 30, command = self.cerrar_sesion)
        self.boton_regresar.grid(row = 5, column = 0, padx = 10, pady = 10)

    def abrir_adicion_edicion(self):
        self.window.withdraw()
        Adicion_Edicion(self.window)
    
    def abrir_ubicacion_asignacion(self):
        self.window.withdraw()
        Ubicacion_Asignacion(self.window)
    
    def abrir_mantenimiento_estado(self):
        self.window.withdraw()
        Mantenimiento_Estado(self.window)
    
    def abrir_consultas(self):
        self.window.withdraw()
        Consultas(self.window)

    def cerrar_sesion(self):
        self.window.destroy()
        self.login_window.limpiar_campos()
        self.root.deiconify()