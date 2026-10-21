from flask import Flask

# Facilita trabalhar com caminhos de arquivos e diretórios.
from pathlib import Path
# CORS significa Cross-Origin Resource Sharing (Compartilhamento de Recursos entre Origens).
# É um mecanismo de segurança dos navegadores que controla se uma página
# carregada de determinada origem pode acessar recursos de outra origem.
# Será utilizado para permitir que o front-end (React + Vite) faça
# requisições ao back-end (Flask + Python), pois, durante o desenvolvimento,
# eles podem estar sendo executados em portas diferentes.
from flask_cors import CORS

# Rotas
from routes import rotas

# Aplicação principal
app = Flask(__name__)

# O Flask incorpora suas rotas à aplicação principal.
app.register_blueprint(rotas)


# Faz com que caracteres acentuados sejam preservados nas respostas JSON
app.json.ensure_ascii = False

# Define o tamanho máximo permitido para uma imagem: 5 MiB
LIMITE_IMAGEM_BYTES = 5 * 1024 * 1024
# Configura o limite total do corpo da requisição HTTP em aproximadamente 6 MiB.
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024
# Define onde as imagens serão armazenadas.
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



if __name__ == "__main__":
    app.run()