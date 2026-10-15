"""Atalhos locais de desenvolvimento para Windows, macOS e Linux."""

from pathlib import Path
import os
import shutil
import socket
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"
DB_CONTAINER = "cantina-mysql"
DB_IMAGE = "mysql:8.4"
DB_VOLUME = "cantina-mysql-data"
API_PORT = 5000
WEB_PORT = 5500
MAX_MYSQL_WAIT_SECONDS = 90


def read_env_file():
    values = {}
    if not ENV_FILE.exists():
        return values
    for line in ENV_FILE.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def ensure_env_file():
    if not ENV_FILE.exists():
        shutil.copyfile(ENV_EXAMPLE, ENV_FILE)
        print("Arquivo .env criado a partir de .env.example.")
    values = read_env_file()
    required = ("MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD")
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise RuntimeError("Preencha no .env: " + ", ".join(missing))
    if values["MYSQL_DATABASE"] != "cantina_inteligente":
        raise RuntimeError("MYSQL_DATABASE deve ser cantina_inteligente para corresponder às migrações do projeto.")
    try:
        port = int(values.get("MYSQL_PORT", "3306"))
    except ValueError as exc:
        raise RuntimeError("MYSQL_PORT precisa ser um número inteiro.") from exc
    if not 1 <= port <= 65535:
        raise RuntimeError("MYSQL_PORT precisa estar entre 1 e 65535.")
    return values


def python_venv():
    if os.name == "nt":
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def run(command, *, check=True, capture=False, input_text=None, env=None):
    return subprocess.run(
        command,
        cwd=ROOT,
        check=check,
        text=True,
        input=input_text,
        capture_output=capture,
        env=env,
    )


def docker_inspect():
    return run(
        ["docker", "inspect", "--format", "{{.State.Running}}", DB_CONTAINER],
        check=False,
        capture=True,
    )


def container_not_found(result):
    return "No such object" in result.stderr


def docker_mysql(sql, values, *, capture=False):
    root_password = values.get("MYSQL_ROOT_PASSWORD") or values.get("MYSQL_PASSWORD")
    if not root_password:
        raise RuntimeError(
            "Configure MYSQL_ROOT_PASSWORD no .env. Se o container já existe, use a senha root dele."
        )
    process_env = os.environ.copy()
    process_env["MYSQL_PWD"] = root_password
    result = run(
        [
            "docker", "exec", "-i", "-e", "MYSQL_PWD", DB_CONTAINER,
            "mysql", "--default-character-set=utf8mb4", "--batch", "--skip-column-names", "-u", "root",
        ],
        check=False,
        capture=True,
        input_text=sql,
        env=process_env,
    )
    if result.returncode != 0:
        details = result.stderr.strip() or "Não foi possível executar o MySQL no container."
        raise RuntimeError(details)
    return result.stdout.strip()


