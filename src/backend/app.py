import mysql.connector
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .conexao import conectar

app = Flask(__name__)
app.json.ensure_ascii = False


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


@app.get("/api/produtos")
def listar_produtos():
    connection = None
    cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT
                   id_produto, codigo_produto, nome, descricao, categoria,
                   preco_centavos, quantidade_estoque, estoque_minimo,
                   estoque_maximo, validade, foto_caminho, zero_lactose,
                   zero_acucar, status, criado_em, atualizado_em
               FROM produtos
               ORDER BY nome, id_produto"""
        )
        products = cursor.fetchall()
        for product in products:
            if product["validade"] is not None:
                product["validade"] = product["validade"].isoformat()
            for key in ("criado_em", "atualizado_em"):
                if product[key] is not None:
                    product[key] = product[key].isoformat() + "Z"
            product["zero_lactose"] = bool(product["zero_lactose"])
            product["zero_acucar"] = bool(product["zero_acucar"])
        return jsonify(products), 200
    except mysql.connector.Error:
        app.logger.exception("Falha ao consultar produtos")
        return jsonify(erro="Banco indisponível ou estrutura ainda não criada."), 503
    except RuntimeError as exc:
        app.logger.error("Configuração do MySQL incompleta: %s", exc)
        return jsonify(erro="Configure a conexão com o banco no arquivo .env."), 503
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


if __name__ == "__main__":
    app.run(debug=True)
