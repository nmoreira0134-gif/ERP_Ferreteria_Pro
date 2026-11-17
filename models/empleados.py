from . import db
from datetime import datetime

class Empleado(db.Model):
    __tablename__ = 'Empleados'
    
    EmpleadoID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    PuestoID = db.Column(db.Integer, db.ForeignKey('Puestos.PuestoID'))
    SalarioBase = db.Column(db.Numeric(10, 2))
    FechaContratacion = db.Column(db.Date)
    Activo = db.Column(db.Boolean, default=True)

    # Esto nos permite acceder al nombre del puesto fácilmente en el HTML
    puesto = db.relationship('Puesto', backref='empleados')