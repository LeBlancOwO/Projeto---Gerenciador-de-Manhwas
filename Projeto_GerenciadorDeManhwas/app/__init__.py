from flask import Flask
from app.controllers.login_controller import login_bp

def create_app():
    
    app = Flask(__name__, template_folder="views", static_folder="static")

    app.register_blueprint(login_bp)

    return app