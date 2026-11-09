from flask import Blueprint, render_template, request
from app.models.cadastro import Cadastro

login_bp = Blueprint ("login", __name__, url_prefix="/login")

@login_bp.route("/")
def renderizar_login():
    return render_template("login.html")

@login_bp.route("/logar", methods = ["POST"])
def Login():
    email = request.form["email"]
    senha = request.form["senha"]

    cadastro = Cadastro.Autenticar(
        email,
        senha
    )

    if cadastro:
        return render_template(
            "homepage.html",
            cadastro = cadastro
        )

    return "Usuário ou senha inválidos"