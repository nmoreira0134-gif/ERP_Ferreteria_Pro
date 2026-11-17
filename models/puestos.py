from . import db

class Puesto(db.Model):
    __tablename__ = 'Puestos'
    
    PuestoID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    SalarioBase = db.Column(db.Numeric(10, 2))
    Descripcion = db.Column(db.String(255))