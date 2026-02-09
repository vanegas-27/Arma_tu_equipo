# app/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.forms import PartidoForm, EditProfileForm
from app.models import Arquero, Partido
from app import db

routes = Blueprint("routes", __name__)

@routes.route("/")
def home():
    return render_template("home.html")

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
    # Llenar lista de arqueros
    form.id_arquero.choices = [(a.id, a.usuario.nombre) for a in Arquero.query.all()]

    if form.validate_on_submit():
        nuevo_partido = Partido(
            id_usuario=current_user.id,
            id_arquero=form.id_arquero.data,
            fecha=form.fecha.data,
            hora=form.hora.data,
            ubicacion=form.ubicacion.data,
            pago=form.pago.data,
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

    # Notificación simple
    for p in partidos:
        if p.estado == "confirmado":
            flash(f"Tu partido con {p.arquero.usuario.nombre} fue confirmado.", "success")
        elif p.estado == "cancelado":
            flash(f"Tu partido con {p.arquero.usuario.nombre} fue cancelado.", "danger")

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
    form = EditProfileForm(obj=current_user)  # precargar datos del usuario

    # Si es arquero, precargar también sus datos
    if current_user.rol == "arquero" and current_user.arquero:
        form.años_tapando.data = current_user.arquero.años_tapando
        form.precio_por_hora.data = current_user.arquero.precio_por_hora

    if form.validate_on_submit():
        # Actualizar datos básicos
        current_user.nombre = form.nombre.data
        current_user.apellido = form.apellido.data
        current_user.telefono = form.telefono.data
        current_user.direccion = form.direccion.data

        # Si es arquero, actualizar datos específicos
        if current_user.rol == "arquero" and current_user.arquero:
            current_user.arquero.años_tapando = form.años_tapando.data
            current_user.arquero.precio_por_hora = form.precio_por_hora.data

        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("routes.panel"))

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