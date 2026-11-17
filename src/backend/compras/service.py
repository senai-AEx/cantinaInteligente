"""Camada de serviço: regras do registro e da consulta de compras.

A compra inteira acontece em UMA transação; qualquer falha desfaz tudo:
  1. trava a carteira do usuário;
  2. se a chave de idempotência já gerou uma compra, devolve essa mesma compra;
  3. trava os produtos em ordem crescente de id (a carteira sempre antes dos
     produtos, para duas compras simultâneas não travarem uma à outra);
  4. confere se os produtos existem e estão ativos, depois o estoque e o saldo;
  5. grava a compra e os itens com o preço de venda e o custo do momento,
     baixa o estoque e debita a carteira com a movimentação "Compra #<id>".

Nome e preço nunca vêm da tela: são lidos do banco com o produto travado.
"""
import mysql.connector

from ..carteira import repository as carteira_repository
from ..erros import ErroNegocio, ErroValidacao, NaoEncontrado
from ..http import validar_chave_idempotencia
from ..seguranca import eh_administrador
from . import repository as compra_repository
from .validacao import validar_itens

# Código do MySQL para valor repetido em coluna única (ER_DUP_ENTRY).
ERRO_CHAVE_DUPLICADA = 1062


def _reais(centavos):
    """450 vira "R$ 4,50" (usado só nas mensagens de erro)."""
    inteiros = f"{centavos // 100:,}".replace(",", ".")
    return f"R$ {inteiros},{centavos % 100:02d}"


# ---------- regras puras (não acessam o banco) ----------

def conferir_itens(itens, produtos):
    """Confere os itens contra os produtos já travados e calcula a compra.

    `itens` vem de `validar_itens`; `produtos` é {id_produto: linha da tabela}.
    Devolve (linhas, total_centavos): cada linha leva o preço de venda e o custo
    do momento. Lança ErroNegocio PRODUTO_INDISPONIVEL ou ESTOQUE_INSUFICIENTE.
    """
    indisponiveis = []
    for item in itens:
        produto = produtos.get(item["id_produto"])
        if produto is None or produto["status"] != "ATIVO":
            indisponiveis.append(item["id_produto"])
    if indisponiveis:
        # Os inativos têm nome para mostrar; os inexistentes, não.
        nomes = [
            produtos[id_produto]["nome"]
            for id_produto in indisponiveis
            if id_produto in produtos
        ]
        if len(nomes) == len(indisponiveis):
            mensagem = (
                f"Não está mais à venda: {', '.join(nomes)}. "
                "Retire da compra para continuar."
            )
        else:
            mensagem = (
                "Um ou mais produtos da compra não estão mais à venda. "
                "Atualize a página e monte a compra de novo."
            )
        raise ErroNegocio(
            mensagem,
            codigo="PRODUTO_INDISPONIVEL",
            detalhes={"produtos": [{"id_produto": id_produto} for id_produto in indisponiveis]},
        )

    em_falta = []
    for item in itens:
        produto = produtos[item["id_produto"]]
        if item["quantidade"] > produto["quantidade_estoque"]:
            em_falta.append(
                {
                    "id_produto": produto["id_produto"],
                    "nome": produto["nome"],
                    "disponivel": produto["quantidade_estoque"],
                    "solicitado": item["quantidade"],
                }
            )
    if em_falta:
        resumo = "; ".join(
            f"{falta['nome']} (disponível: {falta['disponivel']}, pedido: {falta['solicitado']})"
            for falta in em_falta
        )
        raise ErroNegocio(
            f"Estoque insuficiente para: {resumo}. Ajuste as quantidades e tente de novo.",
            codigo="ESTOQUE_INSUFICIENTE",
            detalhes={"produtos": em_falta},
        )

    linhas = []
    total_centavos = 0
    for item in itens:
        produto = produtos[item["id_produto"]]
        subtotal = produto["preco_venda_centavos"] * item["quantidade"]
        linhas.append(
            {
                "id_produto": produto["id_produto"],
                "quantidade": item["quantidade"],
                "preco_unitario_centavos": produto["preco_venda_centavos"],
                "custo_unitario_centavos": produto["preco_compra_centavos"],
                "subtotal_centavos": subtotal,
            }
        )
        total_centavos += subtotal
    return linhas, total_centavos


