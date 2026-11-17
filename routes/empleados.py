from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Empleado, Puesto
from datetime import datetime
import traceback

bp_empleados = Blueprint('empleados', __name__, url_prefix='/empleados')

@bp_empleados.route('/')
def lista():
    try:
        empleados = Empleado.query.all()
        # Usamos list.html
        return render_template('empleados/list.html', empleados=empleados)
    except Exception as e:
        traceback.print_exc()
        return f"Error en la base de datos: {e}"

@bp_empleados.route('/crear', methods=['GET', 'POST'])
def crear():
    try:
        puestos = Puesto.query.all()
    except Exception as e:
        traceback.print_exc()
        puestos = []

    if request.method == 'POST':
        try:
            fecha_str = request.form.get('fecha_contratacion')
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else None

            nuevo = Empleado(
                Nombre=request.form['nombre'],
                PuestoID=request.form.get('puesto_id') or None,
                SalarioBase=request.form['salario'],
                FechaContratacion=fecha_obj,
                Activo=True if request.form.get('activo') else False
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Empleado registrado exitosamente.', 'success')
            return redirect(url_for('empleados.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al guardar: {str(e)}", "danger")

    return render_template('empleados/form.html', puestos=puestos)