"""Camada de serviço: regras da carteira de créditos.

- Todo lançamento trava a carteira, altera o saldo e grava a movimentação na
  mesma transação: o saldo sempre bate com o extrato e nunca fica negativo.
- A tela envia uma chave de idempotência por operação. Repetir o envio (duplo
  clique, internet instável) devolve o lançamento já gravado, sem lançar de novo.
- O crédito é declarado pelo próprio usuário (depósito na caixa da cantina);
  o ajuste é lançado pela administração, por meio de `ajustar_saldo`.
"""
import mysql.connector

from ..erros import ErroValidacao, NaoEncontrado
from ..http import validar_chave_idempotencia
from . import repository as carteira_repository

VALOR_MINIMO_CREDITO = 100  # R$ 1,00
VALOR_MAXIMO_CREDITO = 50_000  # R$ 500,00
DESCRICAO_CREDITO = "Depósito declarado na caixa"
PREFIXO_AJUSTE = "Ajuste da administração: "
TAMANHO_DESCRICAO = 200

# Código do MySQL para valor repetido em coluna única (ER_DUP_ENTRY).
ERRO_CHAVE_DUPLICADA = 1062


def _inteiro(valor):
    """True só para inteiros de verdade (True/False e 10.0 não contam)."""
    return isinstance(valor, int) and not isinstance(valor, bool)


def validar_valor_credito(valor):
    """Crédito em centavos inteiros, de R$ 1,00 a R$ 500,00. Não acessa o banco."""
    if valor is None:
        raise ErroValidacao({"valor_centavos": "Informe o valor do crédito."})
    if not _inteiro(valor):
        raise ErroValidacao({"valor_centavos": "Informe um valor válido, em centavos inteiros."})
    if not VALOR_MINIMO_CREDITO <= valor <= VALOR_MAXIMO_CREDITO:
        raise ErroValidacao({"valor_centavos": "O valor deve ficar entre R$ 1,00 e R$ 500,00."})
    return valor


def consultar_carteira(usuario):
    id_usuario = usuario["id_usuario"]
    carteira = carteira_repository.buscar_carteira(id_usuario)
    if carteira is None:
        # Usuário sem carteira (criado direto no banco): abre uma com saldo zero.
        with carteira_repository.transacao() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                carteira = carteira_repository.bloquear_carteira(cursor, id_usuario)
            finally:
                cursor.close()
    if carteira is None:
        raise NaoEncontrado("Usuário não encontrado.")
    return carteira_repository.carteira_json(carteira)


def listar_movimentacoes(usuario, limite):
    return carteira_repository.listar_movimentacoes(usuario["id_usuario"], limite)


def _conferir_repeticao(existente, carteira, tipo):
    """A chave só pode repetir a MESMA operação: mesma carteira e mesmo tipo."""
    if existente["id_carteira"] != carteira["id_carteira"] or existente["tipo"] != tipo:
        raise ErroValidacao(
            {
                "chave_idempotencia": (
                    "Esta chave já foi usada em outra operação. "
                    "Recarregue a página e tente de novo."
                )
            }
        )


def _lancar_em_transacao(id_usuario, tipo, valor_centavos, descricao, id_autor, chave):
    with carteira_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            carteira = carteira_repository.bloquear_carteira(cursor, id_usuario)
            if carteira is None:
                raise NaoEncontrado("Usuário não encontrado.")

            # Com a carteira travada, duas requisições com a mesma chave passam
            # por aqui uma de cada vez: a segunda já encontra o lançamento da primeira.
            existente = carteira_repository.carregar_movimentacao_por_chave(cursor, chave)
            if existente is not None:
                _conferir_repeticao(existente, carteira, tipo)
                return (
                    carteira_repository.movimentacao_json(existente),
                    carteira_repository.carteira_json(carteira),
                    False,
                )

            movimentacao = carteira_repository.lancar_movimentacao(
                cursor,
                carteira,
                tipo,
                valor_centavos,
                descricao,
                id_autor,
                chave_idempotencia=chave,
            )
            return movimentacao, carteira_repository.carteira_json(carteira), True
        finally:
            cursor.close()


def _lancar(id_usuario, tipo, valor_centavos, descricao, id_autor, chave):
    """Lança com idempotência. Devolve (movimentacao, carteira, criado)."""
    argumentos = (id_usuario, tipo, valor_centavos, descricao, id_autor, chave)
    try:
        return _lancar_em_transacao(*argumentos)
    except mysql.connector.Error as exc:
        if exc.errno != ERRO_CHAVE_DUPLICADA:
            raise
        # A chave foi gravada por outra requisição entre a nossa consulta e o
        # INSERT. A transação foi desfeita; na segunda tentativa a consulta já
        # encontra o lançamento e responde como repetição (ou recusa a chave).
        return _lancar_em_transacao(*argumentos)


def adicionar_credito(usuario, payload):
    """Crédito declarado pelo usuário. Devolve (movimentacao, carteira, criado)."""
    valor = validar_valor_credito(payload.get("valor_centavos"))
    chave = validar_chave_idempotencia(payload.get("chave_idempotencia"))
    id_usuario = usuario["id_usuario"]
    return _lancar(id_usuario, "CREDITO", valor, DESCRICAO_CREDITO, id_usuario, chave)


def ajustar_saldo(id_usuario, valor_centavos, motivo, id_autor, chave_idempotencia):
    """Ajuste feito pela administração. Devolve (movimentacao, carteira, criado).

    O módulo admin valida os limites do valor e o motivo; aqui fica só o mínimo
    para o lançamento ser possível (inteiro com sinal, diferente de zero).
    Ajuste negativo maior que o saldo lança ErroNegocio SALDO_INSUFICIENTE.
    """
    if not _inteiro(valor_centavos) or valor_centavos == 0:
        raise ErroValidacao({"valor_centavos": "Informe um valor inteiro diferente de zero."})
    chave = validar_chave_idempotencia(chave_idempotencia)
    descricao = f"{PREFIXO_AJUSTE}{str(motivo).strip()}"[:TAMANHO_DESCRICAO]
    return _lancar(id_usuario, "AJUSTE", valor_centavos, descricao, id_autor, chave)
