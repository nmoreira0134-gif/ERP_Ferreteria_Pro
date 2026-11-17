from flask import Blueprint, render_template, request
from models import db, Producto, MovimientosInventario
from sqlalchemy import func
import traceback

bp_inventario = Blueprint('inventario', __name__, url_prefix='/inventario')

@bp_inventario.route('/')
def lista():
    try:
        # Consulta corregida: Solo sumamos la columna Cantidad (positivas para entradas, negativas para salidas)
        stock_calculado = db.session.query(
            MovimientosInventario.ProductoID,
            func.sum(MovimientosInventario.Cantidad).label('stock_total')
        ).group_by(MovimientosInventario.ProductoID).all()

        dict_stock = {row.ProductoID: row.stock_total for row in stock_calculado}
        productos = Producto.query.all()

        return render_template('inventario/list.html', productos=productos, dict_stock=dict_stock)
    except Exception as e:
        traceback.print_exc()
        return f"Error al calcular el inventario: {str(e)}"

@bp_inventario.route('/movimientos')
def movimientos():
    try:
        movs = MovimientosInventario.query.order_by(MovimientosInventario.Fecha.desc()).limit(100).all()
        return render_template('inventario/movimientos.html', movimientos=movs)
    except Exception as e:
        traceback.print_exc()
        return f"Error al cargar el kardex: {str(e)}"