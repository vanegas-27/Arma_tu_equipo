# app/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.forms import PartidoForm, EditProfileForm
from app.models import Arquero, Partido
from app import db
from collections import Counter
import calendar
import os

routes = Blueprint("routes", __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@routes.route("/")
def home():
    arqueros = Arquero.query.limit(6).all()
    return render_template("home.html", arqueros=arqueros)

@routes.route("/arquero/<int:arquero_id>")
def arquero_detail(arquero_id):
    arquero = Arquero.query.get_or_404(arquero_id)
    return render_template("arquero_detail.html", arquero=arquero)

@routes.route("/arqueros")
def arqueros():
    arqueros = Arquero.query.all()
    return render_template("arqueros.html", arqueros=arqueros)

@routes.route("/panel")
@login_required
def panel():
    if current_user.rol == "arquero":
        return render_template("panel_arquero.html", usuario=current_user)
    else:
        return render_template("panel_usuario.html", usuario=current_user)
    

@routes.route("/agendar", methods=["GET", "POST"])
@login_required
def agendar():
    if current_user.rol != "normal":
        flash("Solo los usuarios normales pueden agendar partidos.", "danger")
        return redirect(url_for("routes.panel"))

    form = PartidoForm()
    choices = []
    for a in Arquero.query.all():
        nombre = a.usuario.nombre
        if a.calificacion > 0:
            nombre += f" (★ {a.calificacion:.1f})"
        else:
            nombre += " (Sin Calificacion)"
        choices.append((a.id, nombre))
    form.id_arquero.choices = choices

    if form.validate_on_submit():
        arquero = Arquero.query.get(form.id_arquero.data)

        nuevo_partido = Partido(
            id_usuario=current_user.id,
            id_arquero=arquero.id,
            fecha=form.fecha.data,
            hora=form.hora.data,
            ubicacion=form.ubicacion.data,
            pago=arquero.precio_por_hora,   # se asigna automáticamente
            estado="pendiente"
        )
        db.session.add(nuevo_partido)
        db.session.commit()
        flash("Partido agendado correctamente.", "success")
        return redirect(url_for("routes.panel"))

    return render_template("agendar.html", form=form)


@routes.route("/mis_partidos")
@login_required
def mis_partidos():
    if current_user.rol != "normal":
        flash("Solo los usuarios normales pueden ver sus partidos agendados.", "danger")
        return redirect(url_for("routes.panel"))

    partidos = current_user.partidos

    return render_template("mis_partidos.html", partidos=partidos)

@routes.route("/partidos_asignados")
@login_required
def partidos_asignados():
    if current_user.rol != "arquero":
        flash("Solo los arqueros pueden ver sus partidos asignados.", "danger")
        return redirect(url_for("routes.panel"))

    partidos = current_user.arquero.partidos  # relación en models.py
    return render_template("partidos_asignados.html", partidos=partidos)

@routes.route("/editar_perfil", methods=["GET", "POST"])
@login_required
def editar_perfil():
    form = EditProfileForm()

    # Si es arquero, precargar también sus datos
    if current_user.rol == "arquero" and current_user.arquero:
        if request.method == "GET":
            form.años_tapando.data = current_user.arquero.años_tapando
            form.precio_por_hora.data = current_user.arquero.precio_por_hora

    if form.validate_on_submit():
        # Actualizar datos básicos
        current_user.nombre = form.nombre.data
        current_user.apellido = form.apellido.data
        current_user.telefono = form.telefono.data
        current_user.direccion = form.direccion.data

        # Manejar la foto de perfil
        if form.foto.data:
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            file = form.foto.data
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                current_user.foto = filename

        # Si es arquero, actualizar datos específicos
        if current_user.rol == "arquero" and current_user.arquero:
            if form.años_tapando.data is not None:
                current_user.arquero.años_tapando = form.años_tapando.data
            if form.precio_por_hora.data is not None:
                current_user.arquero.precio_por_hora = form.precio_por_hora.data

        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("routes.panel"))

    # Precargar datos para GET
    if request.method == "GET":
        form.nombre.data = current_user.nombre
        form.apellido.data = current_user.apellido
        form.telefono.data = current_user.telefono
        form.direccion.data = current_user.direccion

    return render_template("editar_perfil.html", form=form)


