"""Testes da lógica da administração sem banco real.

Cobrem a interpretação do período (datas de Brasília → intervalo UTC), os
filtros, a validação do ajuste de saldo, os totais dos relatórios e as regras
de usuários (com o repositório substituído por um falso em memória).
"""
from contextlib import contextmanager
from datetime import date, datetime, timezone
from decimal import Decimal
import unittest
from unittest.mock import Mock, patch

from src.backend.admin import repository, service
from src.backend.erros import ErroNegocio, ErroValidacao, NaoEncontrado

HOJE = date(2026, 11, 17)
CHAVE = "123e4567-e89b-12d3-a456-426614174000"

ADMIN = {
    "id_usuario": 1,
    "nome": "Ana Admin",
    "matricula": "1001",
    "email": "ana@exemplo.com",
    "perfil": "ADMINISTRADOR",
    "status": "ATIVO",
    "saldo_centavos": 0,
}
CLIENTE = {
    "id_usuario": 2,
    "nome": "Maria Souza",
    "matricula": "202612345",
    "email": "maria@exemplo.com",
    "perfil": "CLIENTE",
    "status": "ATIVO",
    "saldo_centavos": 1550,
}
EDICAO_ADMIN = {
    "nome": "Ana Admin",
    "matricula": "1001",
    "email": "ana@exemplo.com",
    "perfil": "ADMINISTRADOR",
}
EDICAO_CLIENTE = {
    "nome": "Maria Souza",
    "matricula": "202612345",
    "email": "maria@exemplo.com",
    "perfil": "CLIENTE",
}
CONSUMO_MARIA = {
    "id_usuario": 2,
    "nome": "Maria Souza",
    "matricula": "202612345",
    "quantidade_compras": 3,
    "itens": 8,
    "total_centavos": 4350,
}
COMPRA_12 = {
    "id_compra": 12,
    "data_hora": "2026-11-17T22:50:03.120000Z",
    "valor_total_centavos": 450,
    "usuario": {"id_usuario": 2, "nome": "Maria Souza", "matricula": "202612345"},
    "itens": [
        {"id_produto": 3, "nome": "Suco de uva 200 ml", "quantidade": 1,
         "preco_unitario_centavos": 450, "subtotal_centavos": 450},
    ],
}


def ajuste(**alteracoes):
    return {
        "valor_centavos": 500,
        "motivo": "Troco devolvido",
        "chave_idempotencia": CHAVE,
        **alteracoes,
    }


def validador_falso(valor):
    """Fica no lugar dos validadores de usuarios/validacao.py: aceita texto não vazio."""
    if isinstance(valor, str) and valor.strip():
        return valor.strip(), None
    return None, "Valor inválido."


class RepositorioFalso:
    """Imita o módulo repository guardando os usuários em memória."""

    def __init__(self, usuarios):
        self.usuarios = {usuario["id_usuario"]: dict(usuario) for usuario in usuarios}
        self.duplicado = None  # campo que a próxima gravação acusa como repetido
        self.gravacoes_de_status = 0
        self.consulta_movimentacoes = None
        self.consulta_compras = None
        self.perfil_dos_saldos = None

    @contextmanager
    def transacao(self):
        yield self

    def cursor(self, **_kwargs):
        return self

    def close(self):
        pass

    def carregar_usuario(self, _cursor, id_usuario, bloquear=False):
        usuario = self.usuarios.get(id_usuario)
        return dict(usuario) if usuario else None

    def consultar_usuario(self, id_usuario):
        return self.carregar_usuario(None, id_usuario)

    def atualizar_usuario(self, _cursor, id_usuario, dados):
        if self.duplicado:
            raise repository.RegistroDuplicado(self.duplicado)
        self.usuarios[id_usuario].update(dados)

    def atualizar_status(self, _cursor, id_usuario, status):
        self.gravacoes_de_status += 1
        self.usuarios[id_usuario]["status"] = status

    def listar_movimentacoes(self, inicio_utc, fim_utc, tipo, id_usuario, limite):
        self.consulta_movimentacoes = (inicio_utc, fim_utc, tipo, id_usuario, limite)
        return [], {"creditos_centavos": 0, "debitos_centavos": 0, "ajustes_centavos": 0}

    def relatorio_vendas(self, inicio_utc, fim_utc):
        totais = {
            "quantidade_compras": 12,
            "itens_vendidos": 30,
            "total_centavos": 14250,
            "custo_centavos": 9000,
        }
        return totais, [], [], [dict(CONSUMO_MARIA)]

    def listar_compras(self, inicio_utc, fim_utc, id_usuario, limite):
        self.consulta_compras = (inicio_utc, fim_utc, id_usuario, limite)
        return [dict(COMPRA_12)], 12

    def listar_saldos(self, perfil):
        self.perfil_dos_saldos = perfil
        return [
            {"id_usuario": 2, "nome": "Maria Souza", "matricula": "202612345",
             "status": "ATIVO", "saldo_centavos": 1550},
            {"id_usuario": 3, "nome": "João Lima", "matricula": "202600001",
             "status": "INATIVO", "saldo_centavos": 450},
        ]


