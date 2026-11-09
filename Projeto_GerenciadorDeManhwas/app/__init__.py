from flask import Flask

def create_app():
    
    app = Flask(__name__, template_folder="views", static_folder="static")

    from app.controllers.homepage_controller import homepage_bp
    app.register_blueprint(homepage_bp)

    from app.controllers.login_controller import login_bp
    app.register_blueprint(login_bp)

    from app.controllers.cadastro_controller import cadastro_bp
    app.register_blueprint(cadastro_bp)

    return app