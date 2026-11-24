from flask import Blueprint, render_template, session
from app.utils.auth_middleware import login_required
from app.models.mensagem import Mensagem

mensagens_bp = Blueprint("mensagens", __name__, url_prefix="/mensagens")


@mensagens_bp.route("/")
@login_required
def canal_mensagens():
    """Exibe o canal de mensagens e atualizações do usuário."""
    user_id = session["user_id"]
    mensagens = Mensagem.ListarPorUsuario(user_id)
    Mensagem.MarcarTodasComoLidas(user_id)

    return render_template("mensagens.html", mensagens=mensagens)