class CasoAdmin(unittest.TestCase):
    """Base dos testes: atalho para ler os campos de um ErroValidacao."""

    def campos_invalidos(self, funcao, *args, **kwargs):
        with self.assertRaises(ErroValidacao) as contexto:
            funcao(*args, **kwargs)
        return contexto.exception.campos


class PeriodoTests(CasoAdmin):
    def periodo_invalido(self, de, ate):
        return self.campos_invalidos(service.interpretar_periodo, de, ate, HOJE)

    def test_periodo_padrao_segue_o_exemplo_do_contrato(self):
        periodo = service.interpretar_periodo("", "", HOJE)
        self.assertEqual(periodo.de, date(2026, 10, 18))
        self.assertEqual(periodo.ate, HOJE)
        self.assertEqual(
            service.periodo_json(periodo), {"de": "2026-10-18", "ate": "2026-11-17"}
        )

    def test_parametros_ausentes_valem_como_vazios(self):
        self.assertEqual(
            service.interpretar_periodo(None, None, HOJE),
            service.interpretar_periodo("", "", HOJE),
        )

    def test_limites_utc_ficam_tres_horas_depois_da_meia_noite_local(self):
        periodo = service.interpretar_periodo("2026-11-01", "2026-11-17", HOJE)
        self.assertEqual(periodo.inicio_utc, datetime(2026, 11, 1, 3, 0))
        self.assertEqual(periodo.fim_utc, datetime(2026, 11, 18, 3, 0))
        self.assertIsNone(periodo.inicio_utc.tzinfo)
        self.assertIsNone(periodo.fim_utc.tzinfo)

    def test_dia_local_inteiro_entra_no_periodo(self):
        periodo = service.interpretar_periodo("2026-11-17", "2026-11-17", HOJE)
        vespera = datetime(2026, 11, 17, 2, 59, 59)  # 23:59:59 do dia 16 em Brasília
        primeira = datetime(2026, 11, 17, 3, 0, 0)  # 00:00:00 do dia 17
        ultima = datetime(2026, 11, 18, 2, 59, 59)  # 23:59:59 do dia 17
        seguinte = datetime(2026, 11, 18, 3, 0, 0)  # 00:00:00 do dia 18

        def dentro(momento):
            return periodo.inicio_utc <= momento < periodo.fim_utc

        self.assertFalse(dentro(vespera))
        self.assertTrue(dentro(primeira))
        self.assertTrue(dentro(ultima))
        self.assertFalse(dentro(seguinte))

    def test_somente_ate_recua_trinta_dias(self):
        periodo = service.interpretar_periodo("", "2026-03-10", HOJE)
        self.assertEqual((periodo.de, periodo.ate), (date(2026, 2, 8), date(2026, 3, 10)))

    def test_somente_de_vai_ate_hoje(self):
        periodo = service.interpretar_periodo("2026-11-01", "", HOJE)
        self.assertEqual((periodo.de, periodo.ate), (date(2026, 11, 1), HOJE))

    def test_espacos_em_volta_sao_ignorados(self):
        periodo = service.interpretar_periodo(" 2026-11-01 ", " 2026-11-02 ", HOJE)
        self.assertEqual((periodo.de, periodo.ate), (date(2026, 11, 1), date(2026, 11, 2)))

    def test_datas_invalidas(self):
        invalidas = (
            "17/11/2026",
            "2026-02-30",
            "2026-1-5",
            "20261117",
            "2026-11-17T10:00",
            "ontem",
            "0000-01-01",
            "9999-12-31",
        )
        for texto in invalidas:
            with self.subTest(texto=texto):
                self.assertEqual(set(self.periodo_invalido(texto, "")), {"de"})
                self.assertEqual(set(self.periodo_invalido("", texto)), {"ate"})

    def test_duas_datas_invalidas_apontam_os_dois_campos(self):
        self.assertEqual(set(self.periodo_invalido("abc", "def")), {"de", "ate"})

    def test_de_depois_de_ate(self):
        self.assertIn("de", self.periodo_invalido("2026-11-10", "2026-11-09"))

    def test_de_no_futuro_sem_ate(self):
        self.assertIn("de", self.periodo_invalido("2026-11-18", ""))

    def test_ano_bissexto_inteiro_cabe_no_limite(self):
        periodo = service.interpretar_periodo("2024-01-01", "2024-12-31", HOJE)
        self.assertEqual((periodo.ate - periodo.de).days + 1, 366)

    def test_periodo_maior_que_366_dias(self):
        self.assertTrue(self.periodo_invalido("2024-01-01", "2025-01-01"))

    def test_hoje_em_brasilia_vira_as_tres_da_manha_utc(self):
        antes = datetime(2026, 11, 18, 2, 59, tzinfo=timezone.utc)
        depois = datetime(2026, 11, 18, 3, 0, tzinfo=timezone.utc)
        self.assertEqual(service.hoje_brasilia(antes), date(2026, 11, 17))
        self.assertEqual(service.hoje_brasilia(depois), date(2026, 11, 18))


