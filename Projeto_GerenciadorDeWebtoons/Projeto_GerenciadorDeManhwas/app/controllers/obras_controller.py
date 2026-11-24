import os
import uuid
from flask import Blueprint, render_template, request, redirect, session, flash, current_app
from werkzeug.utils import secure_filename
from app.utils.auth_middleware import login_required
from app.models.obras import Obras, TAGS_PADRAO, STATUS_VALIDOS
from app.models.acompanhamento import Acompanhamento
from app.models.mensagem import Mensagem

obras_bp = Blueprint("obras", __name__, url_prefix="/obras")


def _salvar_capa(arquivo):
    """Salva a imagem de capa enviada em static/uploads e retorna o caminho relativo."""
    if not arquivo or not arquivo.filename:
        return None
    nome_seguro = secure_filename(arquivo.filename)
    nome_unico = f"{uuid.uuid4().hex[:8]}_{nome_seguro}"
    pasta_uploads = os.path.join(current_app.static_folder, "uploads")
    os.makedirs(pasta_uploads, exist_ok=True)
    arquivo.save(os.path.join(pasta_uploads, nome_unico))
    return f"uploads/{nome_unico}"


@obras_bp.route("/")
@login_required
def renderizar_obras():
    """Exibe o formulário para cadastrar uma nova obra."""
    return render_template(
        "adicionar_obras.html",
        tags_padrao=TAGS_PADRAO,
        titulo="",
        sinopse="",
        tags_selecionadas=[],
    )


@obras_bp.route("/adicionar", methods=["POST"])
@login_required
def Adicionar_obra():
    """Valida e salva uma nova obra preservando os campos preenchidos em caso de erro."""
    titulo = request.form.get("titulo", "").strip()
    sinopse = request.form.get("sinopse", "").strip()
    tags_selecionadas = [t for t in request.form.getlist("tags") if t in TAGS_PADRAO]
    usuario_id = session["user_id"]
    arquivo = request.files.get("capa")

    erro = None
    if not titulo or not sinopse:
        erro = "Preencha o título e a sinopse."
    elif len(titulo) < 2 or len(titulo) > 150:
        erro = "O título deve ter entre 2 e 150 caracteres."
    elif len(sinopse) < 10:
        erro = "A sinopse deve ter pelo menos 10 caracteres."
    elif not tags_selecionadas:
        erro = "Selecione pelo menos uma tag para a obra."
    elif Obras.BuscarPorTitulo(titulo):
        erro = "Já existe uma obra cadastrada com esse título."

    if erro:
        flash(erro, "error")
        return render_template(
            "adicionar_obras.html",
            tags_padrao=TAGS_PADRAO,
            titulo=titulo,
            sinopse=sinopse,
            tags_selecionadas=tags_selecionadas,
        )

    capa = _salvar_capa(arquivo)
    if not capa:
        flash("Envie uma imagem de capa válida.", "error")
        return render_template(
            "adicionar_obras.html",
            tags_padrao=TAGS_PADRAO,
            titulo=titulo,
            sinopse=sinopse,
            tags_selecionadas=tags_selecionadas,
        )

    tags_texto = ", ".join(tags_selecionadas)
    obra = Obras(titulo, sinopse, capa, "Em andamento", usuario_id, tags=tags_texto)
    obra.Salvar()
    current_app.logger.info("Obra criada '%s' pelo usuário_id=%s", titulo, usuario_id)
    flash("Obra enviada para análise com sucesso!", "success")
    return redirect("/obras/minhas")


@obras_bp.route("/biblioteca")
@login_required
def Biblioteca():
    """Lista apenas as obras lidas pelo usuário logado com filtros de tags incluídas e excluídas."""
    busca = request.args.get("busca", "").strip()
    status = request.args.get("status", "").strip()
    tags_incluir = [t for t in request.args.getlist("tags_incluir") if t in TAGS_PADRAO]
    tags_excluir = [t for t in request.args.getlist("tags_excluir") if t in TAGS_PADRAO]

    obras = Obras.ListarLidasPorUsuario(
        session["user_id"],
        busca=busca or None,
        status=status or None,
        tags_incluir=tags_incluir,
        tags_excluir=tags_excluir,
    )
    return render_template(
        "biblioteca.html",
        obras=obras,
        busca=busca,
        status_filtro=status,
        tags_incluir=tags_incluir,
        tags_excluir=tags_excluir,
        tags_padrao=TAGS_PADRAO,
    )


@obras_bp.route("/minhas")
@login_required
def Minhas_obras():
    """Lista todas as obras criadas pelo usuário logado e seus status de moderação."""
    obras = Obras.MinhasObras(session["user_id"])
    return render_template("minhas_obras.html", obras=obras)


