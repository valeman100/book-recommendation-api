import json

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash


class User(UserMixin):
    def __init__(self, id, email, password, name):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.remaining_calls = current_app.db.get_remaining_calls(id)

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

    def get_previous_recommendations(self):
        response = current_app.db.get_previous_recommendations(self.id)
        recommendations = []
        for recommendation in response:
            recommendations.append({"photo_url": recommendation[1],
                                   "photo_description": str(recommendation[2]),
                                   **json.loads(recommendation[0])})
        return recommendations


def load_user(user_id):
    db_user = current_app.db.get_user_by_id(user_id)
    if db_user:
        return User(**db_user)
    return None
