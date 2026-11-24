from flask import Blueprint, session, redirect, flash, current_app

logout_bp = Blueprint("logout", __name__, url_prefix="/logout")


@logout_bp.route("/")
def logout():
    """Encerra a sessão do usuário no servidor e redireciona para a página inicial."""
    username = session.get("username")
    session.clear()
    if username:
        current_app.logger.info("Logout realizado: %s", username)
    flash("Você saiu da sua conta.", "info")
    return redirect("/")