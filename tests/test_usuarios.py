"""Testes de cadastro e login sem banco real (repositório substituído por um falso)."""
from contextlib import contextmanager
import unittest
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from src.backend.app import app
from src.backend.usuarios import service
from src.backend.usuarios.validacao import (
    validar_cadastro,
    validar_cpf,
    validar_email,
    validar_matricula,
    validar_senha,
)

CADASTRO_VALIDO = {
    "nome": "Maria Souza",
    "matricula": "202612345",
    "cpf": "529.982.247-25",
    "email": "Maria@Exemplo.com",
    "senha": "segredo123",
    "confirmar_senha": "segredo123",
}


class RepositorioFalso:
    """Imita usuarios.repository guardando os usuários em memória."""

    def __init__(self):
        self.usuarios = {}
        self.senhas = {}
        self.proximo_id = 1

    @contextmanager
    def transacao(self):
        yield self

    def cursor(self, **_kwargs):
        return self

    def close(self):
        pass

    def inserir(self, _cursor, dados, senha_hash, perfil="CLIENTE"):
        id_usuario = self.proximo_id
        self.proximo_id += 1
        self.usuarios[id_usuario] = {
            "id_usuario": id_usuario,
            "nome": dados["nome"],
            "matricula": dados["matricula"],
            "cpf": dados["cpf"],
            "email": dados["email"],
            "perfil": perfil,
            "status": "ATIVO",
            "saldo_centavos": 0,
            "criado_em": None,
        }
        self.senhas[id_usuario] = senha_hash
        return id_usuario

    def criar_carteira(self, _cursor, id_usuario):
        pass

    def carregar(self, _cursor, id_usuario):
        return self.buscar_por_id(id_usuario)

    def buscar_por_id(self, id_usuario):
        usuario = self.usuarios.get(id_usuario)
        return dict(usuario) if usuario else None

    def buscar_credenciais(self, email, digitos):
        encontrados = []
        for usuario in self.usuarios.values():
            if (email and usuario["email"] == email) or (
                digitos and digitos in (usuario["matricula"], usuario["cpf"])
            ):
                encontrados.append(
                    {
                        "id_usuario": usuario["id_usuario"],
                        "senha_hash": self.senhas[usuario["id_usuario"]],
                        "status": usuario["status"],
                    }
                )
        return encontrados


