"""Aplicação Flask da Cantina Inteligente.

Um único servidor entrega as telas (src/frontend) e a API (/api/...), na mesma
porta. Assim a sessão de login funciona por cookie, sem CORS.

Executar a partir da raiz do repositório:
    python -m flask --app src.backend.app run --debug
(ou simplesmente `python iniciar.py`).
"""
from datetime import timedelta
import os
from pathlib import Path
import secrets

import mysql.connector
from flask import Flask, abort, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException

from .admin import admin_api
from .carteira import carteira_api
from .compras import compras_api
from .conexao import conectar
from .erros import ErroAplicacao
from .produtos import produtos_api
from .qr import qr_api
from .uploads import uploads_api
from .usuarios import auth_api, usuarios_admin_api

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
PASTA_FRONTEND = RAIZ_PROJETO / "src" / "frontend"

app = Flask(__name__, static_folder=None)
# Mantém acentos legíveis nas respostas JSON.
app.json.ensure_ascii = False
# Limite do corpo da requisição (~6 MiB): a foto pode ter até 5 MiB.
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024
app.config["PRODUCT_IMAGE_FOLDER"] = RAIZ_PROJETO / "assets" / "produtos"
# Em desenvolvimento, o navegador sempre busca a versão mais nova das telas.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# Sessão de login: cookie assinado, inacessível ao JavaScript e não enviado
# por outros sites. Sem SECRET_KEY no .env, uma chave temporária é gerada e os
# logins caem a cada reinício do servidor.
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_NAME="cantina_sessao",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)

MODULOS = (
    auth_api,
    usuarios_admin_api,
    produtos_api,
    uploads_api,
    carteira_api,
    compras_api,
    admin_api,
    qr_api,
)
for modulo in MODULOS:
    app.register_blueprint(modulo)


# ---------- saúde ----------

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


# ---------- telas (arquivos estáticos) ----------

@app.get("/")
def inicio():
    return send_from_directory(PASTA_FRONTEND, "index.html")


@app.get("/assets/produtos/<path:nome>")
def foto_produto(nome):
    return send_from_directory(app.config["PRODUCT_IMAGE_FOLDER"], nome)


@app.get("/<path:caminho>")
def arquivo_frontend(caminho):
    if caminho.startswith("api/"):
        abort(404)
    return send_from_directory(PASTA_FRONTEND, caminho)


# ---------- erros ----------

@app.errorhandler(ErroAplicacao)
def erro_aplicacao(exc):
    return jsonify(exc.para_json()), exc.status


@app.errorhandler(mysql.connector.Error)
def erro_banco(exc):
    app.logger.error("Erro no MySQL", exc_info=(type(exc), exc, exc.__traceback__))
    return jsonify(erro="Não foi possível acessar o banco de dados. Tente novamente."), 503


@app.errorhandler(RuntimeError)
def erro_configuracao(exc):
    app.logger.error("Erro de configuração: %s", exc)
    return jsonify(erro=str(exc)), 503


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
