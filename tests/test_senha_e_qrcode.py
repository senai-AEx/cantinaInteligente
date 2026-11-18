"""Testes da troca de senha e do QR Code, sem banco real."""
from contextlib import contextmanager
import os
import unittest
from unittest.mock import patch

from werkzeug.security import check_password_hash, generate_password_hash

from src.backend.app import app
from src.backend.qr import service as qr_service
from src.backend.usuarios import service as usuario_service
from tests.apoio import ADMINISTRADOR, CLIENTE, simular_login

SENHA_ATUAL = "antiga123"
SENHA_NOVA = "novinha456"


class RepositorioDeSenhas:
    """Imita usuarios.repository guardando só os hashes das senhas."""

    def __init__(self):
        self.hashes = {CLIENTE["id_usuario"]: generate_password_hash(SENHA_ATUAL)}

    @contextmanager
    def transacao(self):
        yield self

    def cursor(self, **_kwargs):
        return self

    def close(self):
        pass

    def buscar_senha_hash(self, _cursor, id_usuario, bloquear=False):
        return self.hashes.get(id_usuario)

    def atualizar_senha(self, _cursor, id_usuario, senha_hash):
        self.hashes[id_usuario] = senha_hash

    def carregar(self, _cursor, id_usuario):
        return dict(CLIENTE) if id_usuario == CLIENTE["id_usuario"] else None


class SenhaTests(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioDeSenhas()
        substituto = patch.object(usuario_service, "usuario_repository", self.repo)
        substituto.start()
        self.addCleanup(substituto.stop)
        self.cliente = app.test_client()

    def trocar(self, **alteracoes):
        corpo = {"senha_atual": SENHA_ATUAL, "nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA}
        return self.cliente.put("/api/auth/senha", json={**corpo, **alteracoes})

    def test_troca_exige_login(self):
        self.assertEqual(self.trocar().status_code, 401)

    def test_troca_com_sucesso_grava_novo_hash(self):
        simular_login(self, self.cliente, CLIENTE)
        resposta = self.trocar()
        self.assertEqual(resposta.status_code, 200)
        novo_hash = self.repo.hashes[CLIENTE["id_usuario"]]
        self.assertTrue(check_password_hash(novo_hash, SENHA_NOVA))
        self.assertNotIn(SENHA_NOVA, novo_hash)

    def test_senha_atual_errada(self):
        simular_login(self, self.cliente, CLIENTE)
        resposta = self.trocar(senha_atual="outra-senha-1")
        self.assertEqual(resposta.status_code, 422)
        self.assertIn("senha_atual", resposta.json["campos"])
        self.assertTrue(check_password_hash(self.repo.hashes[CLIENTE["id_usuario"]], SENHA_ATUAL))

    def test_nova_senha_fraca_igual_ou_sem_confirmacao(self):
        simular_login(self, self.cliente, CLIENTE)
        casos = (
            ({"nova_senha": "curta1", "confirmar_senha": "curta1"}, "nova_senha"),
            ({"nova_senha": SENHA_ATUAL, "confirmar_senha": SENHA_ATUAL}, "nova_senha"),
            ({"confirmar_senha": "diferente789"}, "confirmar_senha"),
        )
        for alteracoes, campo in casos:
            with self.subTest(campo=campo, alteracoes=list(alteracoes)):
                resposta = self.trocar(**alteracoes)
                self.assertEqual(resposta.status_code, 422)
                self.assertIn(campo, resposta.json["campos"])

    def test_cliente_nao_redefine_senha_de_ninguem(self):
        simular_login(self, self.cliente, CLIENTE)
        resposta = self.cliente.post(
            f"/api/admin/usuarios/{CLIENTE['id_usuario']}/senha",
            json={"nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA},
        )
        self.assertEqual(resposta.status_code, 403)

    def test_administrador_redefine_senha(self):
        simular_login(self, self.cliente, ADMINISTRADOR)
        resposta = self.cliente.post(
            f"/api/admin/usuarios/{CLIENTE['id_usuario']}/senha",
            json={"nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA},
        )
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json["usuario"]["id_usuario"], CLIENTE["id_usuario"])
        self.assertNotIn("senha", str(resposta.json).replace("cpf_mascarado", ""))
        self.assertTrue(check_password_hash(self.repo.hashes[CLIENTE["id_usuario"]], SENHA_NOVA))

    def test_redefinir_usuario_inexistente(self):
        simular_login(self, self.cliente, ADMINISTRADOR)
        resposta = self.cliente.post(
            "/api/admin/usuarios/999/senha",
            json={"nova_senha": SENHA_NOVA, "confirmar_senha": SENHA_NOVA},
        )
        self.assertEqual(resposta.status_code, 404)


class QrCodeTests(unittest.TestCase):
    def test_endereco_publico_tem_prioridade(self):
        with patch.dict(os.environ, {"URL_PUBLICA": "http://192.168.0.10:5000/"}):
            base = qr_service.url_base("http://127.0.0.1:5000/")
        self.assertEqual(base, "http://192.168.0.10:5000")
        self.assertFalse(qr_service.somente_local(base))

    def test_endereco_publico_invalido_e_ignorado(self):
        with patch.dict(os.environ, {"URL_PUBLICA": "javascript:alert(1)"}):
            self.assertEqual(qr_service.url_base("http://127.0.0.1:5000/"), "http://127.0.0.1:5000")

    def test_sem_endereco_publico_usa_o_da_requisicao_e_avisa_que_e_local(self):
        with patch.dict(os.environ, {"URL_PUBLICA": ""}):
            base = qr_service.url_base("http://localhost:5000/")
        self.assertTrue(qr_service.somente_local(base))

    def test_enderecos_do_catalogo_e_do_produto(self):
        info = qr_service.informacoes("http://192.168.0.10:5000")
        self.assertEqual(info["url_cantina"], "http://192.168.0.10:5000/html/catalogo_produtos.html")
        self.assertEqual(
            info["url_produto"], "http://192.168.0.10:5000/html/catalogo_produtos.html?adicionar={id}"
        )

    def test_desenha_svg(self):
        svg = qr_service.desenhar_svg("http://192.168.0.10:5000/html/catalogo_produtos.html?adicionar=7")
        self.assertTrue(svg.startswith(b"<svg"))
        self.assertIn(b"viewBox", svg)

    def test_rotas_exigem_administrador(self):
        cliente = app.test_client()
        self.assertEqual(cliente.get("/api/qrcode").status_code, 401)
        self.assertEqual(cliente.get("/api/qrcode/cantina.svg").status_code, 401)
        simular_login(self, cliente, CLIENTE)
        self.assertEqual(cliente.get("/api/qrcode/cantina.svg").status_code, 403)

    def test_administrador_recebe_a_imagem(self):
        cliente = app.test_client()
        simular_login(self, cliente, ADMINISTRADOR)
        resposta = cliente.get("/api/qrcode/cantina.svg")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.mimetype, "image/svg+xml")
        self.assertTrue(resposta.data.startswith(b"<svg"))
        self.assertIn("url_cantina", cliente.get("/api/qrcode").json)


if __name__ == "__main__":
    unittest.main()
