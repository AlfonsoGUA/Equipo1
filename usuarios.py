import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from datetime import datetime

class VentanaUsuarios:
    def __init__(self, master):
        self.master = tk.Toplevel(master)
        self.master.title("Gestión de Usuarios")
        self.master.geometry("800x500")

        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["db_aplicacion"]
        self.collection = self.db["usuarios"]

        form_frame = tk.Frame(self.master)
        form_frame.pack(pady=10)

        self.etiquetas = ["Usuario", "Nombre Completo", "Contraseña", "Rol"]
        self.entradas = {}

        roles = ["admin", "usuario"]

        for i, etiqueta in enumerate(self.etiquetas):
            tk.Label(form_frame, text=etiqueta).grid(row=0, column=i, padx=5)
            if etiqueta == "Rol":
                combo = ttk.Combobox(form_frame, values=roles, state="readonly", width=15)
                combo.grid(row=1, column=i, padx=5)
                self.entradas[etiqueta] = combo
            else:
                entry = tk.Entry(form_frame, width=20, show="*" if etiqueta == "Contraseña" else "")
                entry.grid(row=1, column=i, padx=5)
                self.entradas[etiqueta] = entry

        btn_frame = tk.Frame(self.master)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Agregar Usuario", command=self.agregar_usuario, bg="green", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Guardar Cambios", command=self.guardar_cambios, bg="blue", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Eliminar Usuario", command=self.eliminar_usuario, bg="red", fg="white").pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.master, columns=self.etiquetas, show="headings", height=10)
        for et in self.etiquetas:
            self.tree.heading(et, text=et)
            self.tree.column(et, width=180)

        self.tree.pack(pady=10, fill="both", expand=True)
        self.tree.bind("<Double-1>", self.cargar_usuario_seleccionado)

        self.usuario_seleccionado = None
        self.cargar_usuarios()

        regresar_frame = tk.Frame(self.master)
        regresar_frame.pack(pady=10)
        tk.Button(regresar_frame, text="Regresar al Menú", command=self.regresar_menu, bg="gray", fg="white").pack()

    def regresar_menu(self):
        self.master.destroy()
        self.master.master.deiconify()

    def cargar_usuarios(self):
        self.tree.delete(*self.tree.get_children())
        for doc in self.collection.find():
            self.tree.insert("", "end", values=(
                doc.get("usuario", ""),
                doc.get("nombre_completo", ""),
                "*****", 
                doc.get("rol", "")
            ))

    def agregar_usuario(self):
        datos = {et: self.entradas[et].get().strip() for et in self.etiquetas}
        if not all(datos.values()):
            messagebox.showerror("Error", "Todos los campos son requeridos.")
            return

        if self.collection.find_one({"usuario": datos["Usuario"]}):
            messagebox.showerror("Error", "Ya existe un usuario con ese nombre.")
            return

        nuevo = {
            "usuario": datos["Usuario"],
            "nombre_completo": datos["Nombre Completo"],
            "contrasena": datos["Contraseña"],
            "rol": datos["Rol"],
            "fecha_creacion": datetime.utcnow().strftime("%Y-%m-%d"),
            "ultimo_login": None
        }

        self.collection.insert_one(nuevo)
        messagebox.showinfo("Éxito", "Usuario registrado exitosamente.")
        self.limpiar_campos()
        self.cargar_usuarios()

    def cargar_usuario_seleccionado(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            valores = self.tree.item(seleccion[0], "values")
            usuario = self.collection.find_one({"usuario": valores[0]})
            if usuario:
                self.usuario_seleccionado = usuario["_id"]
                self.entradas["Usuario"].delete(0, tk.END)
                self.entradas["Usuario"].insert(0, usuario["usuario"])
                self.entradas["Nombre Completo"].delete(0, tk.END)
                self.entradas["Nombre Completo"].insert(0, usuario["nombre_completo"])
                self.entradas["Contraseña"].delete(0, tk.END)
                self.entradas["Contraseña"].insert(0, usuario["contrasena"])
                self.entradas["Rol"].set(usuario["rol"])

    def guardar_cambios(self):
        if not self.usuario_seleccionado:
            messagebox.showwarning("Aviso", "Selecciona un usuario para editar.")
            return

        datos = {et: self.entradas[et].get().strip() for et in self.etiquetas}
        if not all(datos.values()):
            messagebox.showerror("Error", "Todos los campos son requeridos.")
            return

        self.collection.update_one(
            {"_id": self.usuario_seleccionado},
            {"$set": {
                "usuario": datos["Usuario"],
                "nombre_completo": datos["Nombre Completo"],
                "contrasena": datos["Contraseña"], 
                "rol": datos["Rol"]
            }}
        )

        messagebox.showinfo("Éxito", "Usuario actualizado.")
        self.usuario_seleccionado = None
        self.limpiar_campos()
        self.cargar_usuarios()

    def eliminar_usuario(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona un usuario para eliminar.")
            return

        valores = self.tree.item(seleccion[0], "values")
        usuario = valores[0]

        confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Eliminar el usuario '{usuario}'?")
        if confirmar:
            resultado = self.collection.delete_one({"usuario": usuario})
            if resultado.deleted_count:
                messagebox.showinfo("Eliminado", f"Usuario '{usuario}' eliminado.")
                self.usuario_seleccionado = None
                self.limpiar_campos()
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", f"No se encontró el usuario '{usuario}'.")

    def limpiar_campos(self):
        for campo in self.entradas.values():
            if isinstance(campo, ttk.Combobox):
                campo.set("")
            else:
                campo.delete(0, tk.END)
