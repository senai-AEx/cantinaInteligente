"""Testes do separador de SQL e da escrita de valores do backup (sem banco de dados)."""
import datetime as dt
import sys
import unittest
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import banco  # noqa: E402


class SepararInstrucoesTests(unittest.TestCase):
    def test_divide_por_ponto_e_virgula(self):
        partes = banco.separar_instrucoes("SELECT 1; SELECT 2;")
        self.assertEqual(partes, ["SELECT 1", "SELECT 2"])

    def test_ponto_e_virgula_dentro_de_texto_nao_divide(self):
        partes = banco.separar_instrucoes("INSERT INTO t VALUES ('a;b'); SELECT 1;")
        self.assertEqual(partes, ["INSERT INTO t VALUES ('a;b')", "SELECT 1"])

    def test_aspas_escapadas_com_barra(self):
        partes = banco.separar_instrucoes(r"INSERT INTO t VALUES ('x\'y;z'); SELECT 1;")
        self.assertEqual(len(partes), 2)
        self.assertIn(r"'x\'y;z'", partes[0])

    def test_ignora_comentarios_de_linha_e_de_bloco(self):
        sql = "-- comentario; com ponto\nSELECT 1; /* bloco; */ SELECT 2;"
        self.assertEqual(banco.separar_instrucoes(sql), ["SELECT 1", "SELECT 2"])

    def test_arquivos_de_migracao_viram_instrucoes(self):
        for nome in banco.MIGRACOES + ["produtos_exemplo.sql"]:
            caminho = (banco.PASTA_MIGRACOES if nome.startswith("0") else banco.ARQUIVO_SEMENTE.parent) / nome
            with self.subTest(arquivo=nome):
                instrucoes = banco.separar_instrucoes(caminho.read_text(encoding="utf-8-sig"))
                self.assertTrue(instrucoes)
                self.assertTrue(all(i.strip() for i in instrucoes))

    def test_create_database_e_use_sao_ignorados_pelo_usuario_do_sistema(self):
        self.assertTrue(banco._sem_criacao_de_banco("CREATE DATABASE IF NOT EXISTS x"))
        self.assertTrue(banco._sem_criacao_de_banco("  USE cantina_inteligente"))
        self.assertFalse(banco._sem_criacao_de_banco("CREATE TABLE t (id INT)"))


class LiteralDoBackupTests(unittest.TestCase):
    def test_valores_comuns(self):
        self.assertEqual(banco._literal(None), "NULL")
        self.assertEqual(banco._literal(True), "1")
        self.assertEqual(banco._literal(False), "0")
        self.assertEqual(banco._literal(450), "450")
        self.assertEqual(banco._literal(Decimal("2.50")), "2.50")
        self.assertEqual(banco._literal(dt.date(2026, 11, 17)), "'2026-11-17'")
        self.assertEqual(banco._literal(dt.datetime(2026, 11, 17, 22, 5, 1, 123)), "'2026-11-17 22:05:01.000123'")

    def test_texto_com_aspas_e_barras_e_escapado(self):
        self.assertEqual(banco._literal("O'Neil"), "'O\\'Neil'")
        self.assertIn("\\\\", banco._literal("caminho\\pasta"))

    def test_bytes_viram_hexadecimal(self):
        self.assertEqual(banco._literal(b"\x01\xff"), "X'01ff'")


class ConfiguracaoTests(unittest.TestCase):
    def test_porta_invalida_gera_erro_claro(self):
        import os
        from unittest.mock import patch

        with patch.dict(os.environ, {}, clear=False):
            with patch.object(banco, "ler_env", lambda: {"MYSQL_PORT": "abc"}):
                with self.assertRaises(banco.ErroBanco):
                    banco.configuracao()

    def test_nome_de_banco_com_caracteres_perigosos_e_recusado(self):
        from unittest.mock import patch

        with patch.object(banco, "ler_env", lambda: {"MYSQL_DATABASE": "x; DROP TABLE y"}):
            with self.assertRaises(banco.ErroBanco):
                banco.configuracao()


if __name__ == "__main__":
    unittest.main()
