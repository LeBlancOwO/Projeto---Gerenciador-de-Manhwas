from flask import Blueprint, session, render_template, redirect, request, flash, abort, current_app
from app.utils.auth_middleware import login_required
from app.models.obras import Obras
from app.models.comunicado import Comunicado

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/pendentes")
@login_required
def Listar_pendentes():
    """Lista obras aguardando análise e exibe o formulário de comunicados (apenas administradores)."""
    if session.get("tipo") != "admin":
        abort(403)

    obras = Obras.ListarPendentes()
    return render_template("pendentes.html", obras=obras)


@admin_bp.route("/aprovar/<int:id_obra>")
@login_required
def Aprovar(id_obra):
    """Aprova uma obra pendente para exibição no catálogo público."""
    if session.get("tipo") != "admin":
        abort(403)

    Obras.Aprovar(id_obra)
    current_app.logger.info("Obra id=%s aprovada pelo admin %s", id_obra, session.get("username"))
    flash("Obra aprovada com sucesso!", "success")
    return redirect("/admin/pendentes")


@admin_bp.route("/desaprovar/<int:id_obra>")
@login_required
def renderizar_desaprovacao(id_obra):
    """Exibe o formulário para informar a justificativa da desaprovação."""
    if session.get("tipo") != "admin":
        abort(403)

    return render_template("desaprovar.html", id_obra=id_obra)


@admin_bp.route("/desaprovar/salvar/<int:id_obra>", methods=["POST"])
@login_required
def Salvar_desaprovacao(id_obra):
    """Registra a desaprovação da obra com a justificativa informada."""
    if session.get("tipo") != "admin":
        abort(403)

    justificativa = request.form.get("justificativa", "").strip()
    if len(justificativa) < 5:
        flash("A justificativa deve ter pelo menos 5 caracteres.", "error")
        return redirect(f"/admin/desaprovar/{id_obra}")

    Obras.Desaprovar(id_obra, justificativa)
    current_app.logger.info("Obra id=%s desaprovada pelo admin %s", id_obra, session.get("username"))
    flash("Obra desaprovada com justificativa salva.", "info")
    return redirect("/admin/pendentes")


@admin_bp.route("/comunicados/adicionar", methods=["POST"])
@login_required
def Publicar_comunicado():
    """Permite ao administrador publicar um comunicado importante na tela inicial."""
    if session.get("tipo") != "admin":
        abort(403)

    titulo = request.form.get("titulo", "").strip()
    conteudo = request.form.get("conteudo", "").strip()

    if len(titulo) < 3 or len(titulo) > 150 or len(conteudo) < 5:
        flash("Preencha o título (3-150) e o conteúdo do comunicado.", "error")
        return redirect("/admin/pendentes")

    comunicado = Comunicado(titulo, conteudo, session["user_id"])
    comunicado.Salvar()
    current_app.logger.info("Comunicado '%s' publicado pelo admin %s", titulo, session.get("username"))
    flash("Comunicado publicado na página inicial!", "success")
    return redirect("/admin/pendentes")


@admin_bp.route("/comunicados/<int:id_comunicado>/excluir", methods=["POST"])
@login_required
def Excluir_comunicado(id_comunicado):
    """Permite ao administrador remover um comunicado da página inicial."""
    if session.get("tipo") != "admin":
        abort(403)

    Comunicado.Excluir(id_comunicado)
    current_app.logger.info("Comunicado id=%s excluído pelo admin %s", id_comunicado, session.get("username"))
    flash("Comunicado removido.", "info")
    return redirect("/")