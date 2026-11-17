from flask_sqlalchemy import SQLAlchemy

# 1. Inicializamos la base de datos
db = SQLAlchemy()

# 2. Importamos TODOS los modelos aquí
# (Asegúrate de que estos archivos existan en tu carpeta models)
from .productos import Producto
from .proveedores import Proveedor
from .clientes import Cliente
from .puestos import Puesto      # <--- Este es el que faltaba
from .empleados import Empleado
from .gastos import Gasto
from .cargas import CargasInventario
from .movimientos import MovimientosInventario
# from .correlativo import Correlativo # Descomenta si lo tienes