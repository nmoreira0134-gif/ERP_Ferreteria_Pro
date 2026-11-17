from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .productos import Producto
from .proveedores import Proveedor
from .cargas import CargasInventario
from .movimientos import MovimientosInventario
from .clientes import Cliente
from .empleados import Empleado