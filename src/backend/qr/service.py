"""Camada de serviço do QR Code: monta os endereços e desenha a imagem.

O QR Code é só um endereço do próprio sistema escrito em forma de imagem:
- o da cantina abre o catálogo;
- o de cada produto abre o catálogo já com aquele produto na sacola.
A imagem é gerada em SVG pela biblioteca `segno` (gratuita, sem dependências).
"""
import io
import os
from urllib.parse import urlsplit

import segno

CAMINHO_CATALOGO = "/html/catalogo_produtos.html"
HOSTS_LOCAIS = {"127.0.0.1", "localhost", "::1"}


def url_base(endereco_da_requisicao):
    """Endereço que vai dentro do QR Code.

    Usa URL_PUBLICA do .env (ex.: http://192.168.0.10:5000) quando ela é um
    endereço http/https válido; senão, o endereço pelo qual o administrador
    está acessando o sistema.
    """
    publica = os.getenv("URL_PUBLICA", "").strip().rstrip("/")
    if publica:
        partes = urlsplit(publica)
        if partes.scheme in ("http", "https") and partes.hostname:
            return publica
    return endereco_da_requisicao.rstrip("/")


def somente_local(base):
    """True quando o endereço só funciona neste computador (não abre no celular)."""
    return (urlsplit(base).hostname or "") in HOSTS_LOCAIS


def url_cantina(base):
    return base + CAMINHO_CATALOGO


def url_produto(base, id_produto):
    return f"{base}{CAMINHO_CATALOGO}?adicionar={id_produto}"


def informacoes(base):
    return {
        "url_base": base,
        "url_cantina": url_cantina(base),
        "url_produto": url_produto(base, "{id}"),
        "somente_local": somente_local(base),
    }


def desenhar_svg(conteudo):
    """Devolve os bytes de um SVG com o QR Code de `conteudo`.

    Nível de correção M: continua legível com a etiqueta um pouco gasta.
    A borda de 4 módulos é a margem branca exigida para os leitores.
    """
    qr = segno.make(conteudo, error="m", micro=False)
    saida = io.BytesIO()
    qr.save(saida, kind="svg", scale=8, border=4, xmldecl=False, omitsize=True)
    return saida.getvalue()
