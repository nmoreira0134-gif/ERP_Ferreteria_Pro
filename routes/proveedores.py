from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection

bp_proveedores = Blueprint('proveedores', __name__)

@bp_proveedores.route('/')
def lista():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ProveedorID, Nombre, Contacto, Telefono, Email, Direccion 
            FROM Proveedores 
            ORDER BY Nombre
        """)
        proveedores = cursor.fetchall()
        conn.close()
        return render_template('proveedores/lista.html', proveedores=proveedores)
    except Exception as e:
        return f"Error en la base de datos: {e}"

@bp_proveedores.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        contacto = request.form.get('contacto')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        direccion = request.form.get('direccion')

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Proveedores (Nombre, Contacto, Telefono, Email, Direccion) 
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, contacto, telefono, email, direccion))
            conn.commit()
            conn.close()

            flash('¡Proveedor registrado exitosamente!', 'success')
            return redirect(url_for('proveedores.lista'))

        except Exception as e:
            flash(f'Error al guardar: {e}', 'error')
            return redirect(url_for('proveedores.nuevo'))

    return render_template('proveedores/form.html')