import tkinter as tk
from tkinter import font, messagebox
from pymongo import MongoClient
from Menu import Menu
from datetime import datetime

class Login:
    def __init__(self, root):
        self.root = root
        self.root.title("Iniciar sesión")
        self.root.geometry("600x600")
        self.root.configure(bg="white")

        self.fuente_titulo = font.Font(family="Decotura ICG inline", size=50)
        self.fuente_general = font.Font(family="Decotura ICG", size=25)

        frame = tk.Frame(self.root, bg="white")
        frame.pack(expand=True, padx=10, pady=10)

        self.etiqueta_titulo = tk.Label(frame, text="Iniciar sesión", font=self.fuente_titulo, bg="white")
        self.etiqueta_titulo.grid(row=0, column=0, padx=10, pady=10)

        self.etiqueta_usuario = tk.Label(frame, text="Usuario", font=self.fuente_general, bg="white")
        self.etiqueta_usuario.grid(row=1, column=0, padx=10, pady=10)
        self.entrada_usuario = tk.Entry(frame, width=25, font=self.fuente_general, bg="lightgray")
        self.entrada_usuario.grid(row=2, column=0, padx=10, pady=10)

        self.etiqueta_contraseña = tk.Label(frame, text="Contraseña", font=self.fuente_general, bg="white")
        self.etiqueta_contraseña.grid(row=3, column=0, padx=10, pady=10)
        self.entrada_contraseña = tk.Entry(frame, width=25, font=self.fuente_general, bg="lightgray", show="*")
        self.entrada_contraseña.grid(row=4, column=0, padx=10, pady=10)

        self.boton_ingresar = tk.Button(frame, text="Ingresar", font=self.fuente_general, bg="green", fg="white", width=30, command=self.ingresar)
        self.boton_ingresar.grid(row=5, column=0, padx=10, pady=10)

        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["db_aplicacion"]
        self.usuarios_col = self.db["usuarios"]

    def ingresar(self):
        usuario = self.entrada_usuario.get()
        clave = self.entrada_contraseña.get()

        user_doc = self.usuarios_col.find_one({"usuario": usuario})

        if user_doc and user_doc["contrasena"] == clave:
            self.usuarios_col.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {"ultimo_login": datetime.now().isoformat()}}
            )
            self.root.withdraw()
            Menu(self.root, self, user_doc)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def limpiar_campos(self):
        self.entrada_usuario.delete(0, tk.END)
        self.entrada_contraseña.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    Login(root)
    root.mainloop()
