from . import db
from datetime import datetime

class Gasto(db.Model):
    __tablename__ = 'Gastos'
    
    GastoID = db.Column(db.Integer, primary_key=True)
    Fecha = db.Column(db.DateTime, default=datetime.now)
    Categoria = db.Column(db.String(50), nullable=False)
    Descripcion = db.Column(db.String(255))
    Monto = db.Column(db.Numeric(10, 2), nullable=False)
    MetodoPago = db.Column(db.String(20))
    Proveedor = db.Column(db.String(100))
    Referencia = db.Column(db.String(100))
    UsuarioRegistro = db.Column(db.String(50))
    FechaCreacion = db.Column(db.DateTime, default=datetime.now)
    FechaModificacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)