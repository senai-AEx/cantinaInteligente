"""Mostra a matrícula, o e-mail, o CPF e a senha dos usuários de demonstração.

Uso: python scripts/credenciais.py
Os dados vêm do arquivo .env deste computador; não são guardados em nenhum outro lugar.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ambiente import ler_env  # noqa: E402


def main() -> int:
    env = ler_env()
    print("Dados de demonstração (ficam só no seu .env):")
    for titulo, prefixo in (("Administrador", "ADMIN"), ("Cliente", "CLIENTE")):
        print(f"\n{titulo}")
        print(f"  matrícula: {env.get(prefixo + '_MATRICULA', '')}")
        print(f"  e-mail:    {env.get(prefixo + '_EMAIL', '')}")
        print(f"  CPF:       {env.get(prefixo + '_CPF', '')}")
        print(f"  senha:     {env.get(prefixo + '_SENHA', '')}")
    print("\nO login aceita matrícula, e-mail ou CPF.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
