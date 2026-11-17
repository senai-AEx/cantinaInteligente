import io
from pathlib import Path
import tempfile
import unittest

from src.backend.app import app
from tests.apoio import ADMINISTRADOR, simular_login


class UploadImagemProdutoTests(unittest.TestCase):
    def setUp(self):
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        self.config_original = app.config["PRODUCT_IMAGE_FOLDER"]
        self.testing_original = app.testing
        app.config["PRODUCT_IMAGE_FOLDER"] = Path(self.pasta_temporaria.name)
        app.testing = True
        self.client = app.test_client()
        simular_login(self, self.client, ADMINISTRADOR)

    def tearDown(self):
        app.config["PRODUCT_IMAGE_FOLDER"] = self.config_original
        app.testing = self.testing_original
        self.pasta_temporaria.cleanup()

    def test_salva_imagem_com_nome_gerado_e_retorna_caminho_relativo(self):
        imagem_png = b"\x89PNG\r\n\x1a\n" + b"conteudo-de-teste"
        resposta = self.client.post(
            "/api/uploads/produtos",
            data={"imagem": (io.BytesIO(imagem_png), "produto.png")},
            content_type="multipart/form-data",
        )

        self.assertEqual(resposta.status_code, 201)
        caminho_relativo = resposta.json["foto_caminho"]
        self.assertRegex(caminho_relativo, r"^assets/produtos/[a-f0-9]{32}\.png$")
        arquivo_salvo = Path(self.pasta_temporaria.name) / Path(caminho_relativo).name
        self.assertEqual(arquivo_salvo.read_bytes(), imagem_png)

    def test_rejeita_conteudo_que_nao_corresponde_a_imagem(self):
        resposta = self.client.post(
            "/api/uploads/produtos",
            data={"imagem": (io.BytesIO(b"nao-e-imagem"), "produto.png")},
            content_type="multipart/form-data",
        )

        self.assertEqual(resposta.status_code, 422)
        self.assertIn("imagem", resposta.json["campos"])
        self.assertEqual(list(Path(self.pasta_temporaria.name).iterdir()), [])

    def test_rejeita_extensao_nao_suportada(self):
        resposta = self.client.post(
            "/api/uploads/produtos",
            data={"imagem": (io.BytesIO(b"arquivo"), "produto.gif")},
            content_type="multipart/form-data",
        )

        self.assertEqual(resposta.status_code, 422)
        self.assertIn("imagem", resposta.json["campos"])

    def test_rejeita_imagem_maior_que_limite(self):
        imagem_png = b"\x89PNG\r\n\x1a\n" + b"x" * (5 * 1024 * 1024)
        resposta = self.client.post(
            "/api/uploads/produtos",
            data={"imagem": (io.BytesIO(imagem_png), "produto.png")},
            content_type="multipart/form-data",
        )

        self.assertEqual(resposta.status_code, 413)
        self.assertEqual(list(Path(self.pasta_temporaria.name).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
