# app/models.py
from app import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    contraseña = db.Column(db.String(200), nullable=False)  # encriptada
    fecha_nacimiento = db.Column(db.Date)
    direccion = db.Column(db.String(200))
    rol = db.Column(db.String(20), nullable=False)  # "normal" o "arquero"

    # Relación con arquero (uno a uno)
    arquero = db.relationship("Arquero", back_populates="usuario", uselist=False)

    # Relación con partidos (si es usuario normal)
    partidos = db.relationship("Partido", back_populates="usuario")


class Arquero(db.Model):
    __tablename__ = "arqueros"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True)
    años_tapando = db.Column(db.Integer, nullable=False)
    precio_por_hora = db.Column(db.Float, nullable=False)
    calificacion = db.Column(db.Float, default=0.0)

    # Relación con usuario
    usuario = db.relationship("Usuario", back_populates="arquero")

    # Relación con partidos
    partidos = db.relationship("Partido", back_populates="arquero")


class Partido(db.Model):
    __tablename__ = "partidos"

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    id_arquero = db.Column(db.Integer, db.ForeignKey("arqueros.id"))
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)
    pago = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default="pendiente")  # pendiente, confirmado, cancelado

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="partidos")
    arquero = db.relationship("Arquero", back_populates="partidos")