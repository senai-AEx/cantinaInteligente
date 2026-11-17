"""Aplicação Flask da Cantina Inteligente.

Executar a partir da raiz do repositório:
    python -m flask --app src.backend.app run --debug
(ou simplesmente `make up` / `make api`).
"""
from pathlib import Path

import mysql.connector
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .conexao import conectar
from .produtos import produtos_api
from .uploads import uploads_api

RAIZ_PROJETO = Path(__file__).resolve().parents[2]

app = Flask(__name__)
# Mantém acentos legíveis nas respostas JSON.
app.json.ensure_ascii = False
# Limite do corpo da requisição (~6 MiB): a foto pode ter até 5 MiB.
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024
app.config["PRODUCT_IMAGE_FOLDER"] = RAIZ_PROJETO / "assets" / "produtos"

# CORS permite que as telas servidas em outra porta (5500, Live Server ou Vite)
# chamem a API Flask na porta 5000 durante o desenvolvimento.
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5500",
                "http://127.0.0.1:5500",
                "http://localhost:5501",
                "http://127.0.0.1:5501",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        }
    },
    allow_headers=["Content-Type", "X-Actor"],
    methods=["GET", "POST", "PUT", "PATCH", "OPTIONS"],
)

app.register_blueprint(produtos_api)
app.register_blueprint(uploads_api)


@app.get("/")
def inicio():
    return jsonify(mensagem="API Cantina Inteligente funcionando!")


@app.get("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/health/db")
def health_db():
    connection = None
    cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 AS resultado")
        row = cursor.fetchone()
        return jsonify(status="ok", banco="conectado", resultado=row[0])
    except mysql.connector.Error:
        app.logger.exception("Falha ao verificar conexão com o MySQL")
        return jsonify(status="erro", banco="indisponivel"), 503
    except RuntimeError as exc:
        app.logger.error("Configuração do MySQL incompleta: %s", exc)
        return jsonify(status="erro", banco="configuracao_incompleta"), 503
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.errorhandler(HTTPException)
def erro_http(exc):
    response = exc.get_response()
    response.data = app.json.dumps({"erro": exc.description})
    response.content_type = "application/json"
    return response


@app.errorhandler(Exception)
def erro_interno(exc):
    app.logger.error(
        "Erro inesperado na API",
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return jsonify(erro="Erro interno no servidor."), 500


if __name__ == "__main__":
    app.run(debug=True)
