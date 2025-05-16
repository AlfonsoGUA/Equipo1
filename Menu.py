import tkinter as tk
from tkinter import font
from Adicion_Edicion import Adicion_Edicion
from Ubicacion_Asignacion import Ubicacion_Asignacion
from Mantenimiento_Estado import Mantenimiento_Estado
from Consultas import Consultas
from activos import VentanaActivos
from usuarios import VentanaUsuarios

class Menu:
    def __init__(self, root, login_window, usuario_actual):
        self.root = root
        self.login_window = login_window
        self.usuario_actual = usuario_actual
        
        self.window = tk.Toplevel(root)
        self.window.title("Menú")
        self.window.geometry("600x700")
        self.window.configure(bg="white")

        self.fuente_titulo = font.Font(family="Decotura ICG inline", size=50)
        self.fuente_general = font.Font(family="Decotura ICG", size=25)

        frame = tk.Frame(self.window, bg="white")
        frame.pack(expand=True, padx=10, pady=10)

        self.etiqueta_titulo = tk.Label(frame, text="Menú", font=self.fuente_titulo, bg="white")
        self.etiqueta_titulo.grid(row=0, column=0, padx=10, pady=10)

        row = 1
        if self.usuario_actual.get("rol") == "admin":
            self.boton0 = tk.Button(frame, text="Gestión de usuarios", font=self.fuente_general,
                                    bg="blue", fg="white", width=30, command=self.abrir_usuarios)
            self.boton0.grid(row=row, column=0, padx=10, pady=10)
            row += 1

        self.boton1 = tk.Button(frame, text="Adición y edición de activos", font=self.fuente_general,
                                bg="blue", fg="white", width=30, command=self.abrir_adicion_edicion)
        self.boton1.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.boton2 = tk.Button(frame, text="Ubicación y asignación de activos", font=self.fuente_general,
                                bg="blue", fg="white", width=30, command=self.abrir_ubicacion_asignacion)
        self.boton2.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.boton3 = tk.Button(frame, text="Mantenimiento y estado de activos", font=self.fuente_general,
                                bg="blue", fg="white", width=30, command=self.abrir_mantenimiento_estado)
        self.boton3.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.boton4 = tk.Button(frame, text="Consultas de activos", font=self.fuente_general,
                                bg="blue", fg="white", width=30, command=self.abrir_consultas)
        self.boton4.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.boton_regresar = tk.Button(frame, text="Cerrar sesión", font=self.fuente_general,
                                        bg="red", fg="white", width=30, command=self.cerrar_sesion)
        self.boton_regresar.grid(row=row, column=0, padx=10, pady=10)

    def abrir_usuarios(self):
        self.window.withdraw()
        VentanaUsuarios(self.window)

    def abrir_adicion_edicion(self):
        self.window.withdraw()
        VentanaActivos(self.window)

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
