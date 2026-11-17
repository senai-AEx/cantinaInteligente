"""Validação dos itens enviados em uma compra (lógica pura, sem banco).

A tela envia {"itens": [{"id_produto": 3, "quantidade": 2}, ...]}. Nome, preço e
estoque nunca vêm da tela: são lidos do banco no momento da compra.
"""
from ..erros import ErroValidacao

MAXIMO_ITENS = 50
QUANTIDADE_MAXIMA = 99
MAX_INT = 2_147_483_647  # maior id que cabe na coluna INT do MySQL


def _inteiro(valor):
    """True só para inteiros de verdade (True/False e 2.0 não contam)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def _erro(mensagem):
    return ErroValidacao({"itens": mensagem})


def validar_itens(payload):
    """Devolve [{"id_produto", "quantidade"}] na ordem enviada ou lança ErroValidacao."""
    itens = payload.get("itens") if isinstance(payload, dict) else None
    if not isinstance(itens, list) or not itens:
        raise _erro("Adicione pelo menos um produto à compra.")
    if len(itens) > MAXIMO_ITENS:
        raise _erro(f"Uma compra pode ter no máximo {MAXIMO_ITENS} produtos diferentes.")

    validados = []
    vistos = set()
    for posicao, item in enumerate(itens, start=1):
        if not isinstance(item, dict):
            raise _erro(f"Item {posicao}: formato inválido.")

        id_produto = item.get("id_produto")
        if not _inteiro(id_produto) or not 1 <= id_produto <= MAX_INT:
            raise _erro(f"Item {posicao}: produto inválido.")
        if id_produto in vistos:
            raise _erro(
                f"Item {posicao}: o produto {id_produto} está repetido. "
                "Junte as quantidades em um único item."
            )

        quantidade = item.get("quantidade")
        if not _inteiro(quantidade) or not 1 <= quantidade <= QUANTIDADE_MAXIMA:
            raise _erro(
                f"Item {posicao}: informe uma quantidade inteira de 1 a {QUANTIDADE_MAXIMA}."
            )

        vistos.add(id_produto)
        validados.append({"id_produto": id_produto, "quantidade": quantidade})
    return validados
