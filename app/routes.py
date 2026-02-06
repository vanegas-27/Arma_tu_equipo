# app/routes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user

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