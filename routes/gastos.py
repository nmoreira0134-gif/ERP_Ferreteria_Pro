from flask import Blueprint, render_template
from models import Gasto

# AQUI ESTABA EL ERROR: Faltaba el url_prefix
bp_gastos = Blueprint('gastos', __name__, url_prefix='/gastos')

@bp_gastos.route('/')
def lista():
    try:
        # SQLAlchemy hace la consulta mágicamente sin escribir SQL
        gastos = Gasto.query.order_by(Gasto.Fecha.desc()).all()
        return render_template('gastos/lista.html', gastos=gastos)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error en la base de datos: {e}"