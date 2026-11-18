import os
import traceback
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
from models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://@localhost/FerreteriaDB?trusted_connection=yes&driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY','dev-insecure-key')

db.init_app(app)

# Función auxiliar para registrar módulos sin que un error detenga todo el servidor
def registrar_modulo(nombre_archivo, nombre_blueprint):
    try:
        modulo = __import__(f'routes.{nombre_archivo}', fromlist=[nombre_blueprint])
        blueprint = getattr(modulo, nombre_blueprint)
        app.register_blueprint(blueprint)
        print(f"✅ Módulo '{nombre_archivo}' registrado correctamente.")
    except Exception as e:
        traceback.print_exc()
        print(f"❌ ERROR al registrar el módulo '{nombre_archivo}': {e}")

# Registramos todos los módulos
registrar_modulo('main', 'bp_main')
registrar_modulo('productos', 'bp_productos')
registrar_modulo('clientes', 'bp_clientes')
registrar_modulo('empleados', 'bp_empleados')
registrar_modulo('facturacion', 'bp_facturacion')
registrar_modulo('proveedores', 'bp_proveedores')
registrar_modulo('inventario', 'bp_inventario')
registrar_modulo('gastos', 'bp_gastos')
registrar_modulo('puestos', 'bp_puestos')
registrar_modulo('usuarios', 'bp_usuarios')

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG','false').lower()=='true')