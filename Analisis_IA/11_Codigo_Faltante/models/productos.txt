from models import db

class Producto(db.Model):
    __tablename__ = 'Productos'

    ProductoID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    PrecioUnitario = db.Column(db.Numeric(10, 2), nullable=False)
    ProveedorID = db.Column(db.Integer, db.ForeignKey('Proveedores.ProveedorID'), nullable=True)
    FechaCreacion = db.Column(db.DateTime, nullable=True)
    FechaModificacion = db.Column(db.DateTime, nullable=True)
    UnidadMedida = db.Column(db.String(20), nullable=True)
    SKU = db.Column(db.String(50), nullable=False)
    CodigoProveedor = db.Column(db.String(50), nullable=True)

    # RELACIÓN PARA PODER ACCEDER A p.proveedor.Nombre
    proveedor = db.relationship('Proveedor', backref='productos')

    def __repr__(self):
        return f"<Producto {self.Nombre}>"