class FiltrosTests(CasoAdmin):
    def test_filtros_de_usuarios_vazios_valem_todos(self):
        self.assertEqual(
            service.validar_filtros_usuarios("", "", ""), ("", "TODOS", "TODOS")
        )
        self.assertEqual(
            service.validar_filtros_usuarios(None, None, None), ("", "TODOS", "TODOS")
        )

    def test_filtros_de_usuarios_sao_normalizados(self):
        self.assertEqual(
            service.validar_filtros_usuarios("  maria ", "ativo", " cliente "),
            ("maria", "ATIVO", "CLIENTE"),
        )

    def test_filtros_de_usuarios_invalidos(self):
        campos = self.campos_invalidos(
            service.validar_filtros_usuarios, "x" * 101, "BLOQUEADO", "GERENTE"
        )
        self.assertEqual(set(campos), {"q", "status", "perfil"})

    def test_busca_com_cem_caracteres_e_aceita(self):
        termo, _status, _perfil = service.validar_filtros_usuarios("x" * 100, "", "")
        self.assertEqual(len(termo), 100)

    def test_filtros_de_movimentacoes(self):
        self.assertEqual(service.validar_filtros_movimentacoes("", ""), ("TODOS", None))
        self.assertEqual(service.validar_filtros_movimentacoes("debito", " 7 "), ("DEBITO", 7))

    def test_filtros_de_movimentacoes_invalidos(self):
        self.assertEqual(
            set(self.campos_invalidos(service.validar_filtros_movimentacoes, "PIX", "")),
            {"tipo"},
        )
        for texto in ("abc", "0", "-1", "7.5", "99999999999"):
            with self.subTest(id_usuario=texto):
                campos = self.campos_invalidos(
                    service.validar_filtros_movimentacoes, "", texto
                )
                self.assertEqual(set(campos), {"id_usuario"})

    def test_filtro_de_compras(self):
        self.assertIsNone(service.validar_filtros_compras(""))
        self.assertIsNone(service.validar_filtros_compras(None))
        self.assertEqual(service.validar_filtros_compras(" 7 "), 7)
        for texto in ("abc", "0", "-1", "7.5", "99999999999"):
            with self.subTest(id_usuario=texto):
                campos = self.campos_invalidos(service.validar_filtros_compras, texto)
                self.assertEqual(set(campos), {"id_usuario"})