@routes.route("/actualizar_estado/<int:partido_id>/<string:nuevo_estado>", methods=["POST"])
@login_required
def actualizar_estado(partido_id, nuevo_estado):
    if current_user.rol != "arquero":
        flash("Solo los arqueros pueden actualizar estados de partidos.", "danger")
        return redirect(url_for("routes.panel"))

    partido = Partido.query.get_or_404(partido_id)

    # Verificar que el partido pertenece al arquero actual
    if partido.id_arquero != current_user.arquero.id:
        flash("No tienes permiso para modificar este partido.", "danger")
        return redirect(url_for("routes.partidos_asignados"))

    # Actualizar estado
    if nuevo_estado in ["pendiente", "confirmado", "cancelado"]:
        partido.estado = nuevo_estado
        db.session.commit()
        flash(f"Estado del partido actualizado a {nuevo_estado}.", "success")
    else:
        flash("Estado inválido.", "danger")

    return redirect(url_for("routes.partidos_asignados"))

@routes.route("/historial_usuario")
@login_required
def historial_usuario():
    if current_user.rol != "normal":
        flash("Solo los usuarios normales pueden ver su historial.", "danger")
        return redirect(url_for("routes.panel"))

    partidos = [p for p in current_user.partidos if p.estado == "confirmado"]
    total_gastado = sum(p.pago for p in partidos)

    return render_template("historial_usuario.html", partidos=partidos, total=total_gastado)

@routes.route("/historial_arquero")
@login_required
def historial_arquero():
    if current_user.rol != "arquero":
        flash("Solo los arqueros pueden ver su historial.", "danger")
        return redirect(url_for("routes.panel"))

    partidos = [p for p in current_user.arquero.partidos if p.estado == "confirmado"]
    total_ganado = sum(p.pago for p in partidos)

    return render_template("historial_arquero.html", partidos=partidos, total=total_ganado)


@routes.route("/estadisticas_arquero")
@login_required
def estadisticas_arquero():
    if current_user.rol != "arquero":
        flash("Solo los arqueros pueden ver estadísticas.", "danger")
        return redirect(url_for("routes.panel"))

    arquero = current_user.arquero
    partidos = arquero.partidos

    # Total partidos jugados (confirmados)
    partidos_jugados = [p for p in partidos if p.estado == "confirmado"]
    total_jugados = len(partidos_jugados)
    
    # Total partidos cancelados
    total_cancelados = len([p for p in partidos if p.estado == "cancelado"])
    
    # Total partidos pendientes
    total_pendientes = len([p for p in partidos if p.estado == "pendiente"])
    
    # Ingresos por mes (solo confirmados)
    ingresos_por_mes = {}
    for p in partidos_jugados:
        mes = f"{p.fecha.year}-{p.fecha.month:02d}"
        ingresos_por_mes[mes] = ingresos_por_mes.get(mes, 0) + p.pago

    # Ordenar por mes
    meses_ordenados = sorted(ingresos_por_mes.keys())
    labels = [m.split('-')[1] + '/' + m.split('-')[0][2:] for m in meses_ordenados]
    data = [ingresos_por_mes[m] for m in meses_ordenados]

    total_ingresos = sum(p.pago for p in partidos_jugados)

    return render_template(
        "estadisticas_arquero.html", 
        labels=labels, 
        data=data, 
        total_jugados=total_jugados,
        total_cancelados=total_cancelados,
        total_pendientes=total_pendientes,
        total_ingresos=total_ingresos
    )

@routes.route("/calificar/<int:partido_id>", methods=["POST"])
@login_required
def calificar_arquero(partido_id):
    if current_user.rol != "normal":
        flash("Solo los usuarios pueden calificar arqueros.", "danger")
        return redirect(url_for("routes.mis_partidos"))

    partido = Partido.query.get_or_404(partido_id)

    if partido.id_usuario != current_user.id:
        flash("No tienes permiso para calificar este partido.", "danger")
        return redirect(url_for("routes.mis_partidos"))

    if partido.calificado:
        flash("Ya has calificado este partido.", "warning")
        return redirect(url_for("routes.mis_partidos"))

    calificacion = request.form.get("calificacion")
    if not calificacion or not calificacion.isdigit():
        flash("Por favor selecciona una calificacion.", "danger")
        return redirect(url_for("routes.mis_partidos"))

    calificacion = int(calificacion)
    if calificacion < 1 or calificacion > 5:
        flash("La calificacion debe estar entre 1 y 5.", "danger")
        return redirect(url_for("routes.mis_partidos"))

    arquero = partido.arquero

    if arquero.calificacion == 0:
        arquero.calificacion = float(calificacion)
    else:
        num_partidos = Partido.query.filter_by(id_arquero=arquero.id, estado="confirmado").count()
        if num_partidos > 0:
            nueva_calif = ((arquero.calificacion * num_partidos) + calificacion) / (num_partidos + 1)
            arquero.calificacion = round(nueva_calif, 1)

    partido.calificado = True
    db.session.commit()

    flash("Gracias por calificar al arquero!", "success")
    return redirect(url_for("routes.mis_partidos"))