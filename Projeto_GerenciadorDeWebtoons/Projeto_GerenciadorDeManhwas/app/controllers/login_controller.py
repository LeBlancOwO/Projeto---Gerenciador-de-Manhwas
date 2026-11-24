from flask import Blueprint, render_template, request, session, redirect, flash, current_app
from app.models.usuario import Usuario

login_bp = Blueprint("login", __name__, url_prefix="/login")


@login_bp.route("/")
def renderizar_login():
    """Exibe a página de login."""
    return render_template("login.html")


@login_bp.route("/logar", methods=["POST"])
def Login():
    """Autentica o usuário, bloqueia contas suspensas e grava a sessão."""
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "")

    if not email or not senha:
        flash("Preencha o e-mail e a senha.", "error")
        return redirect("/login")

    usuario = Usuario.Autenticar(email, senha)

    if usuario:
        if usuario["suspenso"]:
            current_app.logger.warning("Tentativa de login em conta suspensa: %s", email)
            flash("Sua conta está suspensa pela administração.", "error")
            return redirect("/login")

        session.clear()
        session["user_id"] = usuario["id"]
        session["username"] = usuario["username"]
        session["tipo"] = usuario["tipo"]
        current_app.logger.info("Login realizado com sucesso: %s", usuario["username"])
        flash(f"Bem-vindo(a), {usuario['username']}!", "success")
        return redirect("/")

    current_app.logger.warning("Falha de autenticação para o e-mail: %s", email)
    flash("E-mail ou senha inválidos.", "error")
    return redirect("/login")


@login_bp.route("/redefinir-senha", methods=["GET", "POST"])
def redefinir_senha():
    """Permite redefinir a senha validando e-mail e username cadastrados."""
    if request.method == "GET":
        return render_template("redefinir_senha.html", email="", username="")

    email = request.form.get("email", "").strip()
    username = request.form.get("username", "").strip()
    nova_senha = request.form.get("nova_senha", "")
    confirmar_senha = request.form.get("confirmar_senha", "")

    if not email or not username or not nova_senha or not confirmar_senha:
        flash("Preencha todos os campos.", "error")
        return render_template("redefinir_senha.html", email=email, username=username)

    if len(nova_senha) < 6:
        flash("A nova senha deve ter pelo menos 6 caracteres.", "error")
        return render_template("redefinir_senha.html", email=email, username=username)

    if nova_senha != confirmar_senha:
        flash("As senhas não coincidem.", "error")
        return render_template("redefinir_senha.html", email=email, username=username)

    usuario = Usuario.BuscarPorEmailEUsername(email, username)
    if not usuario:
        flash("Não encontramos nenhuma conta com esse e-mail e username.", "error")
        return render_template("redefinir_senha.html", email=email, username=username)

    Usuario.AtualizarSenha(usuario["id"], nova_senha)
    current_app.logger.info("Senha redefinida para o usuário: %s", username)
    flash("Senha redefinida com sucesso! Faça login com a nova senha.", "success")
    return redirect("/login")