import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from pino import pino
from service.recommendation import service_bp
from user.auth import auth_bp
from database import Database
from user.user_object import load_user
from dotenv import load_dotenv
from config import Config

load_dotenv('/Users/vale/Developer/pycharm/book-recommendation-api/.env')

logger = pino()

login_manager = LoginManager()
login_manager.login_view = "auth"


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize and configure extensions
    login_manager.init_app(app)
    login_manager.user_loader(load_user)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(service_bp)

    # Attach database instance to the app
    app.db = Database()

    # Add routes
    app.add_url_rule("/health", view_func=health_check)
    app.add_url_rule("/", view_func=index)

    return app


def health_check():
    logger.info("Health")
    return "Ok!"


def index():
    return redirect(url_for('auth.auth'))

def list_routes(app):
    logger.info("Listing all endpoints registered in the application:")
    for rule in app.url_map.iter_rules():
        endpoint = rule.endpoint
        path = rule.rule
        methods = ', '.join(sorted(rule.methods))
        logger.info(f"Endpoint: {endpoint}, Path: {path}, Methods: {methods}")

#
