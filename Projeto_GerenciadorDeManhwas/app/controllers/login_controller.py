from flask import Blueprint, render_template

login_bp = Blueprint ("login", __name__, url_prefix="/login")

@login_bp.route("/")
def renderizar_login():
    return render_template("login.html")