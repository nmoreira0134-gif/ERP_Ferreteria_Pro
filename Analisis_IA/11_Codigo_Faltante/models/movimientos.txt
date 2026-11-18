from models import db

class MovimientosInventario(db.Model):
    __tablename__ = 'MovimientosInventario'

    MovimientoID = db.Column(db.Integer, primary_key=True)
    ProductoID = db.Column(db.Integer, db.ForeignKey('Productos.ProductoID'), nullable=True)
    TipoMovimiento = db.Column(db.String(20), nullable=False)
    Cantidad = db.Column(db.Numeric(10, 2), nullable=True) # <-- Decimal para soportar fracciones
    Fecha = db.Column(db.DateTime, nullable=True)
    Referencia = db.Column(db.String(100), nullable=True)
    Usuario = db.Column(db.String(50), nullable=True)
    ProveedorID = db.Column(db.Integer, db.ForeignKey('Proveedores.ProveedorID'), nullable=True)
    CargaID = db.Column(db.Integer, db.ForeignKey('CargasInventario.CargaID'), nullable=True)

    # Relaciones para traer nombres
    producto = db.relationship('Producto')
    proveedor = db.relationship('Proveedor')