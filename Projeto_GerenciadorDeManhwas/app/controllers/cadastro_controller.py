from flask import Blueprint, render_template

cadastro_bp = Blueprint ("cadastro", __name__, url_prefix="/cadastro")

@cadastro_bp.route("/")
def renderizar_cadastro():
    return render_template("cadastro.html")