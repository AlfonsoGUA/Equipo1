import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from datetime import datetime

class Mantenimiento_Estado:
    def __init__(self, master):
        self.master = tk.Toplevel(master)
        self.master.title("Historial de Mantenimiento")
        self.master.geometry("850x700")

        # Conexión a MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["db_aplicacion"]
        self.collection = self.db["activos"]

        # Frame de búsqueda y botón de regreso
        top_frame = tk.Frame(self.master)
        top_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(top_frame, text="Buscar activo:").pack(side="left")
        self.buscador = tk.Entry(top_frame)
        self.buscador.pack(side="left", padx=5)
        tk.Button(top_frame, text="Buscar", command=self.buscar_activos).pack(side="left")
        tk.Button(top_frame, text="Regresar al Menú", command=self.regresar_menu, bg="gray", fg="white").pack(side="right")

        # Tabla de activos
        self.tree = ttk.Treeview(self.master, columns=("Código", "Nombre", "Categoría", "Estado"), show="headings", height=8)
        for col in ("Código", "Nombre", "Categoría", "Estado"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=190)
        self.tree.pack(pady=10, fill="x", padx=10)
        self.tree.bind("<<TreeviewSelect>>", self.cargar_mantenimiento)

        # Formulario
        form_frame = tk.Frame(self.master)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Descripción del Mantenimiento:").grid(row=0, column=0, sticky="w")
        self.desc_mant = tk.Text(form_frame, width=60, height=4)
        self.desc_mant.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        tk.Label(form_frame, text="Técnico Responsable:").grid(row=2, column=0, sticky="w")
        self.tecnico = tk.Entry(form_frame, width=40)
        self.tecnico.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(self.master, text="Registrar Mantenimiento", command=self.guardar_mantenimiento, bg="green", fg="white").pack(pady=5)

        # Combobox para modificar estado
        estado_frame = tk.Frame(self.master)
        estado_frame.pack(pady=5)
        tk.Label(estado_frame, text="Modificar Estado del Activo:").pack(side="left")
        self.estado_var = tk.StringVar()
        self.estado_combo = ttk.Combobox(estado_frame, textvariable=self.estado_var, values=["Operativo", "En reparación", "Dado de baja"], state="readonly")
        self.estado_combo.pack(side="left", padx=5)
        tk.Button(estado_frame, text="Actualizar Estado", command=self.actualizar_estado, bg="blue", fg="white").pack(side="left")

        # Historial
        tk.Label(self.master, text="Historial de Mantenimientos").pack()
        self.historial = tk.Text(self.master, width=100, height=10, state="disabled")
        self.historial.pack(pady=10)

        self.codigo_seleccionado = None
        self.cargar_activos()

    def cargar_activos(self, filtro=None):
        self.tree.delete(*self.tree.get_children())
        consulta = {}
        if filtro:
            consulta = {
                "$or": [
                    {"nombre": {"$regex": filtro, "$options": "i"}},
                    {"codigo": {"$regex": filtro, "$options": "i"}}
                ]
            }

        activos = list(self.collection.find(consulta))
        if not activos and filtro:
            messagebox.showwarning("No encontrado", "No se encontró ningún activo con ese nombre o código. Verifique la información e intente de nuevo.")
            return

        for activo in activos:
            self.tree.insert("", "end", values=(
                activo.get("codigo", ""),
                activo.get("nombre", ""),
                activo.get("categoria", ""),
                activo.get("estado_actual", "")
            ))

    def buscar_activos(self):
        filtro = self.buscador.get().strip()
        self.cargar_activos(filtro=filtro)

    def cargar_mantenimiento(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        valores = self.tree.item(seleccion[0], "values")
        self.codigo_seleccionado = valores[0]

        activo = self.collection.find_one({"codigo": self.codigo_seleccionado})
        if activo:
            # Mostrar historial
            historial = activo.get("historial_mantenimiento", [])
            self.historial.config(state="normal")
            self.historial.delete("1.0", tk.END)
            if historial:
                for item in historial:
                    fecha = item.get("fecha", "")
                    desc = item.get("descripcion", "")
                    tecnico = item.get("tecnico", "")
                    self.historial.insert(tk.END, f"Fecha: {fecha}\nTécnico: {tecnico}\nDescripción: {desc}\n---\n")
            else:
                self.historial.insert(tk.END, "No hay historial de mantenimiento.\n")
            self.historial.config(state="disabled")

            # Mostrar estado actual en el Combobox
            estado_actual = activo.get("estado_actual", "")
            if estado_actual in self.estado_combo['values']:
                self.estado_var.set(estado_actual)
            else:
                self.estado_var.set("")

    def guardar_mantenimiento(self):
        if not self.codigo_seleccionado:
            messagebox.showerror("Error", "Selecciona un activo para registrar mantenimiento.")
            return

        descripcion = self.desc_mant.get("1.0", tk.END).strip()
        tecnico = self.tecnico.get().strip()

        if not descripcion or not tecnico:
            messagebox.showerror("Error", "Todos los campos son requeridos.")
            return

        nuevo_mantenimiento = {
            "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "descripcion": descripcion,
            "tecnico": tecnico
        }

        resultado = self.collection.update_one(
            {"codigo": self.codigo_seleccionado},
            {"$push": {"historial_mantenimiento": nuevo_mantenimiento}}
        )

        if resultado.modified_count:
            messagebox.showinfo("Éxito", "Mantenimiento registrado correctamente.")
            self.desc_mant.delete("1.0", tk.END)
            self.tecnico.delete(0, tk.END)
            self.cargar_mantenimiento(None)
        else:
            messagebox.showerror("Error", "No se pudo actualizar el historial.")

    def actualizar_estado(self):
        if not self.codigo_seleccionado:
            messagebox.showerror("Error", "Selecciona un activo para actualizar el estado.")
            return

        nuevo_estado = self.estado_var.get()
        if nuevo_estado not in ["Operativo", "En reparación", "Dado de baja"]:
            messagebox.showerror("Error", "Selecciona un estado válido.")
            return

        resultado = self.collection.update_one(
            {"codigo": self.codigo_seleccionado},
            {"$set": {"estado_actual": nuevo_estado}}
        )

        if resultado.modified_count:
            messagebox.showinfo("Éxito", "Estado actualizado correctamente.")
            self.cargar_activos()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el estado.")

    def regresar_menu(self):
        self.master.destroy()
        self.master.master.deiconify()
