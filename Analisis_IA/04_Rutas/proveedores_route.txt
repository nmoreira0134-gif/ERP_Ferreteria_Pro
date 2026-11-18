from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Proveedor
import traceback

bp_proveedores = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@bp_proveedores.route('/')
def lista():
    try:
        busqueda = request.args.get('busqueda', '')
        if busqueda:
            proveedores = Proveedor.query.filter(Proveedor.Nombre.contains(busqueda)).all()
        else:
            proveedores = Proveedor.query.all()
        return render_template('proveedores/list.html', proveedores=proveedores, busqueda=busqueda)
    except Exception as e:
        traceback.print_exc()
        return f"Error en la base de datos al cargar proveedores: {str(e)}"

@bp_proveedores.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        try:
            nuevo = Proveedor(
                Nombre=request.form['nombre'],
                Contacto=request.form.get('contacto', ''),
                Telefono=request.form.get('telefono', ''),
                Email=request.form.get('email', '')
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Proveedor creado exitosamente.', 'success')
            return redirect(url_for('proveedores.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al crear proveedor: {str(e)}", 'danger')
            
    return render_template('proveedores/form.html', proveedor=None)

@bp_proveedores.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    proveedor = Proveedor.query.get_or_404(id)
    if request.method == 'POST':
        try:
            proveedor.Nombre = request.form['nombre']
            proveedor.Contacto = request.form.get('contacto', '')
            proveedor.Telefono = request.form.get('telefono', '')
            proveedor.Email = request.form.get('email', '')
            
            db.session.commit()
            flash('Proveedor actualizado exitosamente.', 'success')
            return redirect(url_for('proveedores.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al editar proveedor: {str(e)}", 'danger')

    return render_template('proveedores/form.html', proveedor=proveedor)

@bp_proveedores.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        proveedor = Proveedor.query.get_or_404(id)
        db.session.delete(proveedor)
        db.session.commit()
        flash('Proveedor eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        flash(f"Error al eliminar proveedor: {str(e)}", 'danger')
    return redirect(url_for('proveedores.lista'))