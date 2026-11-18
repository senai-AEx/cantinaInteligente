"""Prepara os usuários de demonstração com os dados do .env.

Uso: `make demo`. Cria (ou redefine) o administrador (ADMIN_*) e um cliente
(CLIENTE_*) e dá ao cliente um crédito inicial de R$ 50,00 para ele já poder
comprar na apresentação. Pode rodar mais de uma vez: o crédito não é repetido.
As senhas nunca são mostradas aqui; use `make credenciais`.
"""
import os
from pathlib import Path
import sys
import uuid

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(RAIZ / ".env")

from src.backend.carteira import service as carteira_service  # noqa: E402
from src.backend.erros import ErroValidacao  # noqa: E402
from src.backend.usuarios import service as usuario_service  # noqa: E402

CREDITO_INICIAL_CENTAVOS = 5000
CAMPOS = ("nome", "matricula", "cpf", "email", "senha")


def ler(prefixo):
    dados = {campo: os.getenv(f"{prefixo}_{campo.upper()}", "").strip() for campo in CAMPOS}
    faltando = [f"{prefixo}_{campo.upper()}" for campo, valor in dados.items() if not valor]
    if faltando:
        raise SystemExit("Preencha no .env (ou rode make setup): " + ", ".join(faltando))
    return dados


def garantir(prefixo, perfil):
    try:
        usuario, criado = usuario_service.garantir_usuario(ler(prefixo), perfil)
    except ErroValidacao as erro:
        for campo, mensagem in (erro.campos or {}).items():
            print(f"{prefixo}_{campo.upper()}: {mensagem}", file=sys.stderr)
        raise SystemExit(1)
    acao = "criado" if criado else "atualizado"
    print(f"{perfil.capitalize()} {acao}: {usuario['nome']} — matrícula {usuario['matricula']}.")
    return usuario


def main():
    garantir("ADMIN", "ADMINISTRADOR")
    cliente = garantir("CLIENTE", "CLIENTE")
    # Chave fixa por usuário: rodar de novo devolve o mesmo crédito, sem duplicar.
    chave = str(uuid.uuid5(uuid.NAMESPACE_URL, f"cantina-demo-credito-{cliente['id_usuario']}"))
    _, carteira, criado = carteira_service.adicionar_credito(
        cliente, {"valor_centavos": CREDITO_INICIAL_CENTAVOS, "chave_idempotencia": chave}
    )
    if criado:
        print("Crédito inicial de R$ 50,00 lançado para o cliente de demonstração.")
    print(f"Saldo do cliente: R$ {carteira['saldo_centavos'] / 100:.2f}".replace(".", ","))
    print("Para ver matrícula e senha de cada um: make credenciais")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
