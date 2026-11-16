from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection

bp_productos = Blueprint('productos', __name__)

@bp_productos.route('/')
def lista():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Agregamos p.UnidadMedida al final de la consulta
        cursor.execute("""
            SELECT p.ProductoID, p.Nombre, p.PrecioUnitario, prov.Nombre AS Proveedor,
                   ISNULL(i.CantidadDisponible, 0) AS Stock, p.UnidadMedida
            FROM Productos p
            LEFT JOIN Proveedores prov ON p.ProveedorID = prov.ProveedorID
            LEFT JOIN Inventario i ON p.ProductoID = i.ProductoID
            ORDER BY p.Nombre
        """)
        productos = cursor.fetchall()
        conn.close()
        return render_template('productos/lista.html', productos=productos)
    except Exception as e:
        return f"Error en la base de datos: {e}"

@bp_productos.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            nombre = request.form.get('nombre')
            precio = request.form.get('precio')
            proveedor_id = request.form.get('proveedor_id')
            unidad_medida = request.form.get('unidad_medida', 'Unidad')
            
            # Aquí está la magia: convertimos a float para aceptar 15.5 libras
            stock_inicial = float(request.form.get('stock_inicial', 0))

            # Insertamos el Producto con su Unidad de Medida
            cursor.execute("""
                INSERT INTO Productos (Nombre, PrecioUnitario, ProveedorID, UnidadMedida) 
                OUTPUT INSERTED.ProductoID
                VALUES (?, ?, ?, ?)
            """, (nombre, precio, proveedor_id if proveedor_id else None, unidad_medida))
            
            nuevo_producto_id = cursor.fetchone()[0]

            # Insertamos en el Inventario
            cursor.execute("""
                INSERT INTO Inventario (ProductoID, CantidadDisponible) 
                VALUES (?, ?)
            """, (nuevo_producto_id, stock_inicial))

            conn.commit()
            conn.close()

            flash('¡Producto registrado con su unidad de medida!', 'success')
            return redirect(url_for('productos.lista'))

        # Si es GET, traemos los proveedores
        cursor.execute("SELECT ProveedorID, Nombre FROM Proveedores ORDER BY Nombre")
        proveedores = cursor.fetchall()
        conn.close()
        
        return render_template('productos/form.html', proveedores=proveedores)

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        flash(f'Error al guardar: {e}', 'error')
        return redirect(url_for('productos.nuevo'))