"""Servidor local que publica somente os arquivos do frontend."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "src" / "frontend"


class FrontendHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        parsed = urlsplit(path)
        prefix = "/assets/produtos/"
        if parsed.path.startswith(prefix):
            relativo = parsed.path[len(prefix):]
            pasta_imagens = ROOT / "assets" / "produtos"
            arquivo = (pasta_imagens / relativo).resolve()
            try:
                arquivo.relative_to(pasta_imagens.resolve())
            except ValueError:
                return str(pasta_imagens / "arquivo-inexistente")
            if not relativo or not arquivo.is_file():
                return str(pasta_imagens / "arquivo-inexistente")
            return str(arquivo)
        return super().translate_path(path)

    def _rewrite_url(self):
        parsed = urlsplit(self.path)
        path = parsed.path
        if path == "/":
            path = "/index.html"
        elif path.startswith("/src/frontend/"):
            path = path[len("/src/frontend"):]
        self.path = path + (f"?{parsed.query}" if parsed.query else "")

    def do_GET(self):
        self._rewrite_url()
        super().do_GET()

    def do_HEAD(self):
        self._rewrite_url()
        super().do_HEAD()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5500
    handler = partial(FrontendHandler, directory=str(FRONTEND))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Frontend disponível em http://127.0.0.1:{port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServidor frontend encerrado.")
