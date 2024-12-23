import os
import mysql.connector
from dotenv import load_dotenv
from pino import pino

load_dotenv('.env')
logger = pino()


class Database:
    def __init__(self, ):
        self.host = os.environ.get('DB_HOST')
        self.user = os.environ.get('DB_USERNAME')
        self.password = os.environ.get('DB_PASSWORD')
        self.database = os.environ.get('DB_NAME')

    def create_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            port=3306,
            password=self.password,
            database=self.database
        )

    def create_user(self, email, password, name):
        query = f"""
        INSERT INTO users (email, password, name)
        VALUES (%s, %s, %s)
        """

        with self.create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (email, password, name))
                connection.commit()

    def create_subscription(self, user_id):
        query = f"""
        INSERT INTO subscriptions (user_id)
        VALUES (%s)
        """

        with self.create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                connection.commit()

    def get_user_by_email(self, email):
        query = f"""
        SELECT * FROM users
        WHERE email = %s
        """

        with self.create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (email,))
                user = cursor.fetchone()
                return {'id': user[0], 'email': user[1], 'password': user[2], 'name': user[3]} if user else None

    def get_user_by_id(self, user_id):
        query = f"""
        SELECT * FROM users
        WHERE id = %s
        """

        with self.create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                user = cursor.fetchone()
                return {'id': user[0], 'email': user[1], 'password': user[2], 'name': user[3]} if user else None

    def log_call(self, user_id, response, path_to_image):
        recommendations_query = f"""
        INSERT INTO recommendations (user_id, response, image_path)
        VALUES (%s, %s, %s)
        """

        subscriptions_query = f"""
        UPDATE subscriptions
        SET used_calls=used_calls+1, remaining_calls=remaining_calls-1
        WHERE user_id = {user_id}
        """

        with self.create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(recommendations_query, (user_id, response, path_to_image))
                cursor.execute(subscriptions_query)
                connection.commit()

    def delete_user(self, user_id):
        user_query = f"""
        DELETE FROM users
        WHERE id = %s
        """
        subscription_query = f"""
        DELETE FROM subscriptions
        WHERE user_id = %s
        """

        recommendations_query = f"""
        DELETE FROM recommendations
        WHERE user_id = %s
        """

        with self.create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(user_query, (user_id,))
                cursor.execute(subscription_query, (user_id,))
                cursor.execute(recommendations_query, (user_id,))
                connection.commit()

    def get_remaining_calls(self, id):
        query = f"""
        SELECT remaining_calls
        FROM subscriptions
        WHERE user_id = {id}
        """

        with self.create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                remaining_calls = cursor.fetchone()[0]
                return remaining_calls

    def get_previous_recommendations(self, user_id):
        query = f"""
        SELECT response, image_path, created_at
        FROM recommendations
        WHERE user_id = {user_id}
        """

        with self.create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                recommendations = cursor.fetchall()
                return recommendations
