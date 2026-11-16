from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection

bp_puestos = Blueprint('puestos', __name__)

@bp_puestos.route('/')
def lista():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PuestoID, Nombre, SalarioBase, Descripcion FROM Puestos ORDER BY Nombre")
        puestos = cursor.fetchall()
        conn.close()
        return render_template('puestos/lista.html', puestos=puestos)
    except Exception as e:
        return f"Error en la base de datos: {e}"

@bp_puestos.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        salario = request.form.get('salario')
        descripcion = request.form.get('descripcion')

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Puestos (Nombre, SalarioBase, Descripcion) VALUES (?, ?, ?)", (nombre, salario, descripcion))
            conn.commit()
            conn.close()
            flash('¡Puesto registrado exitosamente!', 'success')
            return redirect(url_for('puestos.lista'))
        except Exception as e:
            flash(f'Error al guardar: {e}', 'error')
            return redirect(url_for('puestos.nuevo'))

    return render_template('puestos/form.html')