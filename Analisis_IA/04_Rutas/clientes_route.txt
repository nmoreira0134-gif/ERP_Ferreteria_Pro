from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Cliente
import traceback

bp_clientes = Blueprint('clientes', __name__, url_prefix='/clientes')

@bp_clientes.route('/')
def lista():
    try:
        busqueda = request.args.get('busqueda', '')
        if busqueda:
            clientes = Cliente.query.filter(Cliente.Nombre.contains(busqueda)).all()
        else:
            clientes = Cliente.query.all()
        return render_template('clientes/list.html', clientes=clientes, busqueda=busqueda)
    except Exception as e:
        traceback.print_exc()
        return f"Error en la base de datos al cargar clientes: {str(e)}"

@bp_clientes.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        try:
            nuevo = Cliente(
                Nombre=request.form['nombre'],
                Telefono=request.form.get('telefono', ''),
                Email=request.form.get('email', ''),
                Genero=request.form.get('genero', '')
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Cliente creado exitosamente.', 'success')
            return redirect(url_for('clientes.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al crear cliente: {str(e)}", 'danger')
            
    return render_template('clientes/form.html', cliente=None)

@bp_clientes.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        try:
            cliente.Nombre = request.form['nombre']
            cliente.Telefono = request.form.get('telefono', '')
            cliente.Email = request.form.get('email', '')
            cliente.Genero = request.form.get('genero', '')
            
            db.session.commit()
            flash('Cliente actualizado exitosamente.', 'success')
            return redirect(url_for('clientes.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al editar cliente: {str(e)}", 'danger')

    return render_template('clientes/form.html', cliente=cliente)

@bp_clientes.route('/eliminar/<int:id>')
def eliminar(id):
    try:
        cliente = Cliente.query.get_or_404(id)
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        flash(f"Error al eliminar cliente: {str(e)}", 'danger')
    return redirect(url_for('clientes.lista'))