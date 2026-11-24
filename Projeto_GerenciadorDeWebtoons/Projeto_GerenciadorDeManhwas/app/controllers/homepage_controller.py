from flask import Blueprint, render_template, request, make_response, redirect
from app.models.obras import Obras, TAGS_PADRAO
from app.models.comunicado import Comunicado

homepage_bp = Blueprint("homepage", __name__)


@homepage_bp.route("/")
def renderizar_homepage():
    """Página inicial pública: exibe carrossel, comunicados do admin e catálogo com filtros."""
    busca = request.args.get("busca", "").strip()
    status = request.args.get("status", "").strip()
    tags_incluir = [t for t in request.args.getlist("tags_incluir") if t in TAGS_PADRAO]
    tags_excluir = [t for t in request.args.getlist("tags_excluir") if t in TAGS_PADRAO]

    obras = Obras.Listar(
        busca=busca or None,
        status=status or None,
        tags_incluir=tags_incluir,
        tags_excluir=tags_excluir,
    )
    comunicados = Comunicado.Listar()
    return render_template(
        "homepage.html",
        obras=obras,
        comunicados=comunicados,
        busca=busca,
        status_filtro=status,
        tags_incluir=tags_incluir,
        tags_excluir=tags_excluir,
        tags_padrao=TAGS_PADRAO,
    )


@homepage_bp.route("/tema/<tema>")
def alternar_tema(tema):
    """Salva a preferência de tema (claro/escuro) em um cookie no navegador por 30 dias."""
    if tema not in ("claro", "escuro"):
        tema = "claro"
    destino = request.referrer or "/"
    resposta = make_response(redirect(destino))
    resposta.set_cookie("tema", tema, max_age=60 * 60 * 24 * 30)
    return resposta