"""Testes de lógica pura da carteira e das compras: nenhum acessa o banco.

Cobrem a validação dos itens da compra, os limites do crédito, as conferências
de produto, estoque e saldo feitas antes de gravar e o formato dos objetos JSON.
"""
from datetime import datetime
import unittest
from unittest.mock import patch

from src.backend.carteira import repository as carteira_repository
from src.backend.carteira import service as carteira_service
from src.backend.compras import repository as compra_repository
from src.backend.compras import service as compra_service
from src.backend.compras.validacao import MAXIMO_ITENS, QUANTIDADE_MAXIMA, validar_itens
from src.backend.erros import ErroNegocio, ErroValidacao

CHAVE = "3f2b8c1e-9a4d-4e6f-8b7a-1c2d3e4f5a6b"
USUARIO = {"id_usuario": 7, "perfil": "CLIENTE"}

PRODUTOS = {
    3: {
        "id_produto": 3,
        "nome": "Suco de uva 200 ml",
        "preco_compra_centavos": 300,
        "preco_venda_centavos": 450,
        "quantidade_estoque": 10,
        "status": "ATIVO",
    },
    4: {
        "id_produto": 4,
        "nome": "Coxinha",
        "preco_compra_centavos": 250,
        "preco_venda_centavos": 600,
        "quantidade_estoque": 2,
        "status": "ATIVO",
    },
    8: {
        "id_produto": 8,
        "nome": "Bolo de fubá",
        "preco_compra_centavos": 200,
        "preco_venda_centavos": 400,
        "quantidade_estoque": 5,
        "status": "INATIVO",
    },
}


def item(id_produto, quantidade):
    return {"id_produto": id_produto, "quantidade": quantidade}


class ValidacaoItensTests(unittest.TestCase):
    def assertErroItens(self, payload):
        with self.assertRaises(ErroValidacao) as contexto:
            validar_itens(payload)
        self.assertEqual(set(contexto.exception.campos), {"itens"})
        self.assertEqual(contexto.exception.status, 422)

    def test_itens_validos_mantem_a_ordem_enviada(self):
        itens = validar_itens({"itens": [item(5, 2), item(3, 1)]})
        self.assertEqual(itens, [item(5, 2), item(3, 1)])

    def test_campos_extras_do_item_sao_descartados(self):
        # Preço enviado pela tela nunca é usado: vale o que está no banco.
        enviado = {"id_produto": 1, "quantidade": 1, "preco_unitario_centavos": 1}
        self.assertEqual(validar_itens({"itens": [enviado]}), [item(1, 1)])

    def test_lista_ausente_vazia_ou_de_outro_tipo(self):
        for payload in (
            {},
            {"itens": None},
            {"itens": []},
            {"itens": "1"},
            {"itens": {"id_produto": 1, "quantidade": 1}},
            None,
            [],
        ):
            with self.subTest(payload=payload):
                self.assertErroItens(payload)

    def test_quantidade_de_itens_no_limite(self):
        no_limite = [item(numero, 1) for numero in range(1, MAXIMO_ITENS + 1)]
        self.assertEqual(len(validar_itens({"itens": no_limite})), MAXIMO_ITENS)
        self.assertErroItens({"itens": no_limite + [item(MAXIMO_ITENS + 1, 1)]})

    def test_item_que_nao_e_objeto(self):
        for invalido in (3, "1", None, [1, 2]):
            with self.subTest(item=invalido):
                self.assertErroItens({"itens": [invalido]})

    def test_id_produto_invalido(self):
        for id_produto in (0, -3, "3", 3.0, 3.5, True, None, 2**31):
            with self.subTest(id_produto=id_produto):
                self.assertErroItens({"itens": [item(id_produto, 1)]})

    def test_item_sem_id_ou_sem_quantidade(self):
        self.assertErroItens({"itens": [{"quantidade": 1}]})
        self.assertErroItens({"itens": [{"id_produto": 1}]})

    def test_produto_repetido(self):
        self.assertErroItens({"itens": [item(3, 1), item(4, 1), item(3, 2)]})

    def test_limites_da_quantidade_sao_aceitos(self):
        for quantidade in (1, QUANTIDADE_MAXIMA):
            with self.subTest(quantidade=quantidade):
                itens = validar_itens({"itens": [item(1, quantidade)]})
                self.assertEqual(itens[0]["quantidade"], quantidade)

    def test_quantidade_invalida(self):
        for quantidade in (0, -1, QUANTIDADE_MAXIMA + 1, "2", 2.0, 2.5, True, None):
            with self.subTest(quantidade=quantidade):
                self.assertErroItens({"itens": [item(1, quantidade)]})


