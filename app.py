from flask import Flask, redirect, url_for
from flask_login import LoginManager
from pino import pino

from service.recommendation import service_bp
from user.auth import auth_bp
from database import Database
from user.user_object import load_user

logger = pino()
app = Flask(__name__)
app.secret_key = "valeman100"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(load_user)
login_manager.login_view = "auth.auth"
app.register_blueprint(auth_bp)
app.register_blueprint(service_bp)
app.db = Database()


@app.route("/health", methods=['GET'])
def health():
    logger.info("Health")
    return "Ok!"

@app.route('/')
def index():
    return redirect(url_for('auth.auth'))

if __name__ == '__main__':
    app.run(debug=True)
