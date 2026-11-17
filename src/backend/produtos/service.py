"""Camada de serviço: regras de negócio do cadastro de produtos.

- O produto nunca é apagado do banco. "Excluir" muda a situação para INATIVO,
  preservando o histórico (RNF10) e permitindo reativar depois.
- Cada gravação e seu registro de auditoria acontecem na mesma transação (RNF09).
- Produtos da categoria Frutas recebem automaticamente os selos zero lactose e
  zero açúcar; nas demais categorias os selos ficam desmarcados.
"""
import unicodedata

from . import repository as produto_repository
from .validacao import validar_produto

CATEGORIAS_COM_SELOS = {"fruta", "frutas"}


class ErroValidacao(Exception):
    def __init__(self, campos):
        super().__init__("Revise os campos informados.")
        self.campos = campos


class ProdutoNaoEncontrado(Exception):
    pass


def _normalizar(texto):
    sem_acento = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn").casefold()


def aplicar_selos(dados):
    eh_fruta = _normalizar(dados["categoria"]) in CATEGORIAS_COM_SELOS
    dados["zero_lactose"] = eh_fruta
    dados["zero_acucar"] = eh_fruta
    return dados


def _preparar(payload):
    dados, erros = validar_produto(payload)
    if erros:
        raise ErroValidacao(erros)
    return aplicar_selos(dados)


def listar_produtos(termo, status):
    return produto_repository.listar_produtos(termo, status)


def consultar_produto(id_produto):
    produto = produto_repository.consultar_produto(id_produto)
    if produto is None:
        raise ProdutoNaoEncontrado()
    return produto


def incluir_produto(payload, autor, origem):
    dados = _preparar(payload)
    with produto_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            id_produto = produto_repository.inserir(cursor, dados)
            produto = produto_repository.carregar(cursor, id_produto)
            produto_repository.registrar_auditoria(
                cursor, id_produto, "INCLUIR", autor, origem, None, produto
            )
        finally:
            cursor.close()
    return produto


def alterar_produto(id_produto, payload, autor, origem):
    dados = _preparar(payload)
    with produto_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            antes = produto_repository.carregar(cursor, id_produto, bloquear=True)
            if antes is None:
                raise ProdutoNaoEncontrado()
            produto_repository.atualizar(cursor, id_produto, dados)
            depois = produto_repository.carregar(cursor, id_produto)
            produto_repository.registrar_auditoria(
                cursor, id_produto, "ALTERAR", autor, origem, antes, depois
            )
        finally:
            cursor.close()
    return depois


def _mudar_status(id_produto, status_novo, acao, autor, origem):
    with produto_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            antes = produto_repository.carregar(cursor, id_produto, bloquear=True)
            if antes is None:
                raise ProdutoNaoEncontrado()
            if antes["status"] == status_novo:
                return antes
            produto_repository.atualizar_status(cursor, id_produto, status_novo)
            depois = produto_repository.carregar(cursor, id_produto)
            produto_repository.registrar_auditoria(
                cursor, id_produto, acao, autor, origem, antes, depois
            )
        finally:
            cursor.close()
    return depois


def inativar_produto(id_produto, autor, origem):
    """Exclusão lógica: o produto continua no banco com status INATIVO."""
    return _mudar_status(id_produto, "INATIVO", "INATIVAR", autor, origem)


def reativar_produto(id_produto, autor, origem):
    return _mudar_status(id_produto, "ATIVO", "REATIVAR", autor, origem)


def listar_auditoria(id_produto):
    produto_existe, registros = produto_repository.listar_auditoria(id_produto)
    if not produto_existe and not registros:
        raise ProdutoNaoEncontrado()
    return registros
