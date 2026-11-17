from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Empleado
import traceback
from datetime import datetime

bp_empleados = Blueprint('empleados', __name__, url_prefix='/empleados')

@bp_empleados.route('/')
def lista():
    try:
        busqueda = request.args.get('busqueda', '')
        if busqueda:
            empleados = Empleado.query.filter(Empleado.Nombre.contains(busqueda)).all()
        else:
            empleados = Empleado.query.all()
        return render_template('empleados/list.html', empleados=empleados, busqueda=busqueda)
    except Exception as e:
        traceback.print_exc()
        return f"Error en la base de datos al cargar empleados: {str(e)}"

@bp_empleados.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        try:
            fecha_str = request.form.get('fecha_contratacion')
            fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else None
            
            nuevo = Empleado(
                Nombre=request.form['nombre'],
                PuestoID=request.form.get('puesto_id') or None,
                SalarioBase=request.form.get('salario_base') or 0.00,
                FechaContratacion=fecha_dt,
                Activo=bool(request.form.get('activo'))
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Empleado creado exitosamente.', 'success')
            return redirect(url_for('empleados.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al crear empleado: {str(e)}", 'danger')
            
    return render_template('empleados/form.html', empleado=None)

@bp_empleados.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    empleado = Empleado.query.get_or_404(id)
    if request.method == 'POST':
        try:
            fecha_str = request.form.get('fecha_contratacion')
            
            empleado.Nombre = request.form['nombre']
            empleado.PuestoID = request.form.get('puesto_id') or None
            empleado.SalarioBase = request.form.get('salario_base') or 0.00
            if fecha_str:
                empleado.FechaContratacion = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            empleado.Activo = bool(request.form.get('activo'))
            
            db.session.commit()
            flash('Empleado actualizado exitosamente.', 'success')
            return redirect(url_for('empleados.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al editar empleado: {str(e)}", 'danger')

    return render_template('empleados/form.html', empleado=empleado)

@bp_empleados.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        empleado = Empleado.query.get_or_404(id)
        db.session.delete(empleado)
        db.session.commit()
        flash('Empleado eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        flash(f"Error al eliminar empleado: {str(e)}", 'danger')
    return redirect(url_for('empleados.lista'))