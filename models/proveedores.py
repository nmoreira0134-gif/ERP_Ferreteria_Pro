from models import db

class Proveedor(db.Model):
    __tablename__ = 'Proveedores'

    ProveedorID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Contacto = db.Column(db.String(100), nullable=True)
    Telefono = db.Column(db.String(20), nullable=True)
    Email = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Proveedor {self.Nombre}>"