from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection

bp_clientes = Blueprint('clientes', __name__)

@bp_clientes.route('/')
def lista():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ClienteID, Nombre, Telefono, Email, Genero 
            FROM Clientes 
            ORDER BY Nombre
        """)
        clientes = cursor.fetchall()
        conn.close()
        return render_template('clientes/lista.html', clientes=clientes)
    except Exception as e:
        return f"Error en la base de datos: {e}"

# NUEVA RUTA: Crear Cliente
@bp_clientes.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        # 1. Recibimos los datos del formulario HTML
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        genero = request.form.get('genero')
        
        try:
            # 2. Insertamos en SQL Server
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Clientes (Nombre, Telefono, Email, Genero) 
                VALUES (?, ?, ?, ?)
            """, (nombre, telefono, email, genero))
            conn.commit()
            conn.close()
            
            # 3. Mandamos mensaje de éxito y redirigimos a la lista
            flash('¡Cliente registrado exitosamente!', 'success')
            return redirect(url_for('clientes.lista'))
            
        except Exception as e:
            flash(f'Error al guardar: {e}', 'error')
            return redirect(url_for('clientes.nuevo'))
            
    # Si es GET, solo mostramos el formulario vacío
    return render_template('clientes/form.html')