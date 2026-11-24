from flask import session, redirect, g, flash
from functools import wraps
from app.models.usuario import Usuario


def login_required(func):
    """Middleware (decorator) que protege rotas restritas e valida usuário e suspensão no banco."""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")

        # Se não existir user_id na sessão, redireciona para a tela de login
        if not user_id:
            flash("Faça login para acessar esta página.", "warning")
            return redirect("/login")

        # Confirma no banco de dados se o usuário ainda existe
        usuario = Usuario.Buscar_Id(user_id)
        if not usuario:
            session.clear()
            flash("Sessão inválida. Faça login novamente.", "warning")
            return redirect("/login")

        # Se a conta tiver sido suspensa pelo administrador, encerra a sessão imediatamente
        if usuario["suspenso"]:
            session.clear()
            flash("Sua conta foi suspensa pela administração.", "error")
            return redirect("/login")

        # Disponibiliza o usuário autenticado no objeto global g da requisição
        g.usuario = usuario
        return func(*args, **kwargs)

    return decorated_function
