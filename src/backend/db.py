import os
import mysql.connector

def conectar():
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=3306,
        database=os.environ["MYSQL_DATABASE"],
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        connection_timeout=5,
    )