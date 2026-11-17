from models import db
from datetime import datetime

class Empleado(db.Model):
    __tablename__ = 'Empleados'

    EmpleadoID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    PuestoID = db.Column(db.Integer, db.ForeignKey('Puestos.PuestoID'), nullable=True)
    SalarioBase = db.Column(db.Numeric(10, 2), nullable=True)
    FechaContratacion = db.Column(db.Date, nullable=True)
    Activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Empleado {self.Nombre}>"