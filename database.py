import os
import mysql.connector
from dotenv import load_dotenv
from pino import pino

load_dotenv('/Users/vale/Developer/pycharm/book-recommendation-api/.env')
logger = pino()


class Database:
    def __init__(self, ):
        self.host = os.environ.get('DB_HOST')
        self.user = os.environ.get('DB_USERNAME')
        self.password = os.environ.get('DB_PASSWORD')
        self.database = 'book_recommendation_db'

    def create_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
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
