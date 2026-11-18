import traceback
from flask import Blueprint, render_template
from database import get_connection

bp_usuarios = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@bp_usuarios.route('/')
def lista():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Consulta a la tabla Usuarios
        cursor.execute("""
            SELECT UsuarioID, Nombre, Usuario, Rol, Activo 
            FROM Usuarios 
            ORDER BY Nombre
        """)
        usuarios = cursor.fetchall()
        conn.close()
        
        return render_template('usuarios/lista.html', usuarios=usuarios)
    except Exception as e:
        traceback.print_exc()
        return f"Error en la base de datos: {e}"