class AjusteTests(CasoAdmin):
    def test_ajuste_valido(self):
        self.assertEqual(service.validar_ajuste(ajuste()), (500, "Troco devolvido", CHAVE))

    def test_aceita_valor_negativo_e_os_limites(self):
        for valor in (-500, 1, -1, 100_000, -100_000):
            with self.subTest(valor=valor):
                self.assertEqual(service.validar_ajuste(ajuste(valor_centavos=valor))[0], valor)

    def test_valor_invalido(self):
        for valor in (0, 100_001, -100_001, True, False, 10.5, "500", None, [500]):
            with self.subTest(valor=valor):
                campos = self.campos_invalidos(
                    service.validar_ajuste, ajuste(valor_centavos=valor)
                )
                self.assertEqual(set(campos), {"valor_centavos"})

    def test_motivo_e_aparado(self):
        self.assertEqual(service.validar_ajuste(ajuste(motivo="  Troco  "))[1], "Troco")
        self.assertEqual(len(service.validar_ajuste(ajuste(motivo="x" * 150))[1]), 150)

    def test_motivo_invalido(self):
        for motivo in ("", "abcd", "   abcd   ", "x" * 151, None, 12345):
            with self.subTest(motivo=motivo):
                campos = self.campos_invalidos(service.validar_ajuste, ajuste(motivo=motivo))
                self.assertEqual(set(campos), {"motivo"})

    def test_chave_de_idempotencia(self):
        valida = service.validar_ajuste(ajuste(chave_idempotencia=CHAVE.upper()))
        self.assertEqual(valida[2], CHAVE)
        for chave in ("", "abc", None, 123):
            with self.subTest(chave=chave):
                campos = self.campos_invalidos(
                    service.validar_ajuste, ajuste(chave_idempotencia=chave)
                )
                self.assertEqual(set(campos), {"chave_idempotencia"})

    def test_todos_os_erros_aparecem_juntos(self):
        campos = self.campos_invalidos(service.validar_ajuste, {})
        self.assertEqual(set(campos), {"valor_centavos", "motivo", "chave_idempotencia"})


class RelatoriosTests(CasoAdmin):
    def test_resumo_de_vendas_do_exemplo_do_contrato(self):
        resumo = service.montar_resumo_vendas(12, 30, 14250, 9000)
        self.assertEqual(
            resumo,
            {
                "quantidade_compras": 12,
                "itens_vendidos": 30,
                "total_centavos": 14250,
                "custo_centavos": 9000,
                "lucro_centavos": 5250,
                "ticket_medio_centavos": 1187,
            },
        )

    def test_resumo_sem_compras_nao_divide_por_zero(self):
        resumo = service.montar_resumo_vendas(0, 0, 0, 0)
        self.assertEqual(resumo["ticket_medio_centavos"], 0)
        self.assertEqual(resumo["lucro_centavos"], 0)

    def test_estoque_conta_sem_estoque_somente_entre_ativos(self):
        produtos = [
            {"id_produto": 1, "status": "ATIVO", "quantidade_estoque": 0,
             "valor_estoque_centavos": 0},
            {"id_produto": 2, "status": "INATIVO", "quantidade_estoque": 0,
             "valor_estoque_centavos": 0},
            {"id_produto": 3, "status": "ATIVO", "quantidade_estoque": 10,
             "valor_estoque_centavos": 3000},
            {"id_produto": 4, "status": "INATIVO", "quantidade_estoque": 4,
             "valor_estoque_centavos": 800},
        ]
        resumo = service.resumir_estoque(produtos)
        self.assertEqual(resumo["quantidade_produtos"], 4)
        self.assertEqual(resumo["sem_estoque"], 1)
        self.assertEqual(resumo["total_itens"], 14)
        self.assertEqual(resumo["valor_estoque_centavos"], 3800)
        self.assertIs(resumo["produtos"], produtos)

    def test_estoque_vazio(self):
        resumo = service.resumir_estoque([])
        self.assertEqual(
            resumo,
            {
                "quantidade_produtos": 0,
                "sem_estoque": 0,
                "total_itens": 0,
                "valor_estoque_centavos": 0,
                "produtos": [],
            },
        )


