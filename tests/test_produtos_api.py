"""Testes da API de produtos sem banco real (o repositório é substituído por um falso)."""
from contextlib import contextmanager
import copy
import unittest
from unittest.mock import patch

from src.backend.app import app
from src.backend.produtos import service
from src.backend.produtos.validacao import validar_produto
from tests.apoio import ADMINISTRADOR, CLIENTE, simular_login

PRODUTO_VALIDO = {
    "nome": "Suco de uva 200 ml",
    "descricao": "Produto de demonstração",
    "categoria": "Bebidas",
    "preco_compra_centavos": 300,
    "preco_venda_centavos": 450,
    "quantidade_estoque": 10,
    "foto_caminho": None,
}


class RepositorioFalso:
    """Imita o módulo repository guardando os produtos em memória."""

    def __init__(self):
        self.produtos = {}
        self.auditorias = []
        self.proximo_id = 1

    @contextmanager
    def transacao(self):
        yield self

    def cursor(self, **_kwargs):
        return self

    def close(self):
        pass

    def carregar(self, _cursor, id_produto, bloquear=False):
        produto = self.produtos.get(id_produto)
        return copy.deepcopy(produto) if produto else None

    def inserir(self, _cursor, dados):
        id_produto = self.proximo_id
        self.proximo_id += 1
        self.produtos[id_produto] = {"id_produto": id_produto, "status": "ATIVO", **dados}
        return id_produto

    def atualizar(self, _cursor, id_produto, dados):
        self.produtos[id_produto].update(dados)

    def atualizar_status(self, _cursor, id_produto, status):
        self.produtos[id_produto]["status"] = status

    def registrar_auditoria(self, _cursor, id_produto, acao, autor, origem, antes, depois):
        self.auditorias.append({"id_produto": id_produto, "acao": acao, "antes": antes, "depois": depois})

    def listar_produtos(self, termo, status):
        return [p for p in self.produtos.values() if status == "TODOS" or p["status"] == status]

    def consultar_produto(self, id_produto):
        return self.carregar(None, id_produto)

    def listar_auditoria(self, id_produto):
        registros = [a for a in self.auditorias if a["id_produto"] == id_produto]
        return id_produto in self.produtos, list(reversed(registros))


class ProdutosApiTests(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioFalso()
        substituto = patch.object(service, "produto_repository", self.repo)
        substituto.start()
        self.addCleanup(substituto.stop)
        self.cliente = app.test_client()
        simular_login(self, self.cliente, ADMINISTRADOR)

    def cadastrar(self, **alteracoes):
        return self.cliente.post("/api/produtos", json={**PRODUTO_VALIDO, **alteracoes})

    def test_cadastro_gera_id_automatico_sem_codigo_manual(self):
        resposta = self.cadastrar()
        self.assertEqual(resposta.status_code, 201)
        produto = resposta.json["produto"]
        self.assertEqual(produto["id_produto"], 1)
        self.assertNotIn("codigo_produto", produto)
        self.assertEqual(produto["preco_compra_centavos"], 300)
        self.assertEqual(produto["preco_venda_centavos"], 450)
        self.assertEqual(self.repo.auditorias[0]["acao"], "INCLUIR")

    def test_cadastro_recusa_campos_removidos_do_modelo(self):
        for campo, valor in (
            ("codigo_produto", "ABC123"),
            ("estoque_minimo", 1),
            ("estoque_maximo", 10),
            ("validade", "2027-01-01"),
            ("zero_lactose", True),
        ):
            with self.subTest(campo=campo):
                resposta = self.cadastrar(**{campo: valor})
                self.assertEqual(resposta.status_code, 422)
                self.assertIn(campo, resposta.json["campos"])
        self.assertEqual(self.repo.produtos, {})

    def test_frutas_recebem_selos_automaticamente(self):
        fruta = self.cadastrar(categoria="Frutas").json["produto"]
        bebida = self.cadastrar(categoria="Bebidas").json["produto"]
        self.assertTrue(fruta["zero_lactose"] and fruta["zero_acucar"])
        self.assertFalse(bebida["zero_lactose"] or bebida["zero_acucar"])

    def test_excluir_apenas_inativa_e_mantem_no_banco(self):
        self.cadastrar()
        resposta = self.cliente.patch("/api/produtos/1/inativar")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["produto"]["status"], "INATIVO")
        self.assertIn(1, self.repo.produtos)
        self.assertEqual(self.repo.auditorias[-1]["acao"], "INATIVAR")

        reativado = self.cliente.patch("/api/produtos/1/reativar")
        self.assertEqual(reativado.json["produto"]["status"], "ATIVO")

    def test_nao_existe_exclusao_definitiva(self):
        self.cadastrar()
        resposta = self.cliente.delete("/api/produtos/1")
        self.assertEqual(resposta.status_code, 405)
        self.assertIn(1, self.repo.produtos)

    def test_alteracao_registra_antes_e_depois(self):
        self.cadastrar()
        resposta = self.cliente.put(
            "/api/produtos/1", json={**PRODUTO_VALIDO, "preco_venda_centavos": 500}
        )
        self.assertEqual(resposta.status_code, 200)
        auditoria = self.repo.auditorias[-1]
        self.assertEqual(auditoria["acao"], "ALTERAR")
        self.assertEqual(auditoria["antes"]["preco_venda_centavos"], 450)
        self.assertEqual(auditoria["depois"]["preco_venda_centavos"], 500)

    def test_produto_inexistente_responde_404(self):
        self.assertEqual(self.cliente.get("/api/produtos/99").status_code, 404)
        self.assertEqual(
            self.cliente.put("/api/produtos/99", json=PRODUTO_VALIDO).status_code, 404
        )
        self.assertEqual(self.cliente.patch("/api/produtos/99/inativar").status_code, 404)


