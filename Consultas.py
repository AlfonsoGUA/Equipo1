import tkinter as tk
from tkinter import font, ttk, filedialog, messagebox
from pymongo import MongoClient
import pandas as pd

class Consultas:
    def __init__(self, parent_menu):
        self.parent_menu = parent_menu
        self.window = tk.Toplevel(parent_menu)
        self.window.title("Consultas de activos")
        self.window.geometry("1000x700")
        self.window.configure(bg="white")

        self.fuente_general = font.Font(family="Decotura ICG", size=16)

        # Conexión MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["db_aplicacion"]
        self.collection = self.db["activos"]

        # Frame principal
        self.frame = tk.Frame(self.window, bg="white")
        self.frame.pack(expand=True, fill="both", padx=10, pady=(10, 60))

        # Opciones de consulta
        self.opciones = [
            "Activos por ubicación",
            "Activos por persona",
            "Activos en mantenimiento",
            "Fecha del último mantenimiento"
        ]
        self.opcion_var = tk.StringVar(value=self.opciones[0])

        ttk.Label(self.frame, text="Seleccione una consulta:", font=self.fuente_general).pack(pady=10)
        self.menu_opciones = ttk.OptionMenu(self.frame, self.opcion_var, self.opciones[0], *self.opciones)
        self.menu_opciones.pack()

        # Filtros de orden
        ttk.Label(self.frame, text="Ordenar por:", font=self.fuente_general).pack(pady=(15, 5))
        self.orden_var = tk.StringVar()
        self.orden_menu = ttk.Combobox(self.frame, textvariable=self.orden_var, font=self.fuente_general, state="readonly", width=40)
        self.orden_menu.pack()

        self.sentido_var = tk.StringVar(value="Ascendente")
        ttk.Radiobutton(self.frame, text="Ascendente", variable=self.sentido_var, value="Ascendente").pack()
        ttk.Radiobutton(self.frame, text="Descendente", variable=self.sentido_var, value="Descendente").pack()

        ttk.Button(self.frame, text="Consultar", command=self.realizar_consulta).pack(pady=10)
        ttk.Button(self.frame, text="Descargar CSV", command=self.descargar_csv).pack()

        # Tabla de resultados
        self.tree = ttk.Treeview(self.frame, columns=[], show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Botón regresar fijo abajo
        self.frame_inferior = tk.Frame(self.window, bg="white")
        self.frame_inferior.pack(side="bottom", fill="x", pady=10)

        self.boton_regresar = tk.Button(
            self.frame_inferior, text="Regresar al menú", font=self.fuente_general,
            bg="gray", fg="white", width=30, height=2, command=self.regresar
        )
        self.boton_regresar.pack(pady=5)

        self.resultado_actual = pd.DataFrame()
        self.window.protocol("WM_DELETE_WINDOW", self.regresar)

        self.actualizar_filtros_orden()
        self.opcion_var.trace_add("write", lambda *args: self.actualizar_filtros_orden())

    def actualizar_filtros_orden(self):
        opcion = self.opcion_var.get()
        columnas = []

        if opcion == "Activos por ubicación":
            columnas = ["Departamento", "Oficina", "Cantidad"]
        elif opcion == "Activos por persona":
            columnas = ["Nombre", "Activo", "Departamento", "Oficina", "Estado"]
        elif opcion == "Activos en mantenimiento":
            columnas = ["Código", "Nombre", "Asignado a", "Departamento", "Oficina"]
        elif opcion == "Fecha del último mantenimiento":
            columnas = ["Código", "Nombre", "Último mantenimiento"]

        self.orden_menu['values'] = columnas
        if columnas:
            self.orden_var.set(columnas[0])
        else:
            self.orden_var.set("")

    def realizar_consulta(self):
        opcion = self.opcion_var.get()
        df = pd.DataFrame()

        if opcion == "Activos por ubicación":
            datos = self.collection.aggregate([
                {"$group": {
                    "_id": {
                        "departamento": "$ubicacion_actual.departamento",
                        "oficina": "$ubicacion_actual.oficina"
                    },
                    "total": {"$sum": 1}
                }}
            ])
            df = pd.DataFrame([{
                "Departamento": d["_id"]["departamento"],
                "Oficina": d["_id"]["oficina"],
                "Cantidad": d["total"]
            } for d in datos])

        elif opcion == "Activos por persona":
            cursor = self.collection.find()
            registros = []
            for d in cursor:
                registros.append({
                    "Nombre": d.get("asignado_a", {}).get("nombre", ""),
                    "Activo": d.get("nombre", ""),
                    "Departamento": d.get("ubicacion_actual", {}).get("departamento", ""),
                    "Oficina": d.get("ubicacion_actual", {}).get("oficina", ""),
                    "Estado": d.get("estado_actual", "")
                })
            df = pd.DataFrame(registros)

        elif opcion == "Activos en mantenimiento":
            cursor = self.collection.find({"estado_actual": "mantenimiento"})
            registros = []
            for d in cursor:
                registros.append({
                    "Código": d.get("codigo", ""),
                    "Nombre": d.get("nombre", ""),
                    "Asignado a": d.get("asignado_a", {}).get("nombre", ""),
                    "Departamento": d.get("ubicacion_actual", {}).get("departamento", ""),
                    "Oficina": d.get("ubicacion_actual", {}).get("oficina", "")
                })
            df = pd.DataFrame(registros)

        elif opcion == "Fecha del último mantenimiento":
            registros = []
            for doc in self.collection.find({}, {"_id": 0, "codigo": 1, "nombre": 1, "historial_mantenimiento": 1}):
                historial = doc.get("historial_mantenimiento", [])
                ultima_fecha = max((item.get("fecha") for item in historial), default=None)
                registros.append({
                    "Código": doc.get("codigo"),
                    "Nombre": doc.get("nombre"),
                    "Último mantenimiento": pd.to_datetime(ultima_fecha).date() if ultima_fecha else "Sin registros"
                })
            df = pd.DataFrame(registros)

        # Ordenar si corresponde
        if not df.empty:
            col = self.orden_var.get()
            if col in df.columns:
                ascending = self.sentido_var.get() == "Ascendente"
                df = df.sort_values(by=col, ascending=ascending)

        self.resultado_actual = df
        self.mostrar_resultados(df)

    def mostrar_resultados(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)

        for _, row in df.iterrows():
            self.tree.insert("", tk.END, values=list(row))

    def descargar_csv(self):
        if self.resultado_actual.empty:
            messagebox.showwarning("Advertencia", "No hay datos para guardar.")
            return

        ruta = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if ruta:
            self.resultado_actual.to_csv(ruta, index=False)
            messagebox.showinfo("Éxito", "Archivo guardado correctamente.")

    def regresar(self):
        self.window.destroy()
        self.parent_menu.deiconify()
