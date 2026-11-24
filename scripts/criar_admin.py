"""Cria (ou redefine) o administrador de demonstração com os dados do .env.

Uso: python scripts/criar_admin.py Lê ADMIN_NOME, ADMIN_MATRICULA, ADMIN_CPF, ADMIN_EMAIL e
ADMIN_SENHA. Se a matrícula já existir, a senha é redefinida e o usuário volta
a ser administrador ativo. A senha nunca é mostrada na tela.
"""
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))
from _ambiente import garantir_venv  # noqa: E402

garantir_venv()

from dotenv import load_dotenv  # noqa: E402

load_dotenv(RAIZ / ".env")

from src.backend.erros import ErroValidacao  # noqa: E402
from src.backend.usuarios import service as usuario_service  # noqa: E402

CAMPOS = {
    "nome": "ADMIN_NOME",
    "matricula": "ADMIN_MATRICULA",
    "cpf": "ADMIN_CPF",
    "email": "ADMIN_EMAIL",
    "senha": "ADMIN_SENHA",
}


def main():
    dados = {campo: os.getenv(variavel, "").strip() for campo, variavel in CAMPOS.items()}
    faltando = [CAMPOS[campo] for campo, valor in dados.items() if not valor]
    if faltando:
        print("Preencha no .env: " + ", ".join(faltando), file=sys.stderr)
        return 1
    try:
        usuario, criado = usuario_service.garantir_administrador(dados)
    except ErroValidacao as erro:
        for campo, mensagem in (erro.campos or {}).items():
            print(f"{CAMPOS.get(campo, campo)}: {mensagem}", file=sys.stderr)
        if "senha" in (erro.campos or {}):
            print(
                "A senha do administrador precisa ter de 8 a 72 caracteres, com pelo menos "
                "uma letra e um número. Nada foi alterado: a senha anterior continua valendo.",
                file=sys.stderr,
            )
        return 1
    acao = "criado" if criado else "atualizado"
    print(f"Administrador {acao}: {usuario['nome']} — matrícula {usuario['matricula']}.")
    print("A senha é a que está em ADMIN_SENHA no seu arquivo .env.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
