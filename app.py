from flask import Flask, render_template
from config import Config
from routes.main import bp_main
from routes.clientes import bp_clientes
from routes.empleados import bp_empleados
from routes.gastos import bp_gastos
from routes.productos import bp_productos
from routes.proveedores import bp_proveedores
from routes.puestos import bp_puestos
from routes.usuarios import bp_usuarios
# NUEVO IMPORT
from routes.facturacion import bp_facturacion 

app = Flask(__name__)
app.config.from_object(Config)

# Registro de Blueprints
app.register_blueprint(bp_main)
app.register_blueprint(bp_clientes, url_prefix='/clientes')
app.register_blueprint(bp_empleados, url_prefix='/empleados')
app.register_blueprint(bp_gastos, url_prefix='/gastos')
app.register_blueprint(bp_productos, url_prefix='/productos')
app.register_blueprint(bp_proveedores, url_prefix='/proveedores')
app.register_blueprint(bp_puestos, url_prefix='/puestos')
app.register_blueprint(bp_usuarios, url_prefix='/usuarios')
# NUEVO REGISTRO
app.register_blueprint(bp_facturacion) 

if __name__ == '__main__':
    app.run(debug=True)