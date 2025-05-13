import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient
from datetime import datetime

class VentanaActivos:
    def __init__(self, master):
        self.master = tk.Toplevel(master)
        self.master.title("Gestión de Activos")
        self.master.geometry("500x450")

        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["gestion_activos"]
        self.collection = self.db["activos"]

        self.etiquetas = ["Código", "Nombre", "Descripción", "Categoría", "Estado"]
        self.entradas = {}

        for i, etiqueta in enumerate(self.etiquetas):
            tk.Label(self.master, text=etiqueta).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            self.entradas[etiqueta] = tk.Entry(self.master, width=40)
            self.entradas[etiqueta].grid(row=i, column=1, padx=10, pady=5)

        tk.Button(self.master, text="Agregar nuevo activo", command=self.agregar_activo, bg="green", fg="white").grid(row=6, column=0, padx=10, pady=10)
        tk.Button(self.master, text="Buscar/Editar activo", command=self.buscar_activo, bg="orange", fg="black").grid(row=6, column=1, padx=10, pady=10)

    def agregar_activo(self):
        datos = {et: self.entradas[et].get().strip() for et in self.etiquetas}

        if not all(datos.values()):
            messagebox.showerror("Error", "Todos los campos son requeridos.")
            return

        if self.collection.find_one({"codigo": datos["Código"]}):
            messagebox.showerror("Error", "Ya existe un activo con ese código.")
            return

        nuevo = {
            "codigo": datos["Código"],
            "nombre": datos["Nombre"],
            "descripcion": datos["Descripción"],
            "categoria": datos["Categoría"],
            "estado_actual": datos["Estado"],
            "ubicacion_actual": None,
            "asignado_a": None,
            "historial_mantenimiento": [],
            "fecha_registro": datetime.utcnow()
        }

        self.collection.insert_one(nuevo)
        messagebox.showinfo("Éxito", "Activo registrado exitosamente.")
        self.limpiar_campos()

    def buscar_activo(self):
        codigo = self.entradas["Código"].get().strip()
        if not codigo:
            messagebox.showwarning("Atención", "Ingresa un código para buscar.")
            return

        activo = self.collection.find_one({"codigo": codigo})
        if not activo:
            messagebox.showerror("No encontrado", "No se encontró un activo con ese código.")
            return

        self.entradas["Nombre"].delete(0, tk.END)
        self.entradas["Nombre"].insert(0, activo["nombre"])
        self.entradas["Descripción"].delete(0, tk.END)
        self.entradas["Descripción"].insert(0, activo["descripcion"])
        self.entradas["Categoría"].delete(0, tk.END)
        self.entradas["Categoría"].insert(0, activo["categoria"])
        self.entradas["Estado"].delete(0, tk.END)
        self.entradas["Estado"].insert(0, activo["estado_actual"])

        tk.Button(self.master, text="Guardar cambios", command=lambda: self.actualizar_activo(activo["_id"]), bg="blue", fg="white").grid(row=7, column=0, columnspan=2, pady=10)

    def actualizar_activo(self, _id):
        datos = {et: self.entradas[et].get().strip() for et in self.etiquetas}
        if not all(datos.values()):
            messagebox.showerror("Error", "Todos los campos son requeridos.")
            return

        self.collection.update_one(
            {"_id": _id},
            {"$set": {
                "nombre": datos["Nombre"],
                "descripcion": datos["Descripción"],
                "categoria": datos["Categoría"],
                "estado_actual": datos["Estado"]
            }}
        )
        messagebox.showinfo("Actualizado", "Los datos del activo se actualizaron correctamente.")

    def limpiar_campos(self):
        for campo in self.entradas.values():
            campo.delete(0, tk.END)