class LimitesCreditoTests(unittest.TestCase):
    def assertErroValor(self, valor):
        with self.assertRaises(ErroValidacao) as contexto:
            carteira_service.validar_valor_credito(valor)
        self.assertEqual(set(contexto.exception.campos), {"valor_centavos"})

    def test_limites_declarados_no_contrato(self):
        self.assertEqual(carteira_service.VALOR_MINIMO_CREDITO, 100)
        self.assertEqual(carteira_service.VALOR_MAXIMO_CREDITO, 50000)

    def test_valores_dentro_dos_limites(self):
        for valor in (100, 101, 2500, 49999, 50000):
            with self.subTest(valor=valor):
                self.assertEqual(carteira_service.validar_valor_credito(valor), valor)

    def test_valores_fora_dos_limites(self):
        for valor in (99, 50001, 1, 0, -100):
            with self.subTest(valor=valor):
                self.assertErroValor(valor)

    def test_valor_precisa_ser_inteiro(self):
        for valor in ("1000", 1000.0, 10.5, True, None, [1000]):
            with self.subTest(valor=valor):
                self.assertErroValor(valor)


class ValidacaoAntesDoBancoTests(unittest.TestCase):
    """Dados inválidos são recusados antes de qualquer transação ser aberta."""

    def setUp(self):
        for repositorio in (carteira_repository, compra_repository):
            substituto = patch.object(
                repositorio,
                "transacao",
                side_effect=AssertionError("Não deveria acessar o banco."),
            )
            substituto.start()
            self.addCleanup(substituto.stop)

    def assertCampoInvalido(self, campo, funcao, *argumentos):
        with self.assertRaises(ErroValidacao) as contexto:
            funcao(*argumentos)
        self.assertIn(campo, contexto.exception.campos)

    def test_credito_com_valor_invalido(self):
        payload = {"valor_centavos": 99, "chave_idempotencia": CHAVE}
        self.assertCampoInvalido(
            "valor_centavos", carteira_service.adicionar_credito, USUARIO, payload
        )

    def test_credito_sem_chave_ou_com_chave_invalida(self):
        for payload in (
            {"valor_centavos": 1000},
            {"valor_centavos": 1000, "chave_idempotencia": "abc"},
            {"valor_centavos": 1000, "chave_idempotencia": 123},
        ):
            with self.subTest(payload=payload):
                self.assertCampoInvalido(
                    "chave_idempotencia", carteira_service.adicionar_credito, USUARIO, payload
                )

    def test_ajuste_precisa_de_inteiro_diferente_de_zero(self):
        for valor in (0, True, "100", 1.5, None):
            with self.subTest(valor=valor):
                self.assertCampoInvalido(
                    "valor_centavos",
                    carteira_service.ajustar_saldo,
                    7,
                    valor,
                    "Troco devolvido",
                    1,
                    CHAVE,
                )

    def test_compra_com_itens_invalidos(self):
        payload = {"itens": [], "chave_idempotencia": CHAVE}
        self.assertCampoInvalido("itens", compra_service.registrar_compra, USUARIO, payload)

    def test_compra_com_chave_invalida(self):
        payload = {"itens": [item(3, 1)], "chave_idempotencia": "abc"}
        self.assertCampoInvalido(
            "chave_idempotencia", compra_service.registrar_compra, USUARIO, payload
        )