@obras_bp.route("/<int:obra_id>/acompanhar", methods=["POST"])
@login_required
def Acompanhar_obra(obra_id):
    """Ativa ou desativa o acompanhamento de uma obra para receber avisos de novos capítulos."""
    obra = Obras.BuscarPorId(obra_id)
    if not obra:
        flash("Obra não encontrada.", "error")
        return redirect("/")

    seguindo = Acompanhamento.Alternar(session["user_id"], obra_id)
    if seguindo:
        flash(f"Você agora está acompanhando '{obra['titulo']}'.", "success")
    else:
        flash(f"Você deixou de acompanhar '{obra['titulo']}'.", "info")

    return redirect(f"/capitulos/obra/{obra_id}")


@obras_bp.route("/<int:id_obra>/editar", methods=["GET", "POST"])
@login_required
def Editar_obra(id_obra):
    """Permite ao dono editar a obra e registra a atualização no canal de Mensagens do autor."""
    obra = Obras.BuscarPorIdEUsuario(id_obra, session["user_id"])
    if not obra:
        flash("Obra não encontrada ou sem permissão para editar.", "error")
        return redirect("/obras/minhas")

    if request.method == "GET":
        tags_atuais = [t.strip() for t in (obra["tags"] or "").split(",") if t.strip()]
        return render_template(
            "editar_obra.html",
            obra=obra,
            tags_padrao=TAGS_PADRAO,
            titulo=obra["titulo"],
            sinopse=obra["sinopse"],
            status_atual=obra["status"],
            tags_selecionadas=tags_atuais,
        )

    titulo = request.form.get("titulo", "").strip()
    sinopse = request.form.get("sinopse", "").strip()
    status = request.form.get("status", "").strip()
    tags_selecionadas = [t for t in request.form.getlist("tags") if t in TAGS_PADRAO]
    arquivo = request.files.get("capa")

    erro = None
    if not titulo or not sinopse or status not in STATUS_VALIDOS:
        erro = "Preencha todos os campos corretamente."
    elif len(titulo) < 2 or len(titulo) > 150 or len(sinopse) < 10:
        erro = "Verifique o tamanho do título (2-150) e da sinopse (mín. 10)."
    elif not tags_selecionadas:
        erro = "Selecione pelo menos uma tag."
    elif Obras.BuscarPorTitulo(titulo, excluir_id=id_obra):
        erro = "Já existe outra obra com esse título."

    if erro:
        flash(erro, "error")
        return render_template(
            "editar_obra.html",
            obra=obra,
            tags_padrao=TAGS_PADRAO,
            titulo=titulo,
            sinopse=sinopse,
            status_atual=status,
            tags_selecionadas=tags_selecionadas,
        )

    nova_capa = _salvar_capa(arquivo)
    tags_texto = ", ".join(tags_selecionadas)
    Obras.Atualizar(id_obra, session["user_id"], titulo, sinopse, status, tags_texto, capa=nova_capa)

    msg = Mensagem(
        usuario_id=session["user_id"],
        categoria="atualizacoes",
        titulo=f"Obra atualizada: '{titulo}'",
        conteudo=f"Você atualizou os dados da sua obra '{titulo}' (Status atual: {status}).",
    )
    msg.Salvar()

    current_app.logger.info("Obra id=%s atualizada pelo usuário_id=%s", id_obra, session["user_id"])
    flash("Obra atualizada e reenviada para análise!", "success")
    return redirect("/obras/minhas")


@obras_bp.route("/<int:id_obra>/excluir", methods=["POST"])
@login_required
def Excluir_obra(id_obra):
    """Exclui uma obra validando o dono e registra a exclusão no canal de Mensagens do autor."""
    obra = Obras.BuscarPorIdEUsuario(id_obra, session["user_id"])
    if not obra:
        current_app.logger.warning("Tentativa de exclusão não autorizada da obra id=%s por usuário_id=%s", id_obra, session["user_id"])
        flash("Não foi possível excluir esta obra.", "error")
        return redirect("/obras/minhas")

    removidas = Obras.Excluir(id_obra, session["user_id"])

    if removidas:
        msg = Mensagem(
            usuario_id=session["user_id"],
            categoria="atualizacoes",
            titulo=f"Obra excluída: '{obra['titulo']}'",
            conteudo=f"Você excluiu a obra '{obra['titulo']}' da plataforma.",
        )
        msg.Salvar()

        current_app.logger.info("Obra id=%s excluída pelo usuário_id=%s", id_obra, session["user_id"])
        flash("Obra excluída com sucesso.", "success")
    else:
        flash("Não foi possível excluir esta obra.", "error")

    return redirect("/obras/minhas")