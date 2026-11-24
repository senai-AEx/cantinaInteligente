"""Instalação da Cantina Inteligente. Rode uma vez, no seu computador:

    python instalar.py

Ele faz tudo sozinho, na ordem:
  1. prepara o arquivo de configuração (.env), gerando as senhas que faltam;
  2. cria o ambiente Python (.venv) e instala as bibliotecas;
  3. cria o banco de dados e as tabelas (pede a senha do MySQL);
  4. cria os usuários de demonstração.

Pode rodar de novo quando quiser: o que já estiver pronto é conferido e mantido.
Pré-requisito: o MySQL 8 instalado e ligado. Não precisa de Docker nem de Make.
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "scripts"))

from _ambiente import VENV, completar_env, python_do_venv  # noqa: E402


def passo(texto: str) -> None:
    print(f"\n==> {texto}")


def main() -> int:
    if sys.version_info < (3, 10):
        print(f"Este projeto precisa de Python 3.10 ou mais novo. Você usou a versão {sys.version.split()[0]}.")
        print("Instale uma versão mais nova em python.org e rode de novo.")
        return 1

    print("Instalação da Cantina Inteligente")

    passo("1/4  Arquivo de configuração (.env)")
    preenchidas = completar_env()
    if preenchidas:
        print(f"  Gerei os valores que faltavam: {', '.join(preenchidas)}.")
    else:
        print("  O .env já está completo.")

    passo("2/4  Ambiente Python e bibliotecas")
    if not python_do_venv().exists():
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV)])
    py = str(python_do_venv())
    subprocess.check_call(
        [py, "-m", "pip", "install", "--disable-pip-version-check", "-q", "-r", str(RAIZ / "requirements.txt")]
    )
    print("  Bibliotecas instaladas.")

    passo("3/4  Banco de dados MySQL")
    if subprocess.call([py, str(RAIZ / "scripts" / "banco.py"), "instalar"]) != 0:
        print("\nA instalação parou no banco de dados. Corrija a mensagem acima e rode: python instalar.py")
        return 1

    passo("4/4  Usuários de demonstração")
    if subprocess.call([py, str(RAIZ / "scripts" / "criar_demo.py")]) != 0:
        print("\nNão consegui criar os usuários de demonstração. Veja a mensagem acima.")
        return 1

    print("\nTudo pronto!")
    print("Para ligar o sistema, rode:")
    print("    python iniciar.py")
    print("Para ver matrícula e senha dos usuários de demonstração:")
    print("    python scripts/credenciais.py")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInstalação cancelada. Rode python instalar.py de novo quando quiser.")
        raise SystemExit(130)