class RegrasDaCompraTests(unittest.TestCase):
    def test_calcula_linhas_e_total_com_preco_e_custo_do_produto(self):
        linhas, total = compra_service.conferir_itens([item(3, 2), item(4, 1)], PRODUTOS)
        self.assertEqual(total, 1500)
        self.assertEqual(
            linhas,
            [
                {
                    "id_produto": 3,
                    "quantidade": 2,
                    "preco_unitario_centavos": 450,
                    "custo_unitario_centavos": 300,
                    "subtotal_centavos": 900,
                },
                {
                    "id_produto": 4,
                    "quantidade": 1,
                    "preco_unitario_centavos": 600,
                    "custo_unitario_centavos": 250,
                    "subtotal_centavos": 600,
                },
            ],
        )

    def test_comprar_todo_o_estoque_e_permitido(self):
        _, total = compra_service.conferir_itens([item(4, 2)], PRODUTOS)
        self.assertEqual(total, 1200)

    def test_produto_inexistente_ou_inativo(self):
        with self.assertRaises(ErroNegocio) as contexto:
            compra_service.conferir_itens([item(3, 1), item(8, 1), item(99, 1)], PRODUTOS)
        erro = contexto.exception
        self.assertEqual(erro.status, 409)
        self.assertEqual(erro.codigo, "PRODUTO_INDISPONIVEL")
        self.assertEqual(erro.detalhes, {"produtos": [{"id_produto": 8}, {"id_produto": 99}]})

    def test_estoque_insuficiente_lista_todos_os_produtos_em_falta(self):
        with self.assertRaises(ErroNegocio) as contexto:
            compra_service.conferir_itens([item(3, 11), item(4, 3)], PRODUTOS)
        erro = contexto.exception
        self.assertEqual(erro.codigo, "ESTOQUE_INSUFICIENTE")
        self.assertEqual(
            erro.detalhes,
            {
                "produtos": [
                    {
                        "id_produto": 3,
                        "nome": "Suco de uva 200 ml",
                        "disponivel": 10,
                        "solicitado": 11,
                    },
                    {"id_produto": 4, "nome": "Coxinha", "disponivel": 2, "solicitado": 3},
                ]
            },
        )

    def test_produto_indisponivel_e_conferido_antes_do_estoque(self):
        with self.assertRaises(ErroNegocio) as contexto:
            compra_service.conferir_itens([item(4, 50), item(8, 1)], PRODUTOS)
        self.assertEqual(contexto.exception.codigo, "PRODUTO_INDISPONIVEL")

    def test_saldo_insuficiente(self):
        with self.assertRaises(ErroNegocio) as contexto:
            compra_service.conferir_saldo(300, 450)
        erro = contexto.exception
        self.assertEqual(erro.codigo, "SALDO_INSUFICIENTE")
        self.assertEqual(erro.detalhes, {"saldo_centavos": 300, "total_centavos": 450})
        self.assertIn("R$ 4,50", erro.mensagem)
        self.assertIn("R$ 3,00", erro.mensagem)

    def test_saldo_exato_paga_a_compra(self):
        self.assertIsNone(compra_service.conferir_saldo(450, 450))


class LancamentoTests(unittest.TestCase):
    def test_debito_maior_que_o_saldo_e_recusado_antes_de_gravar(self):
        carteira = {"id_carteira": 1, "id_usuario": 7, "saldo_centavos": 300, "atualizado_em": None}
        with self.assertRaises(ErroNegocio) as contexto:
            # cursor=None: se a função tentasse gravar algo, o teste falharia.
            carteira_repository.lancar_movimentacao(
                None, carteira, "DEBITO", -450, "Compra #1", id_autor=7, id_compra=1
            )
        self.assertEqual(contexto.exception.codigo, "SALDO_INSUFICIENTE")
        self.assertEqual(
            contexto.exception.detalhes, {"saldo_centavos": 300, "total_centavos": 450}
        )
        self.assertEqual(carteira["saldo_centavos"], 300)


class FormatoJsonTests(unittest.TestCase):
    """Os objetos enviados à tela seguem o contrato e não expõem dados internos."""

    def test_carteira(self):
        linha = {
            "id_carteira": 7,
            "id_usuario": 7,
            "saldo_centavos": 1550,
            "atualizado_em": datetime(2026, 11, 17, 22, 48, 21, 454404),
        }
        self.assertEqual(
            carteira_repository.carteira_json(linha),
            {
                "id_carteira": 7,
                "saldo_centavos": 1550,
                "atualizado_em": "2026-11-17T22:48:21.454404Z",
            },
        )

    def test_movimentacao(self):
        linha = {
            "id_movimentacao": 31,
            "id_carteira": 7,
            "tipo": "DEBITO",
            "valor_centavos": -450,
            "saldo_apos_centavos": 1550,
            "descricao": "Compra #12",
            "id_compra": 12,
            "data_hora": datetime(2026, 11, 17, 22, 50, 3, 120000),
        }
        self.assertEqual(
            carteira_repository.movimentacao_json(linha),
            {
                "id_movimentacao": 31,
                "tipo": "DEBITO",
                "valor_centavos": -450,
                "saldo_apos_centavos": 1550,
                "descricao": "Compra #12",
                "id_compra": 12,
                "data_hora": "2026-11-17T22:50:03.120000Z",
            },
        )

    def test_compra_nao_expoe_o_dono(self):
        itens = [
            {
                "id_produto": 3,
                "nome": "Suco de uva 200 ml",
                "quantidade": 1,
                "preco_unitario_centavos": 450,
                "subtotal_centavos": 450,
            }
        ]
        linha = {
            "id_compra": 12,
            "id_usuario": 7,
            "valor_total_centavos": 450,
            "data_hora": datetime(2026, 11, 17, 22, 50, 3, 120000),
            "itens": itens,
        }
        self.assertEqual(
            compra_repository.compra_json(linha),
            {
                "id_compra": 12,
                "valor_total_centavos": 450,
                "data_hora": "2026-11-17T22:50:03.120000Z",
                "itens": itens,
            },
        )


if __name__ == "__main__":
    unittest.main()
