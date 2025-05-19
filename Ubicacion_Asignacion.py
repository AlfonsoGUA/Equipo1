import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

class Ubicacion_Asignacion:
    def __init__(self, parent_menu):
        self.parent_menu = parent_menu
        self.window = tk.Toplevel(parent_menu)
        self.window.title("Ubicación y asignación de activos")
        self.window.geometry("800x600")
        self.window.configure(bg="white")
        self.window.protocol("WM_DELETE_WINDOW", self.regresar)

        # Conexión a MongoDB
        self.cliente = MongoClient("mongodb://localhost:27017/")
        self.db = self.cliente["db_aplicacion"]
        self.collection = self.db["activos"]

        self.departamentos = {
            "Sistemas": ["Oficina 101", "Oficina 102"],
            "Recursos Humanos": ["Oficina 201", "Oficina 202"],
            "Finanzas": ["Oficina 301"],
        }

        self.puestos = {
            "Sistemas": ["Técnico", "Administrador"],
            "Recursos Humanos": ["Asistente", "Jefe"],
            "Finanzas": ["Contador", "Analista"]
        }

        self.crear_widgets()
        self.cargar_datos()

    def crear_widgets(self):
        
        self.etiqueta_titulo = tk.Label(self.window, text="Ubicación y asignación", bg="white", font=("Decotura ICG inline", 30)).grid(row=0, column=0, columnspan=8, padx=10, pady=10)
        
        self.tree = ttk.Treeview(self.window, columns=("codigo", "nombre", "ubicacion", "asignado_a"), show="headings", height=5)
        for col, text in zip(("codigo", "nombre", "ubicacion", "asignado_a"), ("Código", "Nombre", "Ubicación actual", "Asignado a")):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=175)
        self.tree.grid(row=1, column=0, columnspan=6, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=6, sticky='ns', padx=10, pady=10)

        labels = [
            ("Ubicación del activo", 2, 2), 
            ("Departamento", 3, 1), ("Oficina", 3, 2), ("Fecha de asignación", 3, 3),
            ("Responsable del activo", 5, 2), 
            ("Nombre", 6, 0), ("Depto. al que pertenece", 6, 1), ("Puesto", 6, 2), ("Teléfono", 6, 3), ("Correo", 6, 4)
        ]
        for text, r, c in labels:
            tk.Label(self.window, text=text, bg="white", font=("Decotura ICG", 15)).grid(row=r, column=c, padx=10, pady=10)

        self.combo_departamento = ttk.Combobox(self.window, values=list(self.departamentos.keys()), width=15, font=("Decotura ICG", 15))
        self.combo_departamento.grid(row=4, column=1, padx=10, pady=10)
        self.combo_departamento.bind("<<ComboboxSelected>>", self.actualizar_oficinas)

        self.combo_oficina = ttk.Combobox(self.window, width=15, font=("Decotura ICG", 15))
        self.combo_oficina.grid(row=4, column=2, padx=10, pady=10)

        self.entry_fecha = tk.Entry(self.window, background="lightgray", width=15, font=("Decotura ICG", 15))
        self.entry_fecha.grid(row=4, column=3, padx=10, pady=10)

        self.entry_nombre = tk.Entry(self.window, background="lightgray", width=15, font=("Decotura ICG", 15))
        self.entry_nombre.grid(row=7, column=0, padx=10, pady=10)

        self.combo_depto_responsable = ttk.Combobox(self.window, values=list(self.departamentos.keys()), width=15, font=("Decotura ICG", 15))
        self.combo_depto_responsable.grid(row=7, column=1, padx=10, pady=10)
        self.combo_depto_responsable.bind("<<ComboboxSelected>>", self.actualizar_puestos)

        self.combo_puesto = ttk.Combobox(self.window, width=15, font=("Decotura ICG", 15))
        self.combo_puesto.grid(row=7, column=2, padx=10, pady=10)

        self.entry_telefono = tk.Entry(self.window, background="lightgray", width=15, font=("Decotura ICG", 15))
        self.entry_telefono.grid(row=7, column=3, padx=10, pady=10)

        self.entry_correo = tk.Entry(self.window, background="lightgray", width=15, font=("Decotura ICG", 15))
        self.entry_correo.grid(row=7, column=4, padx=10, pady=10)

        tk.Button(self.window, text="Asignar activo", bg="green", fg="white", font=("Decotura ICG", 15),
                  command=self.asignar_activo, width=15).grid(row=8, column=0, padx=10, pady=10)

        tk.Button(self.window, text="Actualizar info.", bg="blue", fg="white", font=("Decotura ICG", 15),
                  command=self.actualizar_info, width=15).grid(row=8, column=1, padx=10, pady=10)

        tk.Button(self.window, text="Devolver activo", bg="red", fg="white", font=("Decotura ICG", 15),
                  command=self.devolver_activo, width=15).grid(row=8, column=2, padx=10, pady=10)

        tk.Button(self.window, text="Regresar", bg="red", fg="white", font=("Decotura ICG", 15),
                  command=self.regresar, width=15).grid(row=8, column=4, padx=10, pady=10)

        self.tree.bind("<<TreeviewSelect>>", self.mostrar_datos_activo)

    def cargar_datos(self):
        self.tree.delete(*self.tree.get_children())
        for doc in self.collection.find():
            codigo = doc.get("codigo", "")
            nombre = doc.get("nombre", "")
            ubicacion = doc.get("ubicacion_actual", {})
            asignado = doc.get("asignado_a", {})
            self.tree.insert("", "end", iid=str(doc["_id"]), values=(
                codigo,
                nombre,
                ubicacion.get("departamento", "Disponible") if ubicacion else "Disponible",
                asignado.get("nombre", "No asignado") if asignado else "No asignado"
            ))

    def actualizar_oficinas(self, event=None):
        depto = self.combo_departamento.get()
        oficinas = self.departamentos.get(depto, [])
        self.combo_oficina["values"] = oficinas

    def actualizar_puestos(self, event=None):
        depto = self.combo_depto_responsable.get()
        puestos = self.puestos.get(depto, [])
        self.combo_puesto["values"] = puestos

    def validar_campos(self):
        campos = [
            self.combo_departamento.get(), self.combo_oficina.get(), self.entry_fecha.get(),
            self.entry_nombre.get(), self.combo_depto_responsable.get(), self.combo_puesto.get(),
            self.entry_telefono.get(), self.entry_correo.get()
        ]
        return all(campos)

    def limpiar_campos(self):
        self.combo_departamento.set("")
        self.combo_oficina.set("")
        self.combo_oficina["values"] = []
        self.entry_fecha.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.combo_depto_responsable.set("")
        self.combo_puesto.set("")
        self.combo_puesto["values"] = []
        self.entry_telefono.delete(0, tk.END)
        self.entry_correo.delete(0, tk.END)

    def mostrar_datos_activo(self, event=None):
        seleccionado = self.tree.selection()
        if not seleccionado:
            return

        doc = self.collection.find_one({"_id": ObjectId(seleccionado[0])})
        ubicacion = doc.get("ubicacion_actual")
        asignado = doc.get("asignado_a")

        # Limpiar campos primero
        self.limpiar_campos()

        if ubicacion:
            self.combo_departamento.set(ubicacion.get("departamento", ""))
            self.actualizar_oficinas()
            self.combo_oficina.set(ubicacion.get("oficina", ""))
            self.entry_fecha.insert(0, ubicacion.get("fecha_asignacion", ""))

        if asignado:
            self.entry_nombre.insert(0, asignado.get("nombre", ""))
            self.combo_depto_responsable.set(asignado.get("departamento", ""))
            self.actualizar_puestos()
            self.combo_puesto.set(asignado.get("puesto", ""))
            self.entry_telefono.insert(0, asignado.get("telefono", ""))
            self.entry_correo.insert(0, asignado.get("correo", ""))

    def asignar_activo(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un activo.")
            return

        doc = self.collection.find_one({"_id": ObjectId(seleccionado[0])})
        if doc.get("asignado_a"):
            messagebox.showerror("Error", "El activo ya está asignado.")
            return

        if not self.validar_campos():
            messagebox.showerror("Error", "Completa todos los campos.")
            return

        ubicacion = {
            "departamento": self.combo_departamento.get(),
            "oficina": self.combo_oficina.get(),
            "fecha_asignacion": self.entry_fecha.get()
        }

        responsable = {
            "nombre": self.entry_nombre.get(),
            "departamento": self.combo_depto_responsable.get(),
            "puesto": self.combo_puesto.get(),
            "telefono": self.entry_telefono.get(),
            "correo": self.entry_correo.get()
        }

        self.collection.update_one(
            {"_id": ObjectId(seleccionado[0])},
            {"$set": {"ubicacion_actual": ubicacion, "asignado_a": responsable}}
        )
        self.cargar_datos()
        self.limpiar_campos()
        messagebox.showinfo("Éxito", "Activo asignado correctamente.")

    def actualizar_info(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un activo.")
            return

        doc = self.collection.find_one({"_id": ObjectId(seleccionado[0])})
        if not doc.get("asignado_a"):
            messagebox.showerror("Error", "Este activo aún no ha sido asignado.")
            return

        if not self.validar_campos():
            messagebox.showerror("Error", "Completa todos los campos.")
            return

        ubicacion = {
            "departamento": self.combo_departamento.get(),
            "oficina": self.combo_oficina.get(),
            "fecha_asignacion": self.entry_fecha.get()
        }

        responsable = {
            "nombre": self.entry_nombre.get(),
            "departamento": self.combo_depto_responsable.get(),
            "puesto": self.combo_puesto.get(),
            "telefono": self.entry_telefono.get(),
            "correo": self.entry_correo.get()
        }

        self.collection.update_one(
            {"_id": ObjectId(seleccionado[0])},
            {"$set": {"ubicacion_actual": ubicacion, "asignado_a": responsable}}
        )
        self.cargar_datos()
        self.limpiar_campos()
        messagebox.showinfo("Éxito", "Información actualizada correctamente.")

    def devolver_activo(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Selecciona un activo.")
            return

        self.collection.update_one(
            {"_id": ObjectId(seleccionado[0])},
            {"$set": {"ubicacion_actual": None, "asignado_a": None}}
        )
        self.cargar_datos()
        self.limpiar_campos()
        messagebox.showinfo("Éxito", "Activo devuelto correctamente.")

    def regresar(self):
        self.window.destroy()
        self.parent_menu.deiconify()
