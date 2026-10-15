from flask import Flask, jsonify
from .db import conectar

app  = Flask(__name__)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/api/health/db")
def health_db():
    conexao = conectar()

    try:
        cursor = conexao.cursor()

        try:
            cursor.execute("SELECT 1 AS resultado")
            linha = cursor.fetchone()
        finally:
            cursor.close()

        return jsonify({
            "status": "ok",
            "banco": "conectado",
            "resultado": linha[0]
        })
    finally:
        conexao.close()

