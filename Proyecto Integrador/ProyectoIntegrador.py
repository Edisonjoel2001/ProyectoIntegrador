import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime


# --------- Sección 1: Gestión de Base de Datos ---------
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('ventas.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                codigo TEXT PRIMARY KEY,
                descripcion TEXT,
                precio REAL,
                stock INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                nombre TEXT,
                cedula TEXT PRIMARY KEY,
                direccion TEXT,
                telefono TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                codigo TEXT,
                descripcion TEXT,
                cantidad INTEGER,
                precio REAL,
                total REAL,
                cliente TEXT,
                FOREIGN KEY (codigo) REFERENCES productos(codigo),
                FOREIGN KEY (cliente) REFERENCES clientes(cedula)
            )
        ''')
        self.conn.commit()

    def agregar_producto(self, codigo, descripcion, precio):
        self.cursor.execute('''
            INSERT OR REPLACE INTO productos (codigo, descripcion, precio, stock) VALUES (?, ?, ?, ?)
        ''', (codigo, descripcion, precio, 0))
        self.conn.commit()

    def actualizar_stock(self, codigo, cantidad):
        self.cursor.execute('''
            UPDATE productos SET stock = stock + ? WHERE codigo = ?
        ''', (cantidad, codigo))
        self.conn.commit()

    def registrar_cliente(self, nombre, cedula, direccion, telefono):
        self.cursor.execute('''
            INSERT OR REPLACE INTO clientes (nombre, cedula, direccion, telefono) VALUES (?, ?, ?, ?)
        ''', (nombre, cedula, direccion, telefono))
        self.conn.commit()

    def registrar_venta(self, fecha, codigo, descripcion, cantidad, precio, total, cliente):
        self.cursor.execute('''
            INSERT INTO ventas (fecha, codigo, descripcion, cantidad, precio, total, cliente) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (fecha, codigo, descripcion, cantidad, precio, total, cliente))
        self.conn.commit()

    def obtener_productos(self):
        self.cursor.execute('SELECT codigo, descripcion, precio, stock FROM productos')
        return self.cursor.fetchall()

    def obtener_clientes(self):
        self.cursor.execute('SELECT nombre, cedula, direccion, telefono FROM clientes')
        return self.cursor.fetchall()

    def obtener_ventas(self):
        self.cursor.execute('SELECT * FROM ventas')
        return self.cursor.fetchall()


