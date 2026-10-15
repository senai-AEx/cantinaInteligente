
from flask import Flask, jsonify
from conexao import conectar
import mysql.connector
#Aplicação Flask criada
app = Flask(__name__)

# Rota de teste para verificar se a API está funcionando
@app.route("/")
def inicio():
    return jsonify({
        "mensagem": "API Cantina Inteligente funcionando!"
    })

# Rota para listar todos os produtos cadastrados no banco de dados
@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    conexao = None
    cursor = None

    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_produto,
                codigo_produto,
                nome,
                descricao,
                categoria,
                preco_centavos,
                quantidade_estoque,
                estoque_minimo,
                estoque_maximo,
                validade,
                foto_caminho,
                zero_lactose,
                zero_acucar,
                status
            FROM produtos
            ORDER BY nome
        """)

        produtos = cursor.fetchall()
        # Converte a data de validade para o formato ISO 8601 (YYYY-MM-DD) antes de retornar a resposta
        for produto in produtos:
            if produto["validade"] is not None:
                produto["validade"] = produto["validade"].isoformat()

        return jsonify(produtos), 200

    except mysql.connector.Error:
        app.logger.exception("Erro ao consultar produtos")
        return jsonify({
            "erro": "Erro ao consultar produtos no banco de dados"
        }), 500
    
    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()

# Inicia a aplicação Flask
if __name__ == "__main__":
    app.run(debug=True)
