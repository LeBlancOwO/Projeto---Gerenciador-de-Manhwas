from flask import Flask
from app.models.cadastro import Cadastro
from app.models.obras import Obras

def create_app():
    
    app = Flask(__name__, template_folder="views", static_folder="static")

    from app.controllers.homepage_controller import homepage_bp
    app.register_blueprint(homepage_bp)

    from app.controllers.login_controller import login_bp
    app.register_blueprint(login_bp)

    from app.controllers.cadastro_controller import cadastro_bp
    app.register_blueprint(cadastro_bp)

    from app.controllers.obras_controller import obras_bp
    app.register_blueprint(obras_bp)

    Cadastro.Criar_tabela()

    Obras.Criar_tabela()

    return app