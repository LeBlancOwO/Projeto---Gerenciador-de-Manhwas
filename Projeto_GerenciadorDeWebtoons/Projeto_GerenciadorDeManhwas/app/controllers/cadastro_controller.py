import os
import uuid
from flask import Blueprint, render_template, request, redirect, flash, current_app
from werkzeug.utils import secure_filename
from app.models.usuario import Usuario

cadastro_bp = Blueprint("cadastro", __name__, url_prefix="/cadastro")


def _salvar_foto_cadastro(arquivo):
    """Salva a foto opcional enviada no cadastro dentro de static/uploads/perfis."""
    if not arquivo or not arquivo.filename:
        return None
    nome_seguro = secure_filename(arquivo.filename)
    nome_unico = f"{uuid.uuid4().hex[:8]}_{nome_seguro}"
    pasta = os.path.join(current_app.static_folder, "uploads", "perfis")
    os.makedirs(pasta, exist_ok=True)
    arquivo.save(os.path.join(pasta, nome_unico))
    return f"uploads/perfis/{nome_unico}"


@cadastro_bp.route("/")
def renderizar_cadastro():
    """Exibe o formulário de cadastro de novo usuário."""
    return render_template("cadastro.html")


@cadastro_bp.route("/cadastrar", methods=["POST"])
def Cadastrar():
    """Valida os dados, salva a foto opcional e cria um novo usuário."""
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    username = request.form.get("username", "").strip()
    senha = request.form.get("senha", "")
    arquivo_foto = request.files.get("foto")

    if not nome or not email or not username or not senha:
        flash("Todos os campos obrigatórios devem ser preenchidos.", "error")
        return redirect("/cadastro")

    if len(nome) < 3 or len(nome) > 100:
        flash("O nome deve ter entre 3 e 100 caracteres.", "error")
        return redirect("/cadastro")

    if len(username) < 3 or len(username) > 100:
        flash("O username deve ter entre 3 e 100 caracteres.", "error")
        return redirect("/cadastro")

    if len(senha) < 6:
        flash("A senha deve ter pelo menos 6 caracteres.", "error")
        return redirect("/cadastro")

    if Usuario.Buscar_Por_Email_Ou_Username(email, username):
        flash("Já existe um usuário com esse e-mail ou username.", "error")
        return redirect("/cadastro")

    foto = _salvar_foto_cadastro(arquivo_foto)
    usuario = Usuario(nome, email, username, senha, foto=foto)
    usuario.Salvar()
    current_app.logger.info("Novo usuário cadastrado: %s", username)
    flash("Cadastro realizado com sucesso! Faça seu login.", "success")
    return redirect("/login")