from flask_oauthlib.client import OAuth
from flask import request, render_template, redirect, Blueprint, current_app, flash, url_for, session
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash
from user.user_object import User
from google.oauth2 import id_token
from google.auth.transport import requests

auth_bp = Blueprint('auth', __name__)

oauth = OAuth()


@auth_bp.record_once
def on_load(state):
    app = state.app
    oauth.init_app(app)
    app.google = oauth.remote_app(
        'google',
        consumer_key=app.config['GOOGLE_CLIENT_ID'],
        consumer_secret=app.config['GOOGLE_CLIENT_SECRET'],
        request_token_params={
            'scope': 'email',
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )


@auth_bp.route("/", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        email = request.form.get("email").lower()

        user = User.get_user_by_email(email)
        if user.password:
            return redirect(url_for("auth.login", email=email))
        elif user:
            flash("You have previously logged in with Google. Please login with Google.")
            return redirect(url_for("auth.auth"))
        else:
            return render_template("register.html", email=email)

    return render_template("login_only_email.html",
                           google_client_id=current_app.config['GOOGLE_CLIENT_ID'])


@auth_bp.route("/google/callback", methods=["POST"])
def google_callback():
    token = request.form.get("credential")
    user_info = id_token.verify_oauth2_token(token, requests.Request(), current_app.config['GOOGLE_CLIENT_ID'])

    if user_info:
        email = user_info["email"]
        name = user_info["name"]
        picture = user_info["picture"]
        user = User.get_user_by_email(email)

        if not user:
            current_app.db.create_user(email, None, name)

        user = User.get_user_by_email(email)
        login_user(user)
        return redirect(url_for("auth.landing_page"))

    flash("Google login failed.")
    return redirect(url_for("auth.register"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        name = request.form.get("name")

        if not email or not password or not confirm_password:
            return render_template("register.html", message="Please fill in all fields.")

        if password != confirm_password:
            return render_template("register.html", message="Passwords do not match.")

        user = User.get_user_by_email(email)
        if not user.password:
            flash("You have previously logged in with Google. Please login with Google.")
            return redirect(url_for("auth.auth"))
        elif user:
            return render_template("login.html", message="User already exists.")

        hashed_password = generate_password_hash(password)
        current_app.db.create_user(email, hashed_password, name)
        login_user(user)

        return redirect(url_for("auth.landing_page"))

    email = request.args.get("email", "")
    return render_template("register.html", email=email)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")

        user = User.get_user_by_email(email)

        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for("auth.landing_page"))
        else:
            return render_template("login.html", message="Invalid username or password.")

    email = request.args.get("email", "")
    return render_template("login.html", email=email)


@auth_bp.route("/landing-page", methods=["GET"])
@login_required
def landing_page():
    return render_template("landing_page.html", user_id=current_user.id)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return render_template("login_only_email.html",
                           google_client_id=current_app.config['GOOGLE_CLIENT_ID'])
