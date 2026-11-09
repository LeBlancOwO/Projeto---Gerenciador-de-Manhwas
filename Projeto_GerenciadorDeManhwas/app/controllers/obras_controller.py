from flask import Blueprint, render_template, request, redirect
from app.models.obras import Obras

obras_bp = Blueprint ("obras", __name__, url_prefix="/obras")

@obras_bp.route("/")
def renderizar_obras():
    return render_template("adicionar_obras.html")

@obras_bp.route("/adicionar", methods = ["POST"])
def Adicionar_obra():
    titulo = request.form["titulo"]
    autor = request.form["autor"]
    status = request.form["status"]

    obras = Obras(
        titulo,
        autor,
        status
    )

    obras.Salvar()

    return redirect ("/obras/listar")

@obras_bp.route("/listar")
def Listar_obra():
    obras = Obras.Listar()

    return render_template("listar_obras.html", obras = obras)