class AutenticacaoTests(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioFalso()
        for alvo in (
            patch.object(service, "usuario_repository", self.repo),
            patch("src.backend.seguranca.carregar_usuario", self.repo.buscar_por_id),
        ):
            alvo.start()
            self.addCleanup(alvo.stop)
        self.cliente = app.test_client()

    def cadastrar(self, **alteracoes):
        return self.cliente.post("/api/auth/cadastro", json={**CADASTRO_VALIDO, **alteracoes})

    def test_cadastro_cria_cliente_logado_sem_expor_senha_nem_cpf(self):
        resposta = self.cadastrar()
        self.assertEqual(resposta.status_code, 201)
        usuario = resposta.json["usuario"]
        self.assertEqual(usuario["perfil"], "CLIENTE")
        self.assertEqual(usuario["email"], "maria@exemplo.com")
        self.assertEqual(usuario["cpf_mascarado"], "***.982.247-**")
        self.assertNotIn("cpf", usuario)
        self.assertNotIn("senha_hash", usuario)
        self.assertNotEqual(self.repo.senhas[1], "segredo123")
        self.assertEqual(self.cliente.get("/api/auth/eu").json["usuario"]["id_usuario"], 1)

    def test_cadastro_invalido_aponta_cada_campo(self):
        resposta = self.cadastrar(
            nome="A", matricula="12a", cpf="111.111.111-11", email="sem-arroba",
            senha="curta", confirmar_senha="outra",
        )
        self.assertEqual(resposta.status_code, 422)
        self.assertEqual(
            set(resposta.json["campos"]), {"nome", "matricula", "cpf", "email", "senha"}
        )
        self.assertEqual(self.repo.usuarios, {})

    def test_confirmacao_de_senha_diferente(self):
        resposta = self.cadastrar(confirmar_senha="segredo124")
        self.assertEqual(resposta.status_code, 422)
        self.assertIn("confirmar_senha", resposta.json["campos"])

    def test_login_por_matricula_email_e_cpf(self):
        self.cadastrar()
        self.cliente.post("/api/auth/logout")
        for identificador in ("202612345", "MARIA@exemplo.com", "529.982.247-25", "52998224725"):
            with self.subTest(identificador=identificador):
                resposta = self.cliente.post(
                    "/api/auth/login", json={"identificador": identificador, "senha": "segredo123"}
                )
                self.assertEqual(resposta.status_code, 200)
                self.assertEqual(resposta.json["usuario"]["nome"], "Maria Souza")
                self.cliente.post("/api/auth/logout")

    def test_login_com_senha_errada_ou_usuario_inexistente(self):
        self.cadastrar()
        self.cliente.post("/api/auth/logout")
        for identificador, senha in (("202612345", "errada123"), ("999999", "segredo123")):
            with self.subTest(identificador=identificador):
                resposta = self.cliente.post(
                    "/api/auth/login", json={"identificador": identificador, "senha": senha}
                )
                self.assertEqual(resposta.status_code, 401)
        self.assertIsNone(self.cliente.get("/api/auth/eu").json["usuario"])

    def test_usuario_inativo_nao_entra_e_perde_a_sessao(self):
        self.cadastrar()
        self.repo.usuarios[1]["status"] = "INATIVO"
        self.assertIsNone(self.cliente.get("/api/auth/eu").json["usuario"])
        resposta = self.cliente.post(
            "/api/auth/login", json={"identificador": "202612345", "senha": "segredo123"}
        )
        self.assertEqual(resposta.status_code, 403)

    def test_logout_encerra_a_sessao(self):
        self.cadastrar()
        self.assertEqual(self.cliente.post("/api/auth/logout").status_code, 200)
        self.assertIsNone(self.cliente.get("/api/auth/eu").json["usuario"])

    def test_login_exige_os_dois_campos(self):
        resposta = self.cliente.post("/api/auth/login", json={})
        self.assertEqual(resposta.status_code, 422)
        self.assertEqual(set(resposta.json["campos"]), {"identificador", "senha"})


class ValidacaoUsuarioTests(unittest.TestCase):
    def test_cpf(self):
        self.assertEqual(validar_cpf("529.982.247-25"), ("52998224725", None))
        for invalido in ("529.982.247-26", "111.111.111-11", "123", None):
            with self.subTest(cpf=invalido):
                self.assertIsNotNone(validar_cpf(invalido)[1])

    def test_matricula_so_numeros(self):
        self.assertEqual(validar_matricula(" 202612345 "), ("202612345", None))
        for invalida in ("12", "12a45", "1" * 21, ""):
            with self.subTest(matricula=invalida):
                self.assertIsNotNone(validar_matricula(invalida)[1])

    def test_email_em_minusculas(self):
        self.assertEqual(validar_email(" Ana@Senai.BR "), ("ana@senai.br", None))
        self.assertIsNotNone(validar_email("ana@senai")[1])

    def test_senha_precisa_de_letra_e_numero(self):
        self.assertIsNone(validar_senha("abc12345")[1])
        for fraca in ("abcdefgh", "12345678", "a1", "a1" * 40):
            with self.subTest(senha=fraca):
                self.assertIsNotNone(validar_senha(fraca)[1])

    def test_campo_desconhecido_e_recusado(self):
        _, erros = validar_cadastro({**CADASTRO_VALIDO, "perfil": "ADMINISTRADOR"})
        self.assertIn("perfil", erros)

    def test_hash_nao_e_a_senha(self):
        self.assertNotIn("segredo123", generate_password_hash("segredo123"))


if __name__ == "__main__":
    unittest.main()