class ApoioDoRepositorioTests(unittest.TestCase):
    def test_inteiro_converte_o_resultado_de_sum(self):
        convertido = repository.inteiro(Decimal("14250"))
        self.assertEqual(convertido, 14250)
        self.assertIsInstance(convertido, int)
        self.assertEqual(repository.inteiro(None), 0)
        self.assertEqual(repository.inteiro(7), 7)

    def test_campo_duplicado_pelo_nome_da_restricao(self):
        casos = {
            "1062 (23000): Duplicate entry '202612345' for key "
            "'usuarios.uq_usuarios_matricula'": "matricula",
            "1062 (23000): Duplicate entry 'a@b.com' for key "
            "'usuarios.uq_usuarios_email'": "email",
            "Duplicate entry 'a@b.com' for key 'uq_usuarios_email'": "email",
            "Duplicate entry '52998224725' for key 'usuarios.uq_usuarios_cpf'": None,
            "": None,
        }
        for mensagem, campo in casos.items():
            with self.subTest(mensagem=mensagem):
                self.assertEqual(repository.campo_duplicado(mensagem), campo)

    def test_campo_duplicado_ignora_o_valor_digitado(self):
        mensagem = (
            "Duplicate entry 'uq_usuarios_matricula@x.com' for key "
            "'usuarios.uq_usuarios_email'"
        )
        self.assertEqual(repository.campo_duplicado(mensagem), "email")

    def test_padrao_de_busca_trata_curingas_como_texto(self):
        self.assertEqual(repository.padrao_busca("maria"), "%maria%")
        self.assertEqual(repository.padrao_busca("50%_a\\b"), "%50\\%\\_a\\\\b%")

    def test_juntar_itens_distribui_cada_item_na_sua_compra(self):
        def linha(id_compra, id_produto, nome, quantidade, preco):
            return {
                "id_compra": id_compra,
                "id_produto": id_produto,
                "nome": nome,
                "quantidade": quantidade,
                "preco_unitario_centavos": preco,
                "subtotal_centavos": quantidade * preco,
            }

        # Compras na ordem da página (mais recente primeiro); itens na ordem do SQL.
        compras = [
            {"id_compra": 12, "itens": []},
            {"id_compra": 11, "itens": []},
            {"id_compra": 10, "itens": []},
        ]
        linhas = [
            linha(10, 3, "Suco de uva 200 ml", 2, 450),
            linha(12, 5, "Pão de queijo", 1, 500),
            linha(12, 3, "Suco de uva 200 ml", 1, 450),
        ]
        resultado = repository.juntar_itens(compras, linhas)

        self.assertIs(resultado, compras)
        self.assertEqual([compra["id_compra"] for compra in compras], [12, 11, 10])
        self.assertEqual([item["id_produto"] for item in compras[0]["itens"]], [5, 3])
        self.assertEqual(compras[1]["itens"], [])
        self.assertEqual(
            compras[2]["itens"],
            [
                {
                    "id_produto": 3,
                    "nome": "Suco de uva 200 ml",
                    "quantidade": 2,
                    "preco_unitario_centavos": 450,
                    "subtotal_centavos": 900,
                }
            ],
        )
        # A chave id_compra da linha não vaza para o item devolvido à tela.
        self.assertNotIn("id_compra", compras[0]["itens"][0])


