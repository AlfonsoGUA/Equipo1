import tkinter as tk
from tkinter import ttk, messagebox, font
from pymongo import MongoClient
from datetime import datetime

class Mantenimiento_Estado:
    def __init__(self, master):
        self.master = tk.Toplevel(master)
        self.master.title("Historial de Mantenimiento")
        self.master.geometry("1000x700")

        # Fuentes personalizadas
        self.fuente_titulo = font.Font(family="Decotura ICG inline", size=28)
        self.fuente_general = font.Font(family="Decotura ICG", size=14)

        # Conexión a MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["db_aplicacion"]
        self.collection = self.db["activos"]

        # Frame de búsqueda y botón de regreso
        top_frame = tk.Frame(self.master)
        top_frame.pack(pady=5, padx=10, fill="x")

        tk.Label(top_frame, text="Buscar Activo:", font=self.fuente_general).pack(side="left")
        self.buscador = tk.Entry(top_frame, font=self.fuente_general)
        self.buscador.pack(side="left", padx=5)
        tk.Button(top_frame, text="Buscar", command=self.buscar_activos, font=self.fuente_general).pack(side="left")
        tk.Button(top_frame, text="Regresar al Menú", command=self.regresar_menu, bg="gray", fg="white", font=self.fuente_general).pack(side="right")

        # Tabla de activos
        self.tree = ttk.Treeview(self.master, columns=("Código", "Nombre", "Categoría", "Estado"), show="headings", height=8)
        for col in ("Código", "Nombre", "Categoría", "Estado"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=230)
        self.tree.pack(pady=10, fill="x", padx=10)
        self.tree.bind("<<TreeviewSelect>>", self.cargar_mantenimiento)

        # Formulario
        form_frame = tk.Frame(self.master)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Descripción del Mantenimiento:", font=self.fuente_titulo).grid(row=0, column=0, sticky="w", columnspan=2)
        self.desc_mant = tk.Text(form_frame, width=60, height=4, font=self.fuente_general)
        self.desc_mant.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        tk.Label(form_frame, text="Técnico Responsable:", font=self.fuente_titulo).grid(row=2, column=0, sticky="w", columnspan=2)
        self.tecnico = tk.Entry(form_frame, font=self.fuente_general, width=50)
        self.tecnico.grid(row=3, column=0, columnspan=2, pady=5)

        tk.Button(form_frame, text="Registrar Mantenimiento", command=self.registrar_mantenimiento, bg="green", fg="white", font=self.fuente_general).grid(row=4, column=0, columnspan=2, pady=10)

        # Cambio de estado
        estado_frame = tk.Frame(self.master)
        estado_frame.pack(pady=10)

        tk.Label(estado_frame, text="Modificar Estado del Activo:", font=self.fuente_titulo).grid(row=0, column=0, sticky="w")
        self.estado_var = tk.StringVar()
        self.estado_dropdown = ttk.Combobox(estado_frame, textvariable=self.estado_var, values=["Operativo", "Inactivo", "Mantenimiento"], font=self.fuente_general)
        self.estado_dropdown.grid(row=0, column=1, padx=5)
        tk.Button(estado_frame, text="Actualizar Estado", command=self.actualizar_estado, bg="blue", fg="white", font=self.fuente_general).grid(row=0, column=2, padx=10)

        self.cargar_todos_activos()

    def buscar_activos(self):
        query = self.buscador.get()
        filtro = {"$or": [{"nombre": {"$regex": query, "$options": "i"}}, {"codigo": {"$regex": query, "$options": "i"}}]}
        resultados = self.collection.find(filtro)
        self.tree.delete(*self.tree.get_children())
        for activo in resultados:
            self.tree.insert("", "end", values=(activo.get("codigo"), activo.get("nombre"), activo.get("categoria"), activo.get("estado")))

    def cargar_todos_activos(self):
        self.tree.delete(*self.tree.get_children())
        for activo in self.collection.find():
            self.tree.insert("", "end", values=(activo.get("codigo"), activo.get("nombre"), activo.get("categoria"), activo.get("estado")))

    def cargar_mantenimiento(self, event):
        seleccionado = self.tree.focus()
        valores = self.tree.item(seleccionado, "values")
        if valores:
            self.codigo_seleccionado = valores[0]

    def registrar_mantenimiento(self):
        if not hasattr(self, 'codigo_seleccionado'):
            messagebox.showwarning("Advertencia", "Seleccione un activo primero.")
            return

        descripcion = self.desc_mant.get("1.0", tk.END).strip()
        tecnico = self.tecnico.get().strip()

        if not descripcion or not tecnico:
            messagebox.showwarning("Advertencia", "Complete todos los campos.")
            return

        mantenimiento = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "descripcion": descripcion,
            "tecnico": tecnico
        }

        self.collection.update_one(
            {"codigo": self.codigo_seleccionado},
            {"$push": {"historial_mantenimiento": mantenimiento}}
        )

        messagebox.showinfo("Éxito", "Mantenimiento registrado correctamente.")
        self.desc_mant.delete("1.0", tk.END)
        self.tecnico.delete(0, tk.END)

    def actualizar_estado(self):
        if not hasattr(self, 'codigo_seleccionado'):
            messagebox.showwarning("Advertencia", "Seleccione un activo primero.")
            return

        nuevo_estado = self.estado_var.get()
        if not nuevo_estado:
            messagebox.showwarning("Advertencia", "Seleccione un estado.")
            return

        self.collection.update_one({"codigo": self.codigo_seleccionado}, {"$set": {"estado": nuevo_estado}})
        messagebox.showinfo("Éxito", "Estado actualizado correctamente.")
        self.cargar_todos_activos()

    def regresar_menu(self):
        self.master.destroy()
        self.master.master.deiconify()