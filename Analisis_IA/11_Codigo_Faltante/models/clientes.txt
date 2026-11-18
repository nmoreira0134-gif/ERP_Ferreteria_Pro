from models import db

class Cliente(db.Model):
    __tablename__ = 'Clientes'

    ClienteID = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Telefono = db.Column(db.String(20), nullable=True)
    Email = db.Column(db.String(100), nullable=True)
    Genero = db.Column(db.String(1), nullable=True)

    def __repr__(self):
        return f"<Cliente {self.Nombre}>"