# --------- Sección 2: Interfaz de Usuario Mejorada ---------
class Aplicacion:
    def __init__(self, root):
        self.db = Database()
        self.root = root
        self.root.title("Registro de Ventas")
        self.root.geometry("600x400")
        self.root.configure(bg='#f4f4f4')
        self.crear_widgets()

    def crear_widgets(self):
        frame = tk.Frame(self.root, bg='#ffffff', padx=10, pady=10)
        frame.pack(pady=20, padx=20, fill='both', expand=True)

        ttk.Label(frame, text="Menú Principal", font=("Arial", 14, "bold")).grid(row=0, column=1, pady=10)

        opciones = [
            ("Agregar Producto", self.ventana_agregar_producto),
            ("Actualizar Stock", self.ventana_actualizar_stock),
            ("Registrar Cliente", self.ventana_registrar_cliente),
            ("Registrar Venta", self.ventana_registrar_venta),
            ("Mostrar Inventario", self.ventana_mostrar_inventario),
            ("Mostrar Libro Diario", self.ventana_mostrar_libro_diario),
            ("Mostrar Clientes", self.ventana_mostrar_clientes),
            ("Finalizar Día", self.ventana_finalizar_dia)
        ]

        for i, (texto, comando) in enumerate(opciones):
            ttk.Button(frame, text=texto, command=comando, width=25).grid(row=i + 1, column=1, pady=5)

        ttk.Button(frame, text="Salir", command=self.root.quit, width=25, style="TButton").grid(row=len(opciones) + 1,
                                                                                                column=1, pady=5)

    def ventana_agregar_producto(self):
        self.crear_ventana_formulario("Agregar Producto", ["Código", "Descripción", "Precio"], self.agregar_producto)

    def agregar_producto(self, valores, ventana):
        codigo, descripcion, precio = valores
        if not codigo or not descripcion or not precio.isdigit():
            messagebox.showerror("Error", "Datos inválidos")
            return
        self.db.agregar_producto(codigo, descripcion, float(precio))
        messagebox.showinfo("Éxito", "Producto agregado")
        ventana.destroy()

    def crear_ventana_formulario(self, titulo, campos, callback):
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry("300x200")

        valores = []
        for i, campo in enumerate(campos):
            ttk.Label(ventana, text=campo).grid(row=i, column=0, padx=5, pady=5)
            entrada = ttk.Entry(ventana)
            entrada.grid(row=i, column=1, padx=5, pady=5)
            valores.append(entrada)

        ttk.Button(ventana, text="Guardar", command=lambda: callback([e.get() for e in valores], ventana)).grid(
            row=len(campos), column=1, pady=10)

    def ventana_actualizar_stock(self):
        self.crear_ventana_formulario("Actualizar Stock", ["Código", "Cantidad"], self.actualizar_stock)

    def actualizar_stock(self, valores, ventana):
        codigo, cantidad = valores
        if not codigo or not cantidad.isdigit():
            messagebox.showerror("Error", "Datos inválidos")
            return
        self.db.actualizar_stock(codigo, int(cantidad))
        messagebox.showinfo("Éxito", "Stock actualizado")
        ventana.destroy()
    # --------- Sección 3.3: Ventana de registrar cliente ---------
    def ventana_registrar_cliente(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar Cliente")

        tk.Label(ventana, text="Nombre").grid(row=0, column=0)
        tk.Label(ventana, text="Cédula").grid(row=1, column=0)
        tk.Label(ventana, text="Dirección").grid(row=2, column=0)
        tk.Label(ventana, text="Teléfono").grid(row=3, column=0)

        nombre = tk.Entry(ventana)
        cedula = tk.Entry(ventana)
        direccion = tk.Entry(ventana)
        telefono = tk.Entry(ventana)

        nombre.grid(row=0, column=1)
        cedula.grid(row=1, column=1)
        direccion.grid(row=2, column=1)
        telefono.grid(row=3, column=1)

        tk.Button(ventana, text="Registrar",
                  command=lambda: self.registrar_cliente(nombre.get(), cedula.get(), direccion.get(), telefono.get(),
                                                         ventana)).grid(row=4, column=1, padx=5, pady=10)

    def registrar_cliente(self, nombre, cedula, direccion, telefono, ventana):
        if not nombre or not cedula or not direccion or not telefono:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return


        if not cedula.isdigit() or len(cedula) != 10:
            messagebox.showerror("Error", "La cédula debe tener exactamente 10 dígitos y no puede contener letras.")
            return

        self.db.registrar_cliente(nombre, cedula, direccion, telefono)
        messagebox.showinfo("Éxito", "Cliente registrado exitosamente.")
        ventana.destroy()

    # --------- Sección 3.4: Ventana de registrar venta ---------
    def ventana_registrar_venta(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Registrar Venta")

        tk.Label(ventana, text="Código Producto").grid(row=0, column=0)
        tk.Label(ventana, text="Cantidad").grid(row=1, column=0)
        tk.Label(ventana, text="Cédula Cliente").grid(row=2, column=0)

        codigo_producto = tk.Entry(ventana)
        cantidad = tk.Entry(ventana)
        cedula_cliente = tk.Entry(ventana)

        codigo_producto.grid(row=0, column=1)
        cantidad.grid(row=1, column=1)
        cedula_cliente.grid(row=2, column=1)

        tk.Button(ventana, text="Registrar",
                  command=lambda: self.registrar_venta(codigo_producto.get(), cantidad.get(), cedula_cliente.get(),
                                                       ventana)).grid(row=3, column=1, padx=5, pady=10)

        # Mostrar productos
        productos = self.db.obtener_productos()
        tk.Label(ventana, text="Productos Disponibles").grid(row=4, column=0, columnspan=2)
        tabla_productos = ttk.Treeview(ventana, columns=("Código", "Descripción", "Precio", "Stock"), show='headings')
        tabla_productos.heading("Código", text="Código")
        tabla_productos.heading("Descripción", text="Descripción")
        tabla_productos.heading("Precio", text="Precio")
        tabla_productos.heading("Stock", text="Stock")
        tabla_productos.grid(row=5, column=0, columnspan=2)

        for producto in productos:
            tabla_productos.insert("", tk.END, values=producto)

        # Mostrar clientes
        clientes = self.db.obtener_clientes()
        tk.Label(ventana, text="Clientes Disponibles").grid(row=6, column=0, columnspan=2)
        tabla_clientes = ttk.Treeview(ventana, columns=("Nombre", "Cédula", "Dirección", "Teléfono"), show='headings')
        tabla_clientes.heading("Nombre", text="Nombre")
        tabla_clientes.heading("Cédula", text="Cédula")
        tabla_clientes.heading("Dirección", text="Dirección")
        tabla_clientes.heading("Teléfono", text="Teléfono")
        tabla_clientes.grid(row=7, column=0, columnspan=2)

        for cliente in clientes:
            tabla_clientes.insert("", tk.END, values=cliente)

    def registrar_venta(self, codigo, cantidad, cedula_cliente, ventana):
        if not codigo or not cantidad or not cedula_cliente:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return

        if not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showerror("Error", "La cantidad debe ser un número positivo.")
            return

        cantidad = int(cantidad)

        # Verificar si el producto y cliente existen
        productos = self.db.obtener_productos()
        clientes = self.db.obtener_clientes()

        producto_encontrado = False
        cliente_encontrado = False
        precio_producto = 0
        descripcion_producto = ""
        stock_producto = 0

        for prod in productos:
            if prod[0] == codigo:
                producto_encontrado = True
                precio_producto = prod[2]
                descripcion_producto = prod[1]
                stock_producto = prod[3]  # Stock actual del producto
                break

        for cli in clientes:
            if cli[1] == cedula_cliente:
                cliente_encontrado = True
                break

        if not producto_encontrado:
            messagebox.showerror("Error", "Producto no encontrado.")
            return

        if not cliente_encontrado:
            messagebox.showerror("Error", "Cliente no encontrado.")
            return

        if cantidad > stock_producto:
            messagebox.showerror("Error", "No hay suficiente stock disponible.")
            return

        # Calcular el total de la venta
        total = precio_producto * cantidad
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Registrar la venta en la base de datos
        self.db.registrar_venta(fecha, codigo, descripcion_producto, cantidad, precio_producto, total, cedula_cliente)

        # Actualizar el stock del producto
        self.db.actualizar_stock(codigo, -cantidad)  # Restar la cantidad vendida del stock

        messagebox.showinfo("Éxito", "Venta registrada exitosamente.")
        ventana.destroy()

    # --------- Sección 3.5: Ventana de mostrar inventario ---------
    def ventana_mostrar_inventario(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Mostrar Inventario")

        productos = self.db.obtener_productos()

        tabla = ttk.Treeview(ventana, columns=("Código", "Descripción", "Precio", "Stock"), show='headings')
        tabla.heading("Código", text="Código")
        tabla.heading("Descripción", text="Descripción")
        tabla.heading("Precio", text="Precio")
        tabla.heading("Stock", text="Stock")
        tabla.pack()

        for producto in productos:
            tabla.insert("", tk.END, values=producto)

    # --------- Sección 3.6: Ventana de mostrar libro diario ---------
    def ventana_mostrar_libro_diario(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Mostrar Libro Diario")

        ventas = self.db.obtener_ventas()

        tabla = ttk.Treeview(ventana,
                             columns=("","Fecha", "Código", "Descripción", "Cantidad", "Precio", "Total", "Nombre"),
                             show='headings')
        tabla.heading("Código", text="Código")
        tabla.heading("Fecha", text="Fecha")
        tabla.heading("Descripción", text="Descripción")
        tabla.heading("Cantidad", text="Cantidad")
        tabla.heading("Precio", text="Precio")
        tabla.heading("Nombre", text="Nombre")
        tabla.heading("Total", text="Total")
        tabla.pack()

        total_dia = 0

        for venta in ventas:
            tabla.insert("", tk.END, values=venta)
            total_dia += venta[6]  # Columna del total

        tk.Label(ventana, text=f"Total del Día: {total_dia:.2f}").pack()

    # --------- Sección 3.7: Ventana de mostrar clientes ---------
    def ventana_mostrar_clientes(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Mostrar Clientes")

        clientes = self.db.obtener_clientes()

        tabla = ttk.Treeview(ventana, columns=("Nombre", "Cédula", "Dirección", "Teléfono"), show='headings')
        tabla.heading("Nombre", text="Nombre")
        tabla.heading("Cédula", text="Cédula")
        tabla.heading("Dirección", text="Dirección")
        tabla.heading("Teléfono", text="Teléfono")
        tabla.pack()

        for cliente in clientes:
            tabla.insert("", tk.END, values=cliente)

    # --------- Sección 3.8: Finalizar Día ---------
    def ventana_finalizar_dia(self):
        respuesta = messagebox.askyesno("Confirmar",
                                        "¿Desea finalizar el día? Esto borrará el registro de ventas del día.")
        if respuesta:
            self.db.cursor.execute('DELETE FROM ventas')
            self.db.conn.commit()
            messagebox.showinfo("Éxito", "Día finalizado y ventas borradas.")


# --------- Sección 4: Función principal ---------
if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
