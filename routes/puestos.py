from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Puesto
import traceback

bp_puestos = Blueprint('puestos', __name__, url_prefix='/puestos')

@bp_puestos.route('/')
def lista():
    try:
        puestos = Puesto.query.order_by(Puesto.Nombre).all()
        # AQUI ESTABA EL ERROR: Ahora busca lista.html (con "a")
        return render_template('puestos/lista.html', puestos=puestos)
    except Exception as e:
        traceback.print_exc()
        return f"Error en la base de datos: {e}"

@bp_puestos.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        try:
            nuevo = Puesto(
                Nombre=request.form['nombre'],
                SalarioBase=request.form['salario'],
                Descripcion=request.form.get('descripcion', '')
            )
            db.session.add(nuevo)
            db.session.commit()
            flash('Puesto registrado exitosamente.', 'success')
            return redirect(url_for('puestos.lista'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f"Error al guardar: {str(e)}", "danger")

    return render_template('puestos/form.html')