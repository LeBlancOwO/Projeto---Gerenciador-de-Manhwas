from flask import Blueprint, render_template, request, redirect
from app.models.cadastro import Cadastro

cadastro_bp = Blueprint ("cadastro", __name__, url_prefix="/cadastro")

@cadastro_bp.route("/")
def renderizar_cadastro():
    return render_template("cadastro.html")

@cadastro_bp.route("/cadastrar", methods = ["POST"])
def Cadastrar():
    nome = request.form["nome"]
    email = request.form["email"]
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    cadastro = Cadastro(
        nome,
        email,
        usuario,
        senha
    )

    cadastro.Salvar()

    return redirect("/")