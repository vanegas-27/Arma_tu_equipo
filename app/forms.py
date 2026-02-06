# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField, DateField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import Usuario


class LoginForm(FlaskForm):
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    contraseña = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar Sesión")


class RegisterForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=50)])
    apellido = StringField("Apellido", validators=[DataRequired(), Length(min=2, max=50)])
    correo = StringField("Correo", validators=[DataRequired(), Email()])
    telefono = StringField("Teléfono", validators=[Length(max=20)])
    contraseña = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    contraseña_confirmacion = PasswordField(
        "Confirmar Contraseña",
        validators=[DataRequired(), EqualTo("contraseña", message="Las contraseñas deben coincidir")]
    )
    fecha_nacimiento = DateField("Fecha de Nacimiento")
    direccion = StringField("Dirección", validators=[Length(max=200)])
    rol = SelectField("Rol", choices=[("normal", "Usuario Normal"), ("arquero", "Arquero")], default="normal")
    
    # Campos adicionales para arqueros
    años_tapando = IntegerField("Años de Experiencia", default=0)
    precio_por_hora = FloatField("Precio por Hora ($)", default=0.0)
    
    submit = SubmitField("Registrarse")

    def validate_correo(self, correo):
        usuario = Usuario.query.filter_by(correo=correo.data).first()
        if usuario:
            raise ValidationError("El correo ya está registrado")
