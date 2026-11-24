import os
import uuid
from flask import Blueprint, render_template, request, redirect, session, flash, current_app, g
from werkzeug.utils import secure_filename
from app.utils.auth_middleware import login_required
from app.models.usuario import Usuario
from app.models.obras import Obras

perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")


def _salvar_foto_perfil(arquivo):
    """Salva a foto de perfil enviada na pasta static/uploads/perfis e retorna o caminho relativo."""
    if not arquivo or not arquivo.filename:
        return None
    nome_seguro = secure_filename(arquivo.filename)
    nome_unico = f"{uuid.uuid4().hex[:8]}_{nome_seguro}"
    pasta = os.path.join(current_app.static_folder, "uploads", "perfis")
    os.makedirs(pasta, exist_ok=True)
    arquivo.save(os.path.join(pasta, nome_unico))
    return f"uploads/perfis/{nome_unico}"


@perfil_bp.route("/")
@login_required
def ver_perfil():
    """Exibe os dados cadastrados, foto e as obras do usuário autenticado."""
    obras = Obras.MinhasObras(session["user_id"])
    return render_template("perfil.html", usuario=g.usuario, obras=obras)


@perfil_bp.route("/<int:id_usuario>")
def ver_perfil_publico(id_usuario):
    """Exibe o perfil público de um autor ou leitor com suas obras aprovadas."""
    usuario = Usuario.Buscar_Id(id_usuario)
    if not usuario:
        flash("Usuário não encontrado.", "error")
        return redirect("/")

    todas_obras = Obras.MinhasObras(id_usuario)
    obras_aprovadas = [o for o in todas_obras if o["aprovada"] == 1]
    return render_template("perfil_publico.html", usuario=usuario, obras=obras_aprovadas)


@perfil_bp.route("/foto", methods=["POST"])
@login_required
def atualizar_foto():
    """Permite ao usuário logado adicionar ou trocar sua foto de perfil."""
    arquivo = request.files.get("foto")
    caminho_foto = _salvar_foto_perfil(arquivo)

    if not caminho_foto:
        flash("Selecione uma imagem válida para atualizar sua foto.", "error")
        return redirect("/perfil/")

    Usuario.AtualizarFoto(session["user_id"], caminho_foto)
    current_app.logger.info("Foto de perfil atualizada para usuário_id=%s", session["user_id"])
    flash("Foto de perfil atualizada com sucesso!", "success")
    return redirect("/perfil/")


@perfil_bp.route("/senha", methods=["POST"])
@login_required
def alterar_senha():
    """Permite ao usuário logado alterar a própria senha dentro do perfil."""
    senha_atual = request.form.get("senha_atual", "")
    nova_senha = request.form.get("nova_senha", "")
    confirmar_senha = request.form.get("confirmar_senha", "")

    if not senha_atual or not nova_senha or not confirmar_senha:
        flash("Preencha todos os campos de senha.", "error")
        return redirect("/perfil/")

    if len(nova_senha) < 6:
        flash("A nova senha deve ter pelo menos 6 caracteres.", "error")
        return redirect("/perfil/")

    if nova_senha != confirmar_senha:
        flash("A confirmação da nova senha não confere.", "error")
        return redirect("/perfil/")

    if not Usuario.Autenticar(g.usuario["email"], senha_atual):
        flash("Senha atual incorreta.", "error")
        return redirect("/perfil/")

    Usuario.AtualizarSenha(session["user_id"], nova_senha)
    current_app.logger.info("Senha alterada pelo perfil para usuário_id=%s", session["user_id"])
    flash("Senha alterada com sucesso!", "success")
    return redirect("/perfil/")


@perfil_bp.route("/excluir", methods=["POST"])
@login_required
def deletar_perfil():
    """Exclui permanentemente a conta do usuário logado e encerra sua sessão."""
    user_id = session["user_id"]
    username = session.get("username")
    Usuario.Excluir(user_id)
    session.clear()
    current_app.logger.info("Conta excluída pelo próprio usuário: %s (id=%s)", username, user_id)
    flash("Seu perfil e sua conta foram excluídos permanentemente.", "info")
    return redirect("/")