class PermissaoProdutosTests(unittest.TestCase):
    """Só o administrador grava; o catálogo é público."""

    def setUp(self):
        self.repo = RepositorioFalso()
        substituto = patch.object(service, "produto_repository", self.repo)
        substituto.start()
        self.addCleanup(substituto.stop)
        self.cliente = app.test_client()

    def test_catalogo_e_publico(self):
        self.assertEqual(self.cliente.get("/api/produtos").status_code, 200)

    def test_sem_login_nao_cadastra(self):
        resposta = self.cliente.post("/api/produtos", json=PRODUTO_VALIDO)
        self.assertEqual(resposta.status_code, 401)
        self.assertEqual(self.repo.produtos, {})

    def test_cliente_nao_cadastra_nem_inativa(self):
        simular_login(self, self.cliente, CLIENTE)
        self.assertEqual(self.cliente.post("/api/produtos", json=PRODUTO_VALIDO).status_code, 403)
        self.assertEqual(self.cliente.patch("/api/produtos/1/inativar").status_code, 403)
        self.assertEqual(self.repo.produtos, {})


class ValidacaoProdutoTests(unittest.TestCase):
    def test_produto_valido(self):
        dados, erros = validar_produto(PRODUTO_VALIDO)
        self.assertEqual(erros, {})
        self.assertEqual(dados["nome"], "Suco de uva 200 ml")

    def test_obrigatorios(self):
        _, erros = validar_produto({})
        self.assertEqual(
            set(erros),
            {"nome", "categoria", "preco_compra_centavos", "preco_venda_centavos"},
        )

    def test_precos_precisam_ser_positivos(self):
        _, erros = validar_produto(
            {**PRODUTO_VALIDO, "preco_compra_centavos": 0, "preco_venda_centavos": -1}
        )
        self.assertIn("preco_compra_centavos", erros)
        self.assertIn("preco_venda_centavos", erros)

    def test_venda_menor_que_compra(self):
        _, erros = validar_produto(
            {**PRODUTO_VALIDO, "preco_compra_centavos": 500, "preco_venda_centavos": 400}
        )
        self.assertIn("preco_venda_centavos", erros)

    def test_quantidade_negativa_ou_fracionada(self):
        for valor in (-1, 1.5, "3"):
            with self.subTest(valor=valor):
                _, erros = validar_produto({**PRODUTO_VALIDO, "quantidade_estoque": valor})
                self.assertIn("quantidade_estoque", erros)

    def test_nome_so_com_espacos(self):
        _, erros = validar_produto({**PRODUTO_VALIDO, "nome": "   "})
        self.assertIn("nome", erros)


if __name__ == "__main__":
    unittest.main()
