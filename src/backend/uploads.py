"""Upload das fotos dos produtos (JPG, PNG ou WebP de até 5 MB)."""
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request

LIMITE_IMAGEM_BYTES = 5 * 1024 * 1024

ASSINATURAS = {
    ".jpg": lambda dados: dados.startswith(b"\xff\xd8\xff"),
    ".jpeg": lambda dados: dados.startswith(b"\xff\xd8\xff"),
    ".png": lambda dados: dados.startswith(b"\x89PNG\r\n\x1a\n"),
    ".webp": lambda dados: len(dados) >= 12 and dados[:4] == b"RIFF" and dados[8:12] == b"WEBP",
}

uploads_api = Blueprint("uploads_api", __name__)


def _erro(mensagem, campo, status=422):
    return jsonify(erro=mensagem, campos={"imagem": campo}), status


@uploads_api.post("/api/uploads/produtos")
def enviar_foto_produto():
    imagem = request.files.get("imagem")
    if imagem is None or not imagem.filename:
        return _erro("Selecione uma imagem para enviar.", "Selecione uma imagem.")

    extensao = Path(imagem.filename).suffix.lower()
    validar_assinatura = ASSINATURAS.get(extensao)
    if validar_assinatura is None:
        return _erro("Formato de imagem não aceito.", "Use JPG, PNG ou WebP.")

    dados = imagem.stream.read(LIMITE_IMAGEM_BYTES + 1)
    if not dados:
        return _erro("A imagem está vazia.", "Selecione uma imagem válida.")
    if len(dados) > LIMITE_IMAGEM_BYTES:
        return _erro("A imagem excede o limite de 5 MB.", "Escolha uma imagem de até 5 MB.", 413)
    if not validar_assinatura(dados):
        return _erro(
            "O conteúdo não corresponde a uma imagem válida.",
            "O arquivo não parece ser uma imagem JPG, PNG ou WebP válida.",
        )

    nome = f"{uuid4().hex}{extensao}"
    pasta = Path(current_app.config["PRODUCT_IMAGE_FOLDER"])
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / nome).write_bytes(dados)
    return jsonify(foto_caminho=f"assets/produtos/{nome}"), 201
