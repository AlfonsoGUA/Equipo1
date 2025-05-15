import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from datetime import datetime

class VentanaActivos:
    def __init__(self, master):
        self.master = tk.Toplevel(master)  
        self.master.title("Gestión de Activos")
        self.master.geometry("800x600")

        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["db_aplicacion"]
        self.collection = self.db["activos"]

        form_frame = tk.Frame(self.master)
        form_frame.pack(pady=10)

        self.etiquetas = ["Código", "Nombre", "Descripción", "Categoría", "Estado"]
        self.entradas = {}

        categorias = ["Electrónica", "Computación", "Deportes", "Mobiliario", "Otro"]
        estados = ["Operativo", "Mantenimiento", "Inactivo"]

        for i, etiqueta in enumerate(self.etiquetas):
            tk.Label(form_frame, text=etiqueta).grid(row=0, column=i, padx=5)
            if etiqueta == "Categoría":
                combo = ttk.Combobox(form_frame, values=categorias, state="readonly", width=15)
                combo.grid(row=1, column=i, padx=5)
                self.entradas[etiqueta] = combo
            elif etiqueta == "Estado":
                combo = ttk.Combobox(form_frame, values=estados, state="readonly", width=15)
                combo.grid(row=1, column=i, padx=5)
                self.entradas[etiqueta] = combo
            else:
                entry = tk.Entry(form_frame, width=15)
                entry.grid(row=1, column=i, padx=5)
                self.entradas[etiqueta] = entry

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Agregar Activo", command=self.agregar_activo, bg="green", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Guardar Cambios", command=self.guardar_cambios, bg="blue", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar Activo", command=self.eliminar_activo, bg="red", fg="white").pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.master, columns=self.etiquetas, show="headings", height=10)
        for et in self.etiquetas:
            self.tree.heading(et, text=et)
            self.tree.column(et, width=140)

        self.tree.pack(pady=10, fill="both", expand=True)
        self.tree.bind("<Double-1>", self.cargar_activo_seleccionado)

        self.activo_seleccionado = None
        self.cargar_activos()

        regresar_frame = tk.Frame(self.master)
        regresar_frame.pack(pady=10)
        tk.Button(regresar_frame, text="Regresar al Menú", command=self.regresar_menu, bg="gray", fg="white").pack()

    def regresar_menu(self):
        self.master.destroy()  
        self.master.master.deiconify() 

    def cargar_activos(self):
        self.tree.delete(*self.tree.get_children())
        for doc in self.collection.find():
            self.tree.insert("", "end", values=(
                doc.get("codigo", ""),
                doc.get("nombre", ""),
                doc.get("descripcion", ""),
                doc.get("categoria", ""),
                doc.get("estado_actual", "")
            ))

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
        self.cargar_activos()

    def cargar_activo_seleccionado(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            valores = self.tree.item(seleccion[0], "values")
            activo = self.collection.find_one({"codigo": valores[0]})
            if activo:
                self.activo_seleccionado = activo["_id"]
                self.entradas["Código"].delete(0, tk.END)
                self.entradas["Código"].insert(0, activo["codigo"])
                self.entradas["Nombre"].delete(0, tk.END)
                self.entradas["Nombre"].insert(0, activo["nombre"])
                self.entradas["Descripción"].delete(0, tk.END)
                self.entradas["Descripción"].insert(0, activo["descripcion"])
                self.entradas["Categoría"].set(activo["categoria"])
                self.entradas["Estado"].set(activo["estado_actual"])

    def guardar_cambios(self):
        if not self.activo_seleccionado:
            messagebox.showwarning("Aviso", "Selecciona un activo para editar.")
            return

        datos = {et: self.entradas[et].get().strip() for et in self.etiquetas}
        if not all(datos.values()):
            messagebox.showerror("Error", "Todos los campos son requeridos.")
            return

        self.collection.update_one(
            {"_id": self.activo_seleccionado},
            {"$set": {
                "codigo": datos["Código"],
                "nombre": datos["Nombre"],
                "descripcion": datos["Descripción"],
                "categoria": datos["Categoría"],
                "estado_actual": datos["Estado"]
            }}
        )

        messagebox.showinfo("Éxito", "Activo actualizado.")
        self.activo_seleccionado = None
        self.limpiar_campos()
        self.cargar_activos()

    def limpiar_campos(self):
        for campo in self.entradas.values():
            if isinstance(campo, ttk.Combobox):
                campo.set("")
            else:
                campo.delete(0, tk.END)

    def eliminar_activo(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona un activo para eliminar.")
            return

        valores = self.tree.item(seleccion[0], "values")
        codigo = valores[0]

        confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar el activo con código '{codigo}'?")
        if confirmar:
            resultado = self.collection.delete_one({"codigo": codigo})
            if resultado.deleted_count:
                messagebox.showinfo("Eliminado", f"Activo '{codigo}' eliminado correctamente.")
                self.activo_seleccionado = None
                self.limpiar_campos()
                self.cargar_activos()
            else:
                messagebox.showerror("Error", f"No se encontró el activo '{codigo}' para eliminar.")
