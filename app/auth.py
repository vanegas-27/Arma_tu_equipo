# app/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db, login_manager
from app.models import Usuario, Arquero
from app.forms import LoginForm, RegisterForm
import os

auth = Blueprint("auth", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# Ruta: Login
@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(correo=form.correo.data).first()
        if usuario and check_password_hash(usuario.contraseña, form.contraseña.data):
            login_user(usuario)
            flash("Has iniciado sesión correctamente", "success")
            return redirect(url_for("routes.panel"))
        else:
            flash("Correo o contraseña incorrectos", "danger")
    return render_template("login.html", form=form)


# Ruta: Registro
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Verificar si el correo ya existe
        usuario_existente = Usuario.query.filter_by(correo=form.correo.data).first()
        if usuario_existente:
            flash("El correo ya está registrado", "warning")
            return redirect(url_for("auth.register"))

        # Manejar la foto de perfil
        foto_filename = None
        if form.foto.data:
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            file = form.foto.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generar nombre único con timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                foto_filename = filename

        # Crear usuario
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            correo=form.correo.data,
            telefono=form.telefono.data,
            contraseña=generate_password_hash(form.contraseña.data),
            fecha_nacimiento=form.fecha_nacimiento.data,
            direccion=form.direccion.data,
            rol=form.rol.data,
            foto=foto_filename
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        # Si es arquero, crear registro en tabla Arqueros
        if form.rol.data == "arquero":
            nuevo_arquero = Arquero(
                id_usuario=nuevo_usuario.id,
                años_tapando=form.años_tapando.data,
                precio_por_hora=form.precio_por_hora.data
            )
            db.session.add(nuevo_arquero)
            db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


# Ruta: Logout
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente", "info")
    return redirect(url_for("routes.home"))