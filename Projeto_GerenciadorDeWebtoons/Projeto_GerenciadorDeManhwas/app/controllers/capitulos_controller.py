from flask import Blueprint, render_template, request, redirect, session, flash, current_app
from app.utils.auth_middleware import login_required
from app.models.obras import Obras, STATUS_VALIDOS
from app.models.capitulo import Capitulo
from app.models.leitura import Leitura
from app.models.comentario import Comentario
from app.models.mensagem import Mensagem
from app.models.acompanhamento import Acompanhamento

capitulos_bp = Blueprint("capitulos", __name__, url_prefix="/capitulos")


@capitulos_bp.route("/obra/<int:obra_id>")
def listar_capitulos(obra_id):
    """Rota pública: exibe sinopse, capítulos, botão de acompanhar e comentários gerais da obra."""
    obra = Obras.BuscarPorId(obra_id)
    if not obra:
        flash("Obra não encontrada.", "error")
        return redirect("/")

    user_id = session.get("user_id")
    eh_dono = user_id is not None and obra["usuario_id"] == user_id
    if obra["aprovada"] != 1 and not eh_dono and session.get("tipo") != "admin":
        flash("Esta obra ainda não está disponível para leitura.", "warning")
        return redirect("/")

    capitulos = Capitulo.ListarPorObra(obra_id)
    lidos_ids = Leitura.ListarCapitulosLidosPorUsuarioEObra(user_id, obra_id) if user_id else set()
    comentarios_obra = Comentario.ListarPorObra(obra_id)
    acompanhando = Acompanhamento.EstaAcompanhando(user_id, obra_id) if user_id else False

    return render_template(
        "capitulos.html",
        obra=obra,
        capitulos=capitulos,
        eh_dono=eh_dono,
        lidos_ids=lidos_ids,
        comentarios_obra=comentarios_obra,
        acompanhando=acompanhando,
    )


@capitulos_bp.route("/obra/<int:obra_id>/comentar", methods=["POST"])
@login_required
def comentar_obra(obra_id):
    """Registra um comentário geral na obra e notifica o autor no canal de mensagens."""
    obra = Obras.BuscarPorId(obra_id)
    if not obra:
        flash("Obra não encontrada.", "error")
        return redirect("/")

    texto = request.form.get("texto", "").strip()
    if len(texto) < 2:
        flash("Escreva um comentário com pelo menos 2 caracteres.", "error")
        return redirect(f"/capitulos/obra/{obra_id}")

    comentario = Comentario(texto, session["user_id"], obra_id=obra_id)
    comentario.Salvar()

    msg = Mensagem(
        usuario_id=obra["usuario_id"],
        categoria="atualizacoes",
        titulo=f"Novo comentário na sua obra '{obra['titulo']}'",
        conteudo=f"{session['username']} comentou na obra: \"{texto[:120]}\"",
    )
    msg.Salvar()

    current_app.logger.info("Comentário na obra id=%s pelo usuário_id=%s", obra_id, session["user_id"])
    flash("Comentário publicado na obra!", "success")
    return redirect(f"/capitulos/obra/{obra_id}")


@capitulos_bp.route("/<int:id_capitulo>/ler")
def ler_capitulo(id_capitulo):
    """Rota pública: exibe o conteúdo do capítulo, registra leitura (se logado) e carrega comentários."""
    capitulo = Capitulo.BuscarPorId(id_capitulo)
    if not capitulo:
        flash("Capítulo não encontrado.", "error")
        return redirect("/")

    obra = Obras.BuscarPorId(capitulo["obra_id"])
    if not obra:
        flash("Obra não encontrada.", "error")
        return redirect("/")

    user_id = session.get("user_id")
    eh_dono = user_id is not None and obra["usuario_id"] == user_id
    if obra["aprovada"] != 1 and not eh_dono and session.get("tipo") != "admin":
        flash("Esta obra ainda não está disponível para leitura.", "warning")
        return redirect("/")

    if user_id:
        Leitura.Registrar(user_id, id_capitulo)
        current_app.logger.info("Capítulo id=%s lido pelo usuário_id=%s", id_capitulo, user_id)

    todos_capitulos = Capitulo.ListarPorObra(obra["id"])
    anterior_id = None
    proximo_id = None
    for idx, cap in enumerate(todos_capitulos):
        if cap["id"] == id_capitulo:
            if idx > 0:
                anterior_id = todos_capitulos[idx - 1]["id"]
            if idx + 1 < len(todos_capitulos):
                proximo_id = todos_capitulos[idx + 1]["id"]
            break

    comentarios = Comentario.ListarPorCapitulo(id_capitulo)
    return render_template(
        "ler_capitulo.html",
        obra=obra,
        capitulo=capitulo,
        anterior_id=anterior_id,
        proximo_id=proximo_id,
        comentarios=comentarios,
    )


