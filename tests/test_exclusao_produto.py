"""Testes sem banco real para exclusão definitiva e preservação da auditoria."""
from contextlib import contextmanager
from datetime import date, datetime
import json
import unittest
from unittest.mock import patch

from src.backend.app import app


class BancoFalso:
    def __init__(self):
        self.excluido = False
        self.auditorias = []
        self.ordem_escritas = []
        self.produto = {
            "id_produto": 42,
            "codigo_produto": "CI-TESTE-042",
            "nome": "Produto descartável de teste",
            "descricao": "",
            "categoria": "Bebidas",
            "preco_centavos": 450,
            "quantidade_estoque": 4,
            "estoque_minimo": 1,
            "estoque_maximo": 10,
            "validade": date(2027, 1, 1),
            "foto_caminho": None,
            "zero_lactose": False,
            "zero_acucar": False,
            "status": "ATIVO",
            "criado_em": datetime(2026, 1, 1),
            "atualizado_em": datetime(2026, 1, 1),
        }

    def cursor(self, **_kwargs):
        return CursorFalso(self)

    def is_connected(self):
        return True

    def close(self):
        pass


class CursorFalso:
    def __init__(self, banco):
        self.banco = banco
        self.resultado = None
        self.resultados = []

    def execute(self, sql, parametros=()):
        if sql.startswith("SELECT") and "FROM produtos WHERE id_produto" in sql:
            if sql.startswith("SELECT id_produto FROM produtos"):
                self.resultado = None if self.banco.excluido else {"id_produto": 42}
            else:
                self.resultado = None if self.banco.excluido else self.banco.produto.copy()
        elif sql.startswith("INSERT INTO auditoria_produtos"):
            self.banco.ordem_escritas.append("auditoria")
            self.banco.auditorias.append(
                {
                    "id_auditoria": len(self.banco.auditorias) + 1,
                    "id_produto": parametros[0],
                    "acao": parametros[1],
                    "autor": parametros[2],
                    "origem": parametros[3],
                    "antes_json": parametros[4],
                    "depois_json": parametros[5],
                    "registrado_em": datetime(2026, 10, 15),
                }
            )
        elif sql.startswith("DELETE FROM produtos"):
            self.banco.ordem_escritas.append("produto")
            self.banco.excluido = True
        elif "FROM auditoria_produtos" in sql:
            self.resultados = list(reversed(self.banco.auditorias))

    def fetchone(self):
        return self.resultado

    def fetchall(self):
        return self.resultados

    def close(self):
        pass


class ExclusaoProdutoTests(unittest.TestCase):
    def setUp(self):
        self.banco = BancoFalso()
        self.cliente = app.test_client()

        @contextmanager
        def transacao_falsa():
            yield self.banco

        self.patch_transacao = patch("src.backend.produtos.transacao", transacao_falsa)
        self.patch_transacao.start()
        self.addCleanup(self.patch_transacao.stop)
        self.patch_conectar = patch("src.backend.produtos.conectar", lambda: self.banco)
        self.patch_conectar.start()
        self.addCleanup(self.patch_conectar.stop)

    def test_exclusao_grava_auditoria_antes_de_remover_e_preserva_historico(self):
        resposta = self.cliente.delete("/api/produtos/42")

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(self.banco.excluido)
        self.assertEqual(self.banco.ordem_escritas, ["auditoria", "produto"])
        self.assertEqual(self.banco.auditorias[0]["acao"], "EXCLUIR")
        self.assertEqual(
            json.loads(self.banco.auditorias[0]["depois_json"]),
            {"id_produto": 42, "excluido": True},
        )

        consulta = self.cliente.get("/api/produtos/42/auditoria")
        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(consulta.json["auditorias"][0]["acao"], "EXCLUIR")
        self.assertEqual(consulta.json["auditorias"][0]["antes_json"]["nome"], "Produto descartável de teste")


if __name__ == "__main__":
    unittest.main()
