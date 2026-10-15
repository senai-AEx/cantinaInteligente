import mysql.connector
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .conexao import conectar
from .produtos import produtos_api

app = Flask(__name__)
app.json.ensure_ascii = False
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5500",
                "http://127.0.0.1:5500",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        }
    },
    allow_headers=["Content-Type", "X-Actor"],
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
app.register_blueprint(produtos_api)


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
