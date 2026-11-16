from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_connection

bp_empleados = Blueprint('empleados', __name__)

@bp_empleados.route('/')
def lista():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.EmpleadoID, e.Nombre, p.Nombre AS Puesto, 
                   e.SalarioBase, CONVERT(varchar, e.FechaContratacion, 103) AS Fecha, e.Activo
            FROM Empleados e
            LEFT JOIN Puestos p ON e.PuestoID = p.PuestoID
            ORDER BY e.Nombre
        """)
        empleados = cursor.fetchall()
        conn.close()
        return render_template('empleados/lista.html', empleados=empleados)
    except Exception as e:
        return f"Error en la base de datos: {e}"

@bp_empleados.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            nombre = request.form.get('nombre')
            puesto_id = request.form.get('puesto_id')
            salario = request.form.get('salario')
            fecha_contratacion = request.form.get('fecha_contratacion')
            activo = 1 if request.form.get('activo') else 0

            cursor.execute("""
                INSERT INTO Empleados (Nombre, PuestoID, SalarioBase, FechaContratacion, Activo) 
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, puesto_id if puesto_id else None, salario, fecha_contratacion, activo))
            
            conn.commit()
            conn.close()

            flash('¡Empleado registrado exitosamente!', 'success')
            return redirect(url_for('empleados.lista'))

        cursor.execute("SELECT PuestoID, Nombre FROM Puestos ORDER BY Nombre")
        puestos = cursor.fetchall()
        conn.close()
        
        return render_template('empleados/form.html', puestos=puestos)

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        flash(f'Error al guardar: {e}', 'error')
        return redirect(url_for('empleados.nuevo'))

# NUEVA RUTA: Dar de baja (Borrado Lógico)
@bp_empleados.route('/baja/<int:id>')
def baja(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # En lugar de DELETE, hacemos un UPDATE para ponerlo inactivo
        cursor.execute("UPDATE Empleados SET Activo = 0 WHERE EmpleadoID = ?", (id,))
        conn.commit()
        conn.close()
        flash('Empleado dado de baja correctamente. Su historial se mantiene intacto.', 'success')
    except Exception as e:
        flash(f'Error al dar de baja: {e}', 'error')
        
    return redirect(url_for('empleados.lista'))