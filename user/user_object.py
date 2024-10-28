from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash

import app


class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    @classmethod
    def get_user_by_email(cls, email):
        db_user = current_app.db.get_user_by_email(email)
        if db_user:
            return cls(**db_user)
        return None

    @classmethod
    def get_user_by_id(cls, user_id):
        db_user = current_app.db.get_user_by_id(user_id)
        if db_user:
            return cls(**db_user)
        return None

    def verify_password(self, password):
        return check_password_hash(self.password, password)

def load_user(user_id):
    db_user = current_app.db.get_user_by_id(user_id)
    if db_user:
        return User(**db_user)
    return None
