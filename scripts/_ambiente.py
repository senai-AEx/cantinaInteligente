"""Ajudas comuns dos scripts: entrar no ambiente Python do projeto e cuidar do arquivo .env.

Este arquivo usa só a biblioteca padrão do Python, para funcionar antes de o ambiente
(.venv) existir. Os outros scripts chamam garantir_venv() logo no começo: se foram
chamados com o Python do sistema, eles rodam de novo com o Python do projeto.
Assim, quem digita `python scripts/banco.py` não precisa saber onde está o .venv.
"""
from __future__ import annotations

import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENV = RAIZ / ".env"
EXEMPLO = RAIZ / ".env.example"
VENV = RAIZ / ".venv"


def python_do_venv() -> Path:
    """Caminho do Python dentro do .venv (é diferente no Windows e no macOS/Linux)."""
    if os.name == "nt":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def garantir_venv() -> None:
    """Se o script está rodando com o Python do sistema, roda de novo com o do projeto."""
    if os.environ.get("CANTINA_NO_VENV") == "1":
        return
    py = python_do_venv()
    if not py.exists():
        sys.exit("O ambiente do projeto ainda não existe. Rode primeiro:\n    python instalar.py")
    if os.path.abspath(sys.executable) == os.path.abspath(py):
        return
    env = dict(os.environ, CANTINA_NO_VENV="1")
    try:
        codigo = subprocess.call([str(py), os.path.abspath(sys.argv[0]), *sys.argv[1:]], env=env)
    except KeyboardInterrupt:
        codigo = 130
    sys.exit(codigo)


def ler_env(caminho: Path = ENV) -> dict[str, str]:
    """Lê um arquivo KEY=VALUE (como o .env) e devolve um dicionário."""
    valores: dict[str, str] = {}
    if not caminho.exists():
        return valores
    for linha in caminho.read_text(encoding="utf-8-sig").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        valores[chave.strip()] = valor
    return valores


def gerar_senha_forte() -> str:
    """Senha de demonstração que atende à regra do sistema (letras e números, mais de 8)."""
    return "Cantina-" + secrets.token_hex(3)


# Valores que o instalar gera sozinho quando estão vazios no .env.
GERADOS = {
    "SECRET_KEY": lambda: secrets.token_hex(32),
    "MYSQL_PASSWORD": lambda: secrets.token_urlsafe(16),
    "ADMIN_SENHA": gerar_senha_forte,
    "CLIENTE_SENHA": gerar_senha_forte,
}


def _e_linha_da_chave(linha: str, chave: str) -> bool:
    s = linha.strip()
    return bool(s) and not s.startswith("#") and "=" in s and s.split("=", 1)[0].strip() == chave


def completar_env() -> list[str]:
    """Cria o .env se não existir e preenche o que estiver vazio ou faltando.

    Nunca mexe em valores que você já preencheu. Devolve os nomes das chaves preenchidas.
    """
    if not ENV.exists():
        shutil.copyfile(EXEMPLO, ENV)
    linhas = ENV.read_text(encoding="utf-8-sig").splitlines()
    atuais = ler_env()
    preenchidas: list[str] = []
    novas: list[str] = []
    for chave, valor_exemplo in ler_env(EXEMPLO).items():
        if atuais.get(chave):
            continue
        if chave in atuais and chave not in GERADOS:
            continue
        valor = GERADOS[chave]() if chave in GERADOS else valor_exemplo
        if chave in atuais:
            linhas = [f"{chave}={valor}" if _e_linha_da_chave(l, chave) else l for l in linhas]
        else:
            novas.append(f"{chave}={valor}")
        preenchidas.append(chave)
    if novas:
        linhas += ["", "# Acrescentado automaticamente a partir de .env.example", *novas]
    if preenchidas:
        ENV.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return preenchidas