@capitulos_bp.route("/<int:id_capitulo>/comentar", methods=["POST"])
@login_required
def comentar_capitulo(id_capitulo):
    """Registra um comentário no capítulo e notifica o autor da obra no canal de mensagens."""
    capitulo = Capitulo.BuscarPorId(id_capitulo)
    if not capitulo:
        flash("Capítulo não encontrado.", "error")
        return redirect("/")

    obra = Obras.BuscarPorId(capitulo["obra_id"])
    texto = request.form.get("texto", "").strip()
    if len(texto) < 2:
        flash("Escreva um comentário com pelo menos 2 caracteres.", "error")
        return redirect(f"/capitulos/{id_capitulo}/ler")

    comentario = Comentario(texto, session["user_id"], capitulo_id=id_capitulo, obra_id=capitulo["obra_id"])
    comentario.Salvar()

    if obra:
        msg = Mensagem(
            usuario_id=obra["usuario_id"],
            categoria="atualizacoes",
            titulo=f"Comentário em '{capitulo['titulo']}' de '{obra['titulo']}'",
            conteudo=f"{session['username']} comentou: \"{texto[:120]}\"",
        )
        msg.Salvar()

    current_app.logger.info("Comentário adicionado no capítulo id=%s pelo usuário_id=%s", id_capitulo, session["user_id"])
    flash("Comentário publicado!", "success")
    return redirect(f"/capitulos/{id_capitulo}/ler")


@capitulos_bp.route("/comentario/<int:id_comentario>/excluir", methods=["POST"])
@login_required
def excluir_comentario(id_comentario):
    """Exclui um comentário validando se pertence ao usuário autenticado."""
    id_capitulo = request.form.get("capitulo_id")
    obra_id = request.form.get("obra_id")
    removidos = Comentario.Excluir(id_comentario, session["user_id"])
    if removidos:
        current_app.logger.info("Comentário id=%s excluído pelo usuário_id=%s", id_comentario, session["user_id"])
        flash("Comentário excluído.", "success")
    else:
        flash("Não foi possível excluir este comentário.", "error")

    if id_capitulo:
        return redirect(f"/capitulos/{id_capitulo}/ler")
    if obra_id:
        return redirect(f"/capitulos/obra/{obra_id}")
    return redirect("/")


