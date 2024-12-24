import json
import os
import hmac
import hashlib
from flask import Flask, redirect, url_for, request, abort
from flask_login import LoginManager
from pino import pino
from service.recommendation import service_bp
from user.auth import auth_bp
from database import Database
from user.user_object import load_user
from dotenv import load_dotenv
from config import Config
from flask_cors import CORS
import git

load_dotenv('.env')
logger = pino()
login_manager = LoginManager()
login_manager.login_view = "auth"


def create_app():
    app = Flask(__name__)
    CORS(app)
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
    app.add_url_rule("/update_server", view_func=webhook, methods=['POST'])

    return app


def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split('=', 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, 'latin-1')
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)


def webhook():
    if request.method != 'POST':
        return 'OK'
    else:
        abort_code = 418
        if 'X-Github-Event' not in request.headers:
            abort(abort_code)
        if 'X-Github-Delivery' not in request.headers:
            abort(abort_code)
        if 'X-Hub-Signature' not in request.headers:
            abort(abort_code)
        if not request.is_json:
            abort(abort_code)
        if 'User-Agent' not in request.headers:
            abort(abort_code)
        ua = request.headers.get('User-Agent')
        if not ua.startswith('GitHub-Hookshot/'):
            abort(abort_code)

        event = request.headers.get('X-GitHub-Event')
        if event == "ping":
            return json.dumps({'msg': 'Hi!'})
        if event != "push":
            return json.dumps({'msg': "Wrong event type"})

        x_hub_signature = request.headers.get('X-Hub-Signature')
        # webhook content type should be application/json for request.data to have the payload
        # request.data is empty in case of x-www-form-urlencoded
        w_secret = os.getenv('WEBHOOK_SECRET')
        if not is_valid_signature(x_hub_signature, request.data, w_secret):
            print('Deploy signature failed: {sig}'.format(sig=x_hub_signature))
            abort(abort_code)

        payload = request.get_json()
        if payload is None:
            print('Deploy payload is empty: {payload}'.format(
                payload=payload))
            abort(abort_code)

        if payload['ref'] != 'refs/heads/main':
            return json.dumps({'msg': 'Not master; ignoring'})

        repo = git.Repo('/home/valeman100/book-recommendation-api/.git')
        origin = repo.remotes.origin

        pull_info = origin.pull()

        if len(pull_info) == 0:
            return json.dumps({'msg': "Didn't pull any information from remote!"})
        if pull_info[0].flags > 128:
            return json.dumps({'msg': "Didn't pull any information from remote!"})

        commit_hash = pull_info[0].commit.hexsha
        build_commit = f'build_commit = "{commit_hash}"'
        print(f'{build_commit}')
        return 'Updated PythonAnywhere server to commit {commit}'.format(commit=commit_hash)


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
