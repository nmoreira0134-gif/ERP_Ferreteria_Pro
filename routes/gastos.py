from flask import Blueprint, render_template
from database import get_connection

bp_gastos = Blueprint('gastos', __name__)

@bp_gastos.route('/')
def lista():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Consulta a la tabla Gastos, ordenada por la más reciente
        cursor.execute("""
            SELECT GastoID, CONVERT(varchar, Fecha, 103) AS Fecha, 
                   Categoria, Descripcion, Monto, MetodoPago, Proveedor
            FROM Gastos 
            ORDER BY Fecha DESC
        """)
        gastos = cursor.fetchall()
        conn.close()
        
        return render_template('gastos/lista.html', gastos=gastos)
    except Exception as e:
        return f"Error en la base de datos: {e}"