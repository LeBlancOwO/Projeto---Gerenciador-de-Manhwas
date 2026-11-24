import logging
from flask import Flask, render_template, session
from app.models.usuario import Usuario
from app.models.obras import Obras
from app.models.capitulo import Capitulo
from app.models.leitura import Leitura
from app.models.comentario import Comentario
from app.models.mensagem import Mensagem
from app.models.acompanhamento import Acompanhamento
from app.models.comunicado import Comunicado


def create_app():
    """Fábrica da aplicação Flask: configura secret_key, Blueprints e tratadores de erro."""
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.secret_key = "Y0u'r&N0th1ng,ButN0tT0M&;-;"

    logging.basicConfig(level=logging.INFO)

    from app.controllers.homepage_controller import homepage_bp
    app.register_blueprint(homepage_bp)

    from app.controllers.login_controller import login_bp
    app.register_blueprint(login_bp)

    from app.controllers.cadastro_controller import cadastro_bp
    app.register_blueprint(cadastro_bp)

    from app.controllers.logout_controller import logout_bp
    app.register_blueprint(logout_bp)

    from app.controllers.perfil_controller import perfil_bp
    app.register_blueprint(perfil_bp)

    from app.controllers.mensagens_controller import mensagens_bp
    app.register_blueprint(mensagens_bp)

    from app.controllers.obras_controller import obras_bp
    app.register_blueprint(obras_bp)

    from app.controllers.capitulos_controller import capitulos_bp
    app.register_blueprint(capitulos_bp)

    from app.controllers.admin_controller import admin_bp
    app.register_blueprint(admin_bp)

    @app.context_processor
    def injetar_mensagens_nao_lidas():
        """Disponibiliza a contagem de mensagens não lidas em todos os templates."""
        user_id = session.get("user_id")
        if user_id:
            try:
                return {"mensagens_nao_lidas": Mensagem.ContarNaoLidas(user_id)}
            except Exception:
                return {"mensagens_nao_lidas": 0}
        return {"mensagens_nao_lidas": 0}

    @app.errorhandler(404)
    def pagina_nao_encontrada(erro):
        app.logger.warning("Página não encontrada (404): %s", erro)
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def acesso_negado(erro):
        app.logger.warning("Acesso negado (403): %s", erro)
        return render_template("403.html"), 403

    return app