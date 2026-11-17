"""Funções de apoio usadas pelos controllers."""
from datetime import date, datetime, timezone
import re

from flask import request

from .erros import ErroAplicacao, ErroValidacao

_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def ler_json():
    """Devolve o corpo JSON como dicionário ou lança erro 400/422."""
    if not request.is_json:
        raise ErroAplicacao("Envie o corpo como application/json.")
    payload = request.get_json(silent=True)
    if payload is None:
        raise ErroAplicacao("O JSON enviado está vazio ou malformado.")
    if not isinstance(payload, dict):
        raise ErroValidacao({"_geral": "Envie um objeto JSON."})
    return payload


def data_utc(valor):
    """Converte datas do MySQL (sessão em UTC) para texto ISO terminado em Z."""
    if isinstance(valor, datetime):
        if valor.tzinfo is None:
            valor = valor.replace(tzinfo=timezone.utc)
        return valor.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(valor, date):
        return valor.isoformat()
    return valor


def validar_chave_idempotencia(valor, campo="chave_idempotencia"):
    """A tela gera um UUID por operação; repetir o envio não duplica o registro."""
    if not isinstance(valor, str) or not _UUID.match(valor.strip().lower()):
        raise ErroValidacao({campo: "Chave da operação inválida. Recarregue a página e tente de novo."})
    return valor.strip().lower()


def ler_limite(padrao=50, maximo=200):
    """Lê o parâmetro ?limite= garantindo um inteiro entre 1 e `maximo`."""
    texto = request.args.get("limite", "").strip()
    if not texto:
        return padrao
    if not (texto.isascii() and texto.isdigit()) or not 1 <= int(texto) <= maximo:
        raise ErroValidacao({"limite": f"Informe um número entre 1 e {maximo}."})
    return int(texto)
