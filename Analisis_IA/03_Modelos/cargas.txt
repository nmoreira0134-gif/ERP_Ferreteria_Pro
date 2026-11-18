from models import db
from datetime import datetime

class CargasInventario(db.Model):
    __tablename__ = 'CargasInventario'

    CargaID = db.Column(db.Integer, primary_key=True)
    Fecha = db.Column(db.DateTime, default=datetime.now)
    ProveedorID = db.Column(db.Integer, db.ForeignKey('Proveedores.ProveedorID'))
    Usuario = db.Column(db.String(50))
    Referencia = db.Column(db.String(100))