"""Conexão e transações do MySQL para o backend da AV04."""
from contextlib import contextmanager
import os
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv, find_dotenv

# Carrega as variáveis de ambiente .ENV
load_dotenv(find_dotenv())

def conectar():
    """Abre conexão do request e configura timestamps da sessão em UTC."""
    required = ("MYSQL_HOST", "MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            "Preencha estas variáveis em .env: " + ", ".join(missing)
        )
    try:
        port = int(os.getenv("MYSQL_PORT", "3306"))
    except ValueError as exc:
        raise RuntimeError("MYSQL_PORT precisa ser um número inteiro.") from exc
    if not 1 <= port <= 65535:
        raise RuntimeError("MYSQL_PORT precisa estar entre 1 e 65535.")

    connection = mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=port,
        database=os.environ["MYSQL_DATABASE"],
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        charset="utf8mb4",
        connection_timeout=5,
        autocommit=False,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET SESSION time_zone = '+00:00'")
    except Exception:
        connection.close()
        raise
    return connection


@contextmanager
def transacao():
    """Confirma todas as gravações em conjunto ou reverte em caso de erro."""
    connection = conectar()
    try:
        connection.start_transaction()
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()