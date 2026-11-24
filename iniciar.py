"""Liga a Cantina Inteligente:

    python iniciar.py                    liga o sistema e abre o navegador
    python iniciar.py --sem-navegador    liga sem abrir o navegador

Antes de ligar, confere a conexão com o MySQL e aplica as migrações que faltam.
Para parar, aperte Ctrl+C. O MySQL continua ligado.
"""
import argparse
import sys
import threading
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(RAIZ))

from _ambiente import garantir_venv, ler_env  # noqa: E402

garantir_venv()

import banco  # noqa: E402

PORTA = 5000


def main() -> int:
    parser = argparse.ArgumentParser(description="Liga a Cantina Inteligente.")
    parser.add_argument("--sem-navegador", action="store_true", help="não abre o navegador")
    args = parser.parse_args()

    host = ler_env().get("APP_HOST") or "127.0.0.1"
    try:
        versao = banco.testar()
        banco.aplicar_migracoes()
    except banco.ErroBanco as erro:
        print(f"\nERRO: {erro}", file=sys.stderr)
        return 1
    print(f"Banco conectado (MySQL {versao}).")

    from src.backend.app import app

    inicio = f"http://127.0.0.1:{PORTA}/"
    print("\nSistema ligado!")
    print(f"  Início:          {inicio}")
    print(f"  Catálogo:        {inicio}html/catalogo_produtos.html")
    print(f"  Administração:   {inicio}html/catalogo_produtos_adm.html")
    print("\nPara parar, aperte Ctrl+C.\n")

    if not args.sem_navegador:
        threading.Timer(1.5, webbrowser.open, args=[inicio]).start()

    try:
        app.run(host=host, port=PORTA, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nSistema desligado. O MySQL continua ligado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
