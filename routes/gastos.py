from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Gasto
from datetime import datetime
import traceback

bp_gastos = Blueprint('gastos', __name__, url_prefix='/gastos')

@bp_gastos.route('/')
def lista():
    try:
        # Consulta con SQLAlchemy
        gastos = Gasto.query.order_by(Gasto.Fecha.desc()).all()
        return render_template('gastos/lista.html', gastos=gastos)
    except Exception as e:
        traceback.print_exc()
        return f"Error en la base de datos: {e}"

@bp_gastos.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        try:
            # Capturamos los datos del formulario
            fecha_str = request.form.get('fecha')
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.now()
            
            monto = float(request.form['monto'])
            
            nuevo_gasto = Gasto(
                Fecha=fecha_obj,
                Categoria=request.form['categoria'],
                Descripcion=request.form.get('descripcion', ''),
                Monto=monto,
                MetodoPago=request.form.get('metodo_pago', ''),
                Proveedor=request.form.get('proveedor', ''),
                UsuarioRegistro='Admin' # O el usuario de la sesión
            )
            
            db.session.add(nuevo_gasto)
            db.session.commit()
            flash('Gasto registrado exitosamente.', 'success')
            return redirect(url_for('gastos.lista'))
            
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al guardar el gasto: {str(e)}", "danger")
            
    return render_template('gastos/form.html')