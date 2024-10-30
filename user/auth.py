from flask import request, render_template, redirect, Blueprint, current_app, flash, url_for
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash

from user.user_object import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        email = request.form.get("email").lower()

        user = User.get_user_by_email(email)
        if user:
            return redirect(url_for("auth.login", email=email))
        else:
            return render_template("register.html", email=email)

    return render_template("login_only_email.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not email or not password or not confirm_password:
            return render_template("register.html", message="Please fill in all fields.")

        if password != confirm_password:
            return render_template("register.html", message="Passwords do not match.")

        user = User.get_user_by_email(email)
        if user:
            return render_template("login.html", message="User already exists.")

        hashed_password = generate_password_hash(password)
        current_app.db.create_user(email, hashed_password)
        login_user(user)

        return redirect(url_for("auth.login", email=email))

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
    # if 'user_id' not in session:
    #     flash("You must be logged in to view this page.")
    #     return redirect(url_for('auth.login'))  # Redirect to login page if not logged in

    return render_template("landing_page.html", user_id=current_user.id)  # Render your landing page template


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return render_template("login_only_email.html")
