
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# Localiza a raiz do projeto
RAIZ_PROJETO = Path(__file__).resolve().parents[2]

# Carrega as configurações do arquivo .env
load_dotenv(RAIZ_PROJETO / ".env")


def conectar():
    """Cria e retorna uma conexão com o MySQL."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


if __name__ == "__main__":
    try:
        conexao = conectar()

        cursor = conexao.cursor()
        cursor.execute("SELECT DATABASE()")

        banco = cursor.fetchone()[0]

        print("Conexão com MySQL realizada com sucesso!")
        print(f"Banco conectado: {banco}")

        cursor.close()
        conexao.close()

    except mysql.connector.Error as erro:
        print(f"Erro ao conectar ao MySQL: {erro}")