def start_database(values):
    inspected = docker_inspect()
    if inspected.returncode != 0:
        if not container_not_found(inspected):
            details = inspected.stderr.strip()
            raise RuntimeError(
                "Não consegui acessar o Docker. Abra o Docker Desktop e tente novamente. "
                + details
            )
        root_password = values.get("MYSQL_ROOT_PASSWORD") or values.get("MYSQL_PASSWORD")
        if not root_password:
            raise RuntimeError("Configure MYSQL_ROOT_PASSWORD no .env para criar o MySQL.")
        port = values.get("MYSQL_PORT", "3306")
        command = [
            "docker", "run", "--name", DB_CONTAINER,
            "--publish", f"{port}:3306",
            "--volume", f"{DB_VOLUME}:/var/lib/mysql",
            "--env", f"MYSQL_ROOT_PASSWORD={root_password}",
            "--env", f"MYSQL_DATABASE={values['MYSQL_DATABASE']}",
            "--env", f"MYSQL_USER={values['MYSQL_USER']}",
            "--env", f"MYSQL_PASSWORD={values['MYSQL_PASSWORD']}",
            "--detach", DB_IMAGE,
        ]
        created = run(command, check=False, capture=True)
        if created.returncode != 0:
            raise RuntimeError(created.stderr.strip() or "Falha ao criar o container MySQL.")
        print(f"Container {DB_CONTAINER} criado com volume persistente {DB_VOLUME}.")
    elif inspected.stdout.strip().lower() != "true":
        result = run(["docker", "start", DB_CONTAINER], check=False, capture=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Falha ao iniciar o container MySQL.")
        print(f"Container {DB_CONTAINER} iniciado.")
    else:
        print(f"Container {DB_CONTAINER} já está rodando.")

    deadline = time.monotonic() + MAX_MYSQL_WAIT_SECONDS
    while time.monotonic() < deadline:
        try:
            if docker_mysql("SELECT 1;", values) == "1":
                print("MySQL pronto.")
                return
        except RuntimeError as error:
            if "Access denied" in str(error) or "ERROR 1045" in str(error):
                raise RuntimeError(
                    "Senha root incorreta. Confira MYSQL_ROOT_PASSWORD no .env com a senha configurada no container."
                ) from error
        time.sleep(2)
    raise RuntimeError(
        "O MySQL não ficou pronto. Confira o Docker Desktop e a senha MYSQL_ROOT_PASSWORD do container no .env."
    )


def apply_migrations(values):
    migrations = ROOT / "database" / "migrations"
    for filename in ("002_produtos_mysql.sql", "003_auditoria_produtos_mysql.sql"):
        sql = (migrations / filename).read_text(encoding="utf-8-sig")
        docker_mysql(sql, values)
        print(f"Migração conferida: {filename}")

    migration_004 = migrations / "004_auditoria_exclusao_mysql.sql"
    if not migration_004.exists():
        print("Migração 004 não está nesta branch; exclusão continuará como inativação.")
        return

    estado = docker_mysql(
        """SELECT
          (SELECT COUNT(*) FROM information_schema.REFERENTIAL_CONSTRAINTS
           WHERE CONSTRAINT_SCHEMA = 'cantina_inteligente'
             AND TABLE_NAME = 'auditoria_produtos'
             AND CONSTRAINT_NAME = 'fk_auditoria_produto'),
          (SELECT COLUMN_TYPE FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA = 'cantina_inteligente'
             AND TABLE_NAME = 'auditoria_produtos'
             AND COLUMN_NAME = 'acao');""",
        values,
    )
    partes = estado.split("\t", 1)
    if len(partes) != 2:
        raise RuntimeError("Não consegui conferir o estado da auditoria de produtos.")
    tem_chave_estrangeira = int(partes[0]) > 0
    enum_acao = partes[1]
    if tem_chave_estrangeira and "EXCLUIR" not in enum_acao:
        docker_mysql(migration_004.read_text(encoding="utf-8-sig"), values)
        print("Migração conferida: 004_auditoria_exclusao_mysql.sql")
    elif not tem_chave_estrangeira and "EXCLUIR" in enum_acao:
        print("Migração 004 já aplicada.")
    else:
        raise RuntimeError(
            "A auditoria está parcialmente migrada. Confira a tabela auditoria_produtos antes de continuar."
        )


def ensure_database():
    values = ensure_env_file()
    start_database(values)
    apply_migrations(values)
    return values


def serve_api():
    python = python_venv()
    if not python.exists():
        raise RuntimeError("Ambiente Python ausente. Rode make setup primeiro.")
    return [
        str(python), "-m", "flask", "--app", "src.backend.app", "run",
        "--debug", "--no-reload", "--host", "127.0.0.1", "--port", str(API_PORT),
    ]


def serve_web():
    python = python_venv()
    if not python.exists():
        raise RuntimeError("Ambiente Python ausente. Rode make setup primeiro.")
    frontend = ROOT / "src" / "frontend" / "html"
    if not frontend.is_dir():
        raise RuntimeError("As telas ainda não estão nesta branch; o servidor do frontend foi omitido.")
    return [str(python), "-m", "http.server", str(WEB_PORT), "--bind", "127.0.0.1"]


def port_is_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except OSError:
        return False


def start_process(name, command, port):
    if port_is_open(port):
        print(f"{name} já está disponível em 127.0.0.1:{port}.")
        return None
    process = subprocess.Popen(command, cwd=ROOT)
    print(f"{name} iniciado em 127.0.0.1:{port}.")
    return process


def run_services(include_web=True):
    ensure_database()
    services = [("Flask", serve_api(), API_PORT)]
    frontend_exists = (ROOT / "src" / "frontend" / "html").is_dir()
    if include_web and frontend_exists:
        services.append(("Frontend", serve_web(), WEB_PORT))

    children = []
    try:
        for name, command, port in services:
            process = start_process(name, command, port)
            if process is not None:
                children.append((name, process))
        print(f"API: http://127.0.0.1:{API_PORT}/api/health")
        print(f"Banco: http://127.0.0.1:{API_PORT}/api/health/db")
        if frontend_exists and include_web:
            print(f"Admin: http://127.0.0.1:{WEB_PORT}/src/frontend/html/catalogo_produtos_adm.html")
            print(f"Catálogo: http://127.0.0.1:{WEB_PORT}/src/frontend/html/catalogo_produtos.html")
        elif include_web:
            print("Telas frontend ainda não existem nesta branch; quando forem integradas, make up também as servirá.")
        print("Pressione Ctrl+C para parar os servidores. O MySQL continuará ligado.")
        while True:
            for name, process in children:
                code = process.poll()
                if code is not None:
                    raise RuntimeError(f"{name} encerrou com código {code}.")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nEncerrando os servidores locais...")
    finally:
        for _, process in children:
            if process.poll() is None:
                process.terminate()
        for _, process in children:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def setup():
    ensure_env_file()
    python = python_venv()
    if not python.exists():
        run([sys.executable, "-m", "venv", str(ROOT / ".venv")])
    run([str(python), "-m", "pip", "install", "-r", "requirements.txt"])
    print("Ambiente pronto. Use make up para iniciar a aplicação.")


def database_down():
    inspected = docker_inspect()
    if inspected.returncode != 0:
        if container_not_found(inspected):
            print(f"Container {DB_CONTAINER} ainda não foi criado.")
        else:
            raise RuntimeError(
                "Não consegui acessar o Docker. Abra o Docker Desktop e tente novamente. "
                + inspected.stderr.strip()
            )
    elif inspected.stdout.strip().lower() == "true":
        result = run(["docker", "stop", DB_CONTAINER], check=False, capture=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Falha ao parar o MySQL.")
        print(f"Container {DB_CONTAINER} parado; os dados foram preservados.")
    else:
        print(f"Container {DB_CONTAINER} já está parado; os dados foram preservados.")


def status():
    inspected = docker_inspect()
    if inspected.returncode != 0:
        if container_not_found(inspected):
            print(f"MySQL: container {DB_CONTAINER} não criado.")
        else:
            raise RuntimeError(
                "Não consegui acessar o Docker. Abra o Docker Desktop e tente novamente. "
                + inspected.stderr.strip()
            )
    else:
        state = "rodando" if inspected.stdout.strip().lower() == "true" else "parado"
        print(f"MySQL: {state}.")
    for name, port in (("Flask", API_PORT), ("Frontend", WEB_PORT)):
        print(f"{name}: {'rodando' if port_is_open(port) else 'parado'}.")


def test():
    python = python_venv()
    if not python.exists():
        raise RuntimeError("Ambiente Python ausente. Rode make setup primeiro.")
    run([str(python), "-m", "unittest", "discover", "-s", "tests", "-v"])


def print_help():
    print("Cantina Inteligente — atalhos de desenvolvimento")
    print("  make setup    cria .env se necessário e prepara o ambiente Python")
    print("  make up       inicia/cria MySQL, aplica migrações e sobe API + frontend disponível")
    print("  make down     para o MySQL sem apagar os dados")
    print("  make db-up    inicia somente o MySQL")
    print("  make db-down  para somente o MySQL")
    print("  make migrate  aplica migrações MySQL pendentes")
    print("  make api      inicia MySQL/migrações e roda somente a API")
    print("  make web      serve as telas em http://127.0.0.1:5500")
    print("  make test     executa os testes automatizados")
    print("  make status   mostra quais serviços estão ativos")


def main():
    actions = {
        "help": print_help,
        "setup": setup,
        "up": run_services,
        "db-up": lambda: start_database(ensure_env_file()),
        "db-down": database_down,
        "migrate": ensure_database,
        "api": lambda: run_services(include_web=False),
        "web": lambda: subprocess.run(serve_web(), cwd=ROOT, check=True),
        "test": test,
        "status": status,
    }
    action = sys.argv[1] if len(sys.argv) > 1 else "help"
    if action not in actions:
        print(f"Comando desconhecido: {action}", file=sys.stderr)
        print_help()
        return 2
    try:
        actions[action]()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