@capitulos_bp.route("/obra/<int:obra_id>/adicionar", methods=["GET", "POST"])
@login_required
def adicionar_capitulo(obra_id):
    """Exibe a página dedicada (acessada via Minhas Obras) e salva um novo capítulo sem exigir número manual."""
    obra = Obras.BuscarPorIdEUsuario(obra_id, session["user_id"])
    if not obra:
        flash("Você não tem permissão para adicionar capítulos nesta obra.", "error")
        return redirect("/obras/minhas")

    if request.method == "GET":
        return render_template(
            "adicionar_capitulo.html",
            obra=obra,
            status_validos=STATUS_VALIDOS,
            titulo="",
            conteudo="",
            status_selecionado=obra["status"],
        )

    titulo = request.form.get("titulo", "").strip()
    conteudo = request.form.get("conteudo", "").strip()
    novo_status = request.form.get("status", "").strip()

    if not titulo or len(titulo) > 150 or not conteudo:
        flash("Preencha o título (máx. 150 caracteres) e o conteúdo do capítulo.", "error")
        return render_template(
            "adicionar_capitulo.html",
            obra=obra,
            status_validos=STATUS_VALIDOS,
            titulo=titulo,
            conteudo=conteudo,
            status_selecionado=novo_status or obra["status"],
        )

    numero = Capitulo.ProximoNumero(obra_id)
    capitulo = Capitulo(numero, titulo, conteudo, obra_id, session["user_id"])
    capitulo.Salvar()

    status_mudou = novo_status in STATUS_VALIDOS and novo_status != obra["status"]
    if status_mudou:
        Obras.AtualizarStatus(obra_id, session["user_id"], novo_status)

    for seguidor_id in Acompanhamento.ListarSeguidores(obra_id):
        if seguidor_id != session["user_id"]:
            msg = Mensagem(
                usuario_id=seguidor_id,
                categoria="atualizacoes",
                titulo=f"Novo capítulo em '{obra['titulo']}'!",
                conteudo=f"'{titulo}' acabou de ser lançado.",
            )
            msg.Salvar()

    detalhe_status = f" Status da obra alterado para '{novo_status}'." if status_mudou else ""
    msg_autor = Mensagem(
        usuario_id=session["user_id"],
        categoria="atualizacoes",
        titulo=f"Capítulo publicado em '{obra['titulo']}'",
        conteudo=f"Você publicou '{titulo}'.{detalhe_status}",
    )
    msg_autor.Salvar()

    current_app.logger.info("Capítulo '%s' adicionado à obra id=%s pelo usuário_id=%s", titulo, obra_id, session["user_id"])
    flash(f"Capítulo '{titulo}' cadastrado com sucesso!", "success")
    return redirect("/obras/minhas")


@capitulos_bp.route("/<int:id_capitulo>/editar", methods=["GET", "POST"])
@login_required
def editar_capitulo(id_capitulo):
    """Permite ao autor editar título e conteúdo do capítulo."""
    capitulo = Capitulo.BuscarPorIdEUsuario(id_capitulo, session["user_id"])
    if not capitulo:
        flash("Capítulo não encontrado ou sem permissão.", "error")
        return redirect("/obras/minhas")

    if request.method == "GET":
        return render_template("editar_capitulo.html", capitulo=capitulo)

    titulo = request.form.get("titulo", "").strip()
    conteudo = request.form.get("conteudo", "").strip()

    if not titulo or len(titulo) > 150 or not conteudo:
        flash("Preencha o título e o conteúdo do capítulo.", "error")
        return redirect(f"/capitulos/{id_capitulo}/editar")

    Capitulo.Atualizar(id_capitulo, session["user_id"], titulo, conteudo)
    obra = Obras.BuscarPorId(capitulo["obra_id"])
    if obra:
        msg = Mensagem(
            usuario_id=session["user_id"],
            categoria="atualizacoes",
            titulo=f"Capítulo editado em '{obra['titulo']}'",
            conteudo=f"Você atualizou o capítulo '{titulo}'.",
        )
        msg.Salvar()

    current_app.logger.info("Capítulo id=%s atualizado pelo usuário_id=%s", id_capitulo, session["user_id"])
    flash("Capítulo atualizado com sucesso!", "success")
    return redirect(f"/capitulos/obra/{capitulo['obra_id']}")


@capitulos_bp.route("/<int:id_capitulo>/excluir", methods=["POST"])
@login_required
def excluir_capitulo(id_capitulo):
    """Exclui um capítulo validando o dono e registra a exclusão no canal de Mensagens do autor."""
    capitulo = Capitulo.BuscarPorIdEUsuario(id_capitulo, session["user_id"])
    if not capitulo:
        flash("Capítulo não encontrado ou sem permissão.", "error")
        return redirect("/obras/minhas")

    obra_id = capitulo["obra_id"]
    obra = Obras.BuscarPorId(obra_id)
    Capitulo.Excluir(id_capitulo, session["user_id"])

    if obra:
        msg = Mensagem(
            usuario_id=session["user_id"],
            categoria="atualizacoes",
            titulo=f"Capítulo excluído em '{obra['titulo']}'",
            conteudo=f"Você excluiu o capítulo '{capitulo['titulo']}'.",
        )
        msg.Salvar()

    current_app.logger.info("Capítulo id=%s excluído pelo usuário_id=%s", id_capitulo, session["user_id"])
    flash("Capítulo excluído com sucesso.", "success")
    return redirect(f"/capitulos/obra/{obra_id}")