def conferir_saldo(saldo_centavos, total_centavos):
    """Lança ErroNegocio SALDO_INSUFICIENTE se o total passar do saldo."""
    if total_centavos > saldo_centavos:
        raise ErroNegocio(
            f"Saldo insuficiente: a compra custa {_reais(total_centavos)} e seu saldo é "
            f"{_reais(saldo_centavos)}. Adicione créditos para continuar.",
            codigo="SALDO_INSUFICIENTE",
            detalhes={"saldo_centavos": saldo_centavos, "total_centavos": total_centavos},
        )


# ---------- registro da compra ----------

def _conferir_dono_da_chave(compra, id_usuario):
    """A chave só pode repetir a compra do próprio usuário."""
    if compra["id_usuario"] != id_usuario:
        raise ErroValidacao(
            {
                "chave_idempotencia": (
                    "Esta chave já foi usada em outra operação. "
                    "Recarregue a página e tente de novo."
                )
            }
        )


def _resposta(compra, carteira, criada):
    return (
        compra_repository.compra_json(compra),
        carteira_repository.carteira_json(carteira),
        criada,
    )


def _registrar_em_transacao(id_usuario, itens, chave):
    with compra_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # 1. Carteira primeiro: serializa as operações do mesmo usuário.
            carteira = carteira_repository.bloquear_carteira(cursor, id_usuario)
            if carteira is None:
                raise NaoEncontrado("Usuário não encontrado.")

            # 2. Envio repetido (duplo clique, internet instável): mesma compra.
            repetida = compra_repository.carregar_por_chave(cursor, chave)
            if repetida is not None:
                _conferir_dono_da_chave(repetida, id_usuario)
                return _resposta(repetida, carteira, False)

            # 3. Produtos travados em ordem crescente de id.
            produtos = compra_repository.bloquear_produtos(
                cursor, [item["id_produto"] for item in itens]
            )

            # 4. Disponibilidade, estoque e saldo, com os dados travados.
            linhas, total_centavos = conferir_itens(itens, produtos)
            conferir_saldo(carteira["saldo_centavos"], total_centavos)

            # 5. Gravações: compra, itens, estoque e débito na carteira.
            id_compra = compra_repository.inserir_compra(
                cursor, id_usuario, total_centavos, chave
            )
            compra_repository.inserir_itens(cursor, id_compra, linhas)
            compra_repository.baixar_estoque(cursor, linhas)
            carteira_repository.lancar_movimentacao(
                cursor,
                carteira,
                "DEBITO",
                -total_centavos,
                f"Compra #{id_compra}",
                id_autor=id_usuario,
                id_compra=id_compra,
            )
            compra = compra_repository.carregar_compra(cursor, id_compra)
            return _resposta(compra, carteira, True)
        finally:
            cursor.close()


def _buscar_repetida(id_usuario, chave):
    """Compra já gravada com a chave, como (compra, carteira, False), ou None."""
    with compra_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            carteira = carteira_repository.bloquear_carteira(cursor, id_usuario)
            repetida = compra_repository.carregar_por_chave(cursor, chave)
            if carteira is None or repetida is None:
                return None
            _conferir_dono_da_chave(repetida, id_usuario)
            return _resposta(repetida, carteira, False)
        finally:
            cursor.close()


def registrar_compra(usuario, payload):
    """Registra a compra do usuário logado. Devolve (compra, carteira, criada)."""
    itens = validar_itens(payload)
    chave = validar_chave_idempotencia(payload.get("chave_idempotencia"))
    id_usuario = usuario["id_usuario"]
    try:
        return _registrar_em_transacao(id_usuario, itens, chave)
    except mysql.connector.Error as exc:
        if exc.errno != ERRO_CHAVE_DUPLICADA:
            raise
        # Corrida: outra requisição gravou a mesma chave entre a nossa consulta
        # e o INSERT. A transação foi desfeita (nada foi cobrado); consultamos
        # de novo e devolvemos a compra que já existe.
        repetida = _buscar_repetida(id_usuario, chave)
        if repetida is None:
            raise
        return repetida


# ---------- consultas ----------

def listar_compras(usuario, limite):
    compras = compra_repository.listar_compras(usuario["id_usuario"], limite)
    return [compra_repository.compra_json(compra) for compra in compras]


def consultar_compra(usuario, id_compra):
    """Compra de outro usuário responde 404, como se não existisse (exceto para administrador)."""
    compra = compra_repository.consultar_compra(id_compra)
    if compra is None or (
        compra["id_usuario"] != usuario["id_usuario"] and not eh_administrador(usuario)
    ):
        raise NaoEncontrado("Compra não encontrada.")
    return compra_repository.compra_json(compra)
