import mysql.connector
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .conexao import conectar
from .produtos import produtos_api

app = Flask(__name__)
app.json.ensure_ascii = False
LIMITE_IMAGEM_BYTES = 5 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024
app.config["PRODUCT_IMAGE_FOLDER"] = Path(__file__).resolve().parents[2] / "assets" / "produtos"

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
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
app.register_blueprint(produtos_api)


@app.post("/api/uploads/produtos")
def enviar_foto_produto():
    imagem = request.files.get("imagem")
    if imagem is None or not imagem.filename:
        return jsonify(erro="Selecione uma imagem para enviar.", campos={"imagem": "Selecione uma imagem."}), 422

    extensao = Path(imagem.filename).suffix.lower()
    validar_assinatura = {
        ".jpg": lambda dados: dados.startswith(b"\xff\xd8\xff"),
        ".jpeg": lambda dados: dados.startswith(b"\xff\xd8\xff"),
        ".png": lambda dados: dados.startswith(b"\x89PNG\r\n\x1a\n"),
        ".webp": lambda dados: len(dados) >= 12 and dados[:4] == b"RIFF" and dados[8:12] == b"WEBP",
    }.get(extensao)
    if validar_assinatura is None:
        return jsonify(erro="Formato de imagem não aceito.", campos={"imagem": "Use JPG, PNG ou WebP."}), 422

    dados = imagem.stream.read(LIMITE_IMAGEM_BYTES + 1)
    if not dados:
        return jsonify(erro="A imagem está vazia.", campos={"imagem": "Selecione uma imagem válida."}), 422
    if len(dados) > LIMITE_IMAGEM_BYTES:
        return jsonify(erro="A imagem excede o limite de 5 MB.", campos={"imagem": "Escolha uma imagem de até 5 MB."}), 413
    if not validar_assinatura(dados):
        return jsonify(erro="O conteúdo não corresponde a uma imagem válida.", campos={"imagem": "O arquivo não parece ser uma imagem JPG, PNG ou WebP válida."}), 422

    nome = f"{uuid4().hex}{extensao}"
    pasta = Path(app.config["PRODUCT_IMAGE_FOLDER"])
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / nome).write_bytes(dados)
    return jsonify(foto_caminho=f"assets/produtos/{nome}"), 201


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
