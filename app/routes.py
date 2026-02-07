# app/routes.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.forms import PartidoForm
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

    partidos = current_user.partidos  # gracias a la relación en models.py
    return render_template("mis_partidos.html", partidos=partidos)