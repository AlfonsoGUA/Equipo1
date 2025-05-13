import tkinter as tk
from tkinter import font

class Consultas:
    def __init__(self, parent_menu):
        self.parent_menu = parent_menu
        self.window = tk.Toplevel(parent_menu)
        self.window.title("Consultas de activos")
        self.window.geometry("800x600")
        self.window.configure(bg = "white")

        self.fuente_titulo = font.Font(family = "Decotura ICG inline", size = 50)
        self.fuente_general = font.Font(family = "Decotura ICG", size = 25)

        frame = tk.Frame(self.window, bg = "white")
        frame.pack(expand = True, padx = 10, pady = 10)

        self.etiqueta_titulo = tk.Label(frame, text = "Consultas de activos", font = self.fuente_titulo, bg = "white")
        self.etiqueta_titulo.grid(row = 0, column = 0, padx = 10, pady = 10)
        
        #Aquí va su código
        
        self.boton_regresar = tk.Button(frame, text = "Regresar", font = self.fuente_general, bg = "red", fg = "white", width = 30, command = self.regresar)
        self.boton_regresar.grid(row = 5, column = 0, padx = 10, pady = 10)
        
        self.window.protocol("WM_DELETE_WINDOW", self.regresar)

    def regresar(self):
        self.window.destroy()
        self.parent_menu.deiconify()