class UsuariosTests(CasoAdmin):
    def setUp(self):
        self.repo = RepositorioFalso([ADMIN, CLIENTE])
        self.carteira = Mock()
        substitutos = {
            "admin_repository": self.repo,
            "carteira_service": self.carteira,
            "validar_nome": validador_falso,
            "validar_matricula": validador_falso,
            "validar_email": validador_falso,
        }
        for nome, substituto in substitutos.items():
            ativo = patch.object(service, nome, substituto)
            ativo.start()
            self.addCleanup(ativo.stop)

    # ----- validação da edição -----

    def test_edicao_valida_normaliza_os_campos(self):
        dados = service.validar_edicao_usuario(
            {**EDICAO_CLIENTE, "nome": "  Maria Souza  ", "perfil": " cliente "}
        )
        self.assertEqual(dados, EDICAO_CLIENTE)

    def test_edicao_recusa_campos_extras(self):
        campos = self.campos_invalidos(
            service.validar_edicao_usuario,
            {**EDICAO_CLIENTE, "cpf": "52998224725", "status": "INATIVO"},
        )
        self.assertEqual(
            campos, {"cpf": "Campo não permitido.", "status": "Campo não permitido."}
        )

    def test_edicao_exige_todos_os_campos(self):
        campos = self.campos_invalidos(service.validar_edicao_usuario, {})
        self.assertEqual(set(campos), {"nome", "matricula", "email", "perfil"})

    def test_edicao_recusa_perfil_desconhecido(self):
        for perfil in ("GERENTE", "", 1, True):
            with self.subTest(perfil=perfil):
                campos = self.campos_invalidos(
                    service.validar_edicao_usuario, {**EDICAO_CLIENTE, "perfil": perfil}
                )
                self.assertEqual(set(campos), {"perfil"})

    def test_edicao_repassa_a_mensagem_dos_validadores(self):
        campos = self.campos_invalidos(
            service.validar_edicao_usuario, {**EDICAO_CLIENTE, "email": "   "}
        )
        self.assertEqual(campos, {"email": "Valor inválido."})

    # ----- alterar -----

    def test_alterar_grava_os_dados_e_o_perfil(self):
        usuario = service.alterar_usuario(
            2, {**EDICAO_CLIENTE, "nome": "Maria S. Lima", "perfil": "ADMINISTRADOR"}, ADMIN
        )
        self.assertEqual(usuario["nome"], "Maria S. Lima")
        self.assertEqual(usuario["perfil"], "ADMINISTRADOR")

    def test_administrador_nao_tira_o_proprio_perfil(self):
        with self.assertRaises(ErroNegocio) as contexto:
            service.alterar_usuario(1, {**EDICAO_ADMIN, "perfil": "CLIENTE"}, ADMIN)
        self.assertEqual(contexto.exception.codigo, "OPERACAO_PROPRIA")
        self.assertEqual(self.repo.usuarios[1]["perfil"], "ADMINISTRADOR")

    def test_administrador_edita_os_proprios_dados(self):
        usuario = service.alterar_usuario(1, {**EDICAO_ADMIN, "nome": "Ana Paula"}, ADMIN)
        self.assertEqual(usuario["nome"], "Ana Paula")
        self.assertEqual(usuario["perfil"], "ADMINISTRADOR")

    def test_alterar_usuario_inexistente(self):
        with self.assertRaises(NaoEncontrado):
            service.alterar_usuario(99, EDICAO_CLIENTE, ADMIN)

    def test_matricula_ou_email_repetido_vira_erro_no_campo(self):
        for campo in ("matricula", "email"):
            with self.subTest(campo=campo):
                self.repo.duplicado = campo
                campos = self.campos_invalidos(
                    service.alterar_usuario, 2, EDICAO_CLIENTE, ADMIN
                )
                self.assertEqual(set(campos), {campo})

    # ----- inativar e reativar -----

    def test_inativar_e_reativar(self):
        self.assertEqual(service.inativar_usuario(2, ADMIN)["status"], "INATIVO")
        self.assertEqual(service.reativar_usuario(2)["status"], "ATIVO")

    def test_inativar_duas_vezes_devolve_o_mesmo_usuario(self):
        primeiro = service.inativar_usuario(2, ADMIN)
        segundo = service.inativar_usuario(2, ADMIN)
        self.assertEqual(primeiro, segundo)
        self.assertEqual(self.repo.gravacoes_de_status, 1)

    def test_administrador_nao_inativa_a_si_mesmo(self):
        with self.assertRaises(ErroNegocio) as contexto:
            service.inativar_usuario(1, ADMIN)
        self.assertEqual(contexto.exception.codigo, "OPERACAO_PROPRIA")
        self.assertEqual(self.repo.usuarios[1]["status"], "ATIVO")

    def test_mudar_status_de_usuario_inexistente(self):
        with self.assertRaises(NaoEncontrado):
            service.inativar_usuario(99, ADMIN)
        with self.assertRaises(NaoEncontrado):
            service.reativar_usuario(99)

    def test_consultar_usuario_inexistente(self):
        with self.assertRaises(NaoEncontrado) as contexto:
            service.consultar_usuario(99)
        self.assertEqual(contexto.exception.mensagem, "Usuário não encontrado.")

    # ----- ajuste de saldo -----

    def test_ajuste_chama_a_carteira_com_o_administrador_como_autor(self):
        resultado = ({"id_movimentacao": 31}, {"saldo_centavos": 1300}, True)
        self.carteira.ajustar_saldo.return_value = resultado
        self.assertEqual(
            service.ajustar_saldo(2, ajuste(valor_centavos=-250), ADMIN), resultado
        )
        self.carteira.ajustar_saldo.assert_called_once_with(
            2, -250, "Troco devolvido", 1, CHAVE
        )

    def test_ajuste_para_usuario_inexistente_nao_chega_na_carteira(self):
        with self.assertRaises(NaoEncontrado):
            service.ajustar_saldo(99, ajuste(), ADMIN)
        self.carteira.ajustar_saldo.assert_not_called()

    def test_ajuste_invalido_nao_chega_na_carteira(self):
        with self.assertRaises(ErroValidacao):
            service.ajustar_saldo(2, ajuste(valor_centavos=0), ADMIN)
        self.carteira.ajustar_saldo.assert_not_called()

    # ----- movimentações e relatórios (montagem da resposta) -----

    def test_movimentacoes_enviam_o_intervalo_utc_ao_repositorio(self):
        resposta = service.listar_movimentacoes(
            "2026-11-01", "2026-11-17", "debito", "2", 200, hoje=HOJE
        )
        self.assertEqual(resposta["periodo"], {"de": "2026-11-01", "ate": "2026-11-17"})
        self.assertEqual(
            self.repo.consulta_movimentacoes,
            (datetime(2026, 11, 1, 3, 0), datetime(2026, 11, 18, 3, 0), "DEBITO", 2, 200),
        )
        self.assertEqual(
            resposta["totais"],
            {"creditos_centavos": 0, "debitos_centavos": 0, "ajustes_centavos": 0},
        )

    def test_relatorio_de_vendas_monta_periodo_e_resumo(self):
        relatorio = service.relatorio_vendas("", "", hoje=HOJE)
        self.assertEqual(relatorio["periodo"], {"de": "2026-10-18", "ate": "2026-11-17"})
        self.assertEqual(relatorio["resumo"]["lucro_centavos"], 5250)
        self.assertEqual(relatorio["resumo"]["ticket_medio_centavos"], 1187)
        self.assertEqual(relatorio["por_produto"], [])
        self.assertEqual(relatorio["por_dia"], [])
        self.assertEqual(relatorio["por_usuario"], [CONSUMO_MARIA])
        self.assertEqual(
            set(relatorio), {"periodo", "resumo", "por_produto", "por_dia", "por_usuario"}
        )

    def test_compras_enviam_o_intervalo_utc_e_o_filtro_ao_repositorio(self):
        resposta = service.listar_compras("2026-11-01", "2026-11-17", " 2 ", 100, hoje=HOJE)
        self.assertEqual(
            self.repo.consulta_compras,
            (datetime(2026, 11, 1, 3, 0), datetime(2026, 11, 18, 3, 0), 2, 100),
        )
        self.assertEqual(
            resposta,
            {
                "periodo": {"de": "2026-11-01", "ate": "2026-11-17"},
                "total_compras": 12,
                "compras": [COMPRA_12],
            },
        )

    def test_compras_sem_filtros_usam_o_periodo_padrao_e_todos_os_usuarios(self):
        resposta = service.listar_compras("", "", "", 100, hoje=HOJE)
        self.assertEqual(resposta["periodo"], {"de": "2026-10-18", "ate": "2026-11-17"})
        self.assertIsNone(self.repo.consulta_compras[2])

    def test_compras_com_filtro_invalido_nao_chegam_ao_repositorio(self):
        self.assertEqual(
            set(self.campos_invalidos(service.listar_compras, "", "", "abc", 100, hoje=HOJE)),
            {"id_usuario"},
        )
        self.assertEqual(
            set(self.campos_invalidos(service.listar_compras, "ontem", "", "", 100, hoje=HOJE)),
            {"de"},
        )
        self.assertIsNone(self.repo.consulta_compras)

    def test_relatorio_de_saldos_soma_somente_clientes(self):
        relatorio = service.relatorio_saldos()
        self.assertEqual(self.repo.perfil_dos_saldos, "CLIENTE")
        self.assertEqual(relatorio["quantidade_usuarios"], 2)
        self.assertEqual(relatorio["total_saldos_centavos"], 2000)


if __name__ == "__main__":
    unittest.main()
