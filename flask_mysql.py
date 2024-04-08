from flask import Flask
from typing import Union

from mysql.connector import MySQLConnection, connect


class MySQL:
    def __init__(self, app: Union[Flask, None] = None):
        self.app: Flask = None
        self.connection: MySQLConnection = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        self.app.config.setdefault('MYSQL_HOST', 'localhost')
        self.app.config.setdefault('MYSQL_PORT', 3306)

        if any(key not in self.app.config for key in ('MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB')):
            raise Exception("No MYSQL_USER, MYSQL_PASSWORD or MYSQL_DB provided")

        self.connection = connect(
            host=app.config['MYSQL_HOST'],
            port=app.config['MYSQL_PORT'],
            database=app.config['MYSQL_DB'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )

    def cursor(self):
        return self.connection.cursor()
