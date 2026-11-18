"""Atalhos locais de desenvolvimento para Windows, macOS e Linux."""

from datetime import datetime
from pathlib import Path
import os
import secrets
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
APP_PORT = 5000
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


def gerar_senha_admin():
    """Senha de demonstração que atende à regra do sistema (letra e número)."""
    return "Cantina-" + secrets.token_hex(3)


def completar_env():
    """Acrescenta ao .env as chaves novas do .env.example, sem mexer nas preenchidas."""
    atuais = read_env_file()
    exemplo = {}
    for line in ENV_EXAMPLE.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            exemplo[key.strip()] = value.strip()
    geradas = {
        "SECRET_KEY": lambda: secrets.token_hex(32),
        "ADMIN_SENHA": gerar_senha_admin,
        "CLIENTE_SENHA": gerar_senha_admin,
    }
    novas = []
    for key, value in exemplo.items():
        if atuais.get(key):
            continue
        if key in geradas:
            value = geradas[key]()
        if key in atuais:
            # A chave existe, mas está vazia: só preenche as que o sistema gera.
            if key not in geradas:
                continue
            linhas = [
                f"{key}={value}" if linha.strip().startswith(key + "=") else linha
                for linha in ENV_FILE.read_text(encoding="utf-8-sig").splitlines()
            ]
            ENV_FILE.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        else:
            novas.append(f"{key}={value}")
    if novas:
        with ENV_FILE.open("a", encoding="utf-8") as arquivo:
            arquivo.write(
                "\n# Acrescentado automaticamente a partir de .env.example\n"
                + "\n".join(novas)
                + "\n"
            )
        print("Seu .env recebeu as chaves novas: " + ", ".join(n.split("=", 1)[0] for n in novas))


def ensure_env_file():
    if not ENV_FILE.exists():
        shutil.copyfile(ENV_EXAMPLE, ENV_FILE)
        print("Arquivo .env criado a partir de .env.example.")
    completar_env()
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
    # O texto muda entre versões do Docker ("No such object" ou "no such object").
    return "no such object" in result.stderr.lower()


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
        if port_is_open(int(port)):
            raise RuntimeError(
                f"A porta {port} já está em uso por outro programa (talvez um MySQL instalado "
                "no computador). Mude MYSQL_PORT no .env para 3307 e rode o comando de novo."
            )
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

    # Na primeira inicialização o MySQL sobe um servidor temporário que ainda não
    # tem a senha root definida; "Access denied" nesse período é normal. Só é
    # tratado como senha errada se continuar acontecendo depois de alguns segundos.
    deadline = time.monotonic() + MAX_MYSQL_WAIT_SECONDS
    acesso_negado_desde = None
    while time.monotonic() < deadline:
        try:
            if docker_mysql("SELECT 1;", values) == "1":
                print("MySQL pronto.")
                return
            acesso_negado_desde = None
        except RuntimeError as error:
            if "Access denied" in str(error) or "ERROR 1045" in str(error):
                acesso_negado_desde = acesso_negado_desde or time.monotonic()
                if time.monotonic() - acesso_negado_desde > 40:
                    raise RuntimeError(
                        "Senha root incorreta. Confira MYSQL_ROOT_PASSWORD no .env com a senha "
                        "configurada no container."
                    ) from error
            else:
                acesso_negado_desde = None
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

    colunas = docker_mysql(
        """SELECT
          (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA = 'cantina_inteligente' AND TABLE_NAME = 'produtos'
             AND COLUMN_NAME = 'codigo_produto'),
          (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA = 'cantina_inteligente' AND TABLE_NAME = 'produtos'
             AND COLUMN_NAME = 'preco_compra_centavos');""",
        values,
    ).split("\t")
    tem_codigo, tem_preco_compra = (int(valor) > 0 for valor in colunas)
    if tem_codigo and not tem_preco_compra:
        sql = (migrations / "005_produto_av05_mysql.sql").read_text(encoding="utf-8-sig")
        docker_mysql(sql, values)
        print("Migração conferida: 005_produto_av05_mysql.sql")
    elif not tem_codigo and tem_preco_compra:
        print("Migração 005 já aplicada.")
    else:
        raise RuntimeError(
            "A tabela produtos está parcialmente migrada. Confira as colunas antes de continuar."
        )

    # A 006 usa CREATE TABLE IF NOT EXISTS: pode ser aplicada sempre.
    nome_006 = "006_usuarios_carteira_compras_mysql.sql"
    docker_mysql((migrations / nome_006).read_text(encoding="utf-8-sig"), values)
    print(f"Migração conferida: {nome_006}")


def seed():
    values = ensure_database()
    total = int(docker_mysql("SELECT COUNT(*) FROM cantina_inteligente.produtos;", values) or 0)
    if total:
        print(f"O banco já tem {total} produto(s); nenhum dado de exemplo foi inserido.")
        return
    sql = (ROOT / "database" / "seeds" / "produtos_exemplo.sql").read_text(encoding="utf-8-sig")
    docker_mysql(sql, values)
    print("Produtos de exemplo inseridos.")


def ensure_database():
    values = ensure_env_file()
    start_database(values)
    apply_migrations(values)
    return values


def servidor():
    python = python_venv()
    if not python.exists():
        raise RuntimeError("Ambiente Python ausente. Rode make setup primeiro.")
    host = read_env_file().get("APP_HOST") or "127.0.0.1"
    return [
        str(python), "-m", "flask", "--app", "src.backend.app", "run",
        "--debug", "--no-reload", "--host", host, "--port", str(APP_PORT),
    ]


def port_is_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except OSError:
        return False


def run_services():
    """Sobe o banco, aplica as migrações e inicia o Flask (telas + API na mesma porta)."""
    ensure_database()
    base = f"http://127.0.0.1:{APP_PORT}"
    if port_is_open(APP_PORT):
        print(f"O sistema já está rodando em {base}.")
        return
    process = subprocess.Popen(servidor(), cwd=ROOT)
    print(f"Sistema:        {base}/")
    print(f"Catálogo:       {base}/html/catalogo_produtos.html")
    print(f"Administração:  {base}/html/catalogo_produtos_adm.html")
    print(f"Teste do banco: {base}/api/health/db")
    print("Pressione Ctrl+C para parar. O MySQL continuará ligado (use make down para parar).")
    try:
        while process.poll() is None:
            time.sleep(0.5)
        raise RuntimeError(f"O servidor encerrou com código {process.returncode}.")
    except KeyboardInterrupt:
        print("\nEncerrando o servidor...")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


def criar_admin():
    ensure_database()
    python = python_venv()
    if not python.exists():
        raise RuntimeError("Ambiente Python ausente. Rode make setup primeiro.")
    run([str(python), "scripts/criar_admin.py"])


def demo():
    """Produtos de exemplo + administrador + cliente com crédito, para testar e apresentar."""
    seed()
    python = python_venv()
    if not python.exists():
        raise RuntimeError("Ambiente Python ausente. Rode make setup primeiro.")
    run([str(python), "scripts/criar_demo.py"])


def credenciais():
    """Mostra os dados de acesso de demonstração guardados no .env deste computador."""
    values = ensure_env_file()
    print("Credenciais de demonstração (ficam só no seu .env; crie os usuários com make demo)")
    for titulo, prefixo in (("Administrador", "ADMIN"), ("Cliente", "CLIENTE")):
        print(f"\n{titulo}")
        print(f"  matrícula: {values.get(prefixo + '_MATRICULA', '')}")
        print(f"  e-mail:    {values.get(prefixo + '_EMAIL', '')}")
        print(f"  CPF:       {values.get(prefixo + '_CPF', '')}")
        print(f"  senha:     {values.get(prefixo + '_SENHA', '')}")
    print("\nO login aceita matrícula, e-mail ou CPF.")


def backup():
    """Grava uma cópia completa do banco em backups/ (RNF de recuperação)."""
    values = ensure_env_file()
    start_database(values)
    root_password = values.get("MYSQL_ROOT_PASSWORD") or values.get("MYSQL_PASSWORD")
    process_env = os.environ.copy()
    process_env["MYSQL_PWD"] = root_password
    pasta = ROOT / "backups"
    pasta.mkdir(exist_ok=True)
    arquivo = pasta / f"cantina-{datetime.now():%Y%m%d-%H%M%S}.sql"
    resultado = subprocess.run(
        [
            "docker", "exec", "-e", "MYSQL_PWD", DB_CONTAINER, "mysqldump",
            "--default-character-set=utf8mb4", "--single-transaction", "--no-tablespaces",
            "-u", "root", values["MYSQL_DATABASE"],
        ],
        cwd=ROOT, capture_output=True, env=process_env,
    )
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr.decode("utf-8", "replace").strip() or "Falha no backup.")
    arquivo.write_bytes(resultado.stdout)
    print(f"Backup gravado em {arquivo.relative_to(ROOT)} ({len(resultado.stdout) // 1024} KB).")


def restore():
    """Restaura o banco a partir de um arquivo de backups/. Substitui os dados atuais."""
    if len(sys.argv) < 3 or not sys.argv[2].strip():
        raise RuntimeError("Informe o arquivo: make restore ARQUIVO=backups/cantina-AAAAMMDD-HHMMSS.sql")
    arquivo = (ROOT / sys.argv[2]).resolve()
    if not arquivo.is_file():
        raise RuntimeError(f"Arquivo não encontrado: {sys.argv[2]}")
    values = ensure_env_file()
    start_database(values)
    sql = f"USE {values['MYSQL_DATABASE']};\n" + arquivo.read_text(encoding="utf-8")
    docker_mysql(sql, values)
    print(f"Banco restaurado a partir de {arquivo.name}.")


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
    estado = "rodando" if port_is_open(APP_PORT) else "parado"
    print(f"Sistema (Flask): {estado}.")


def test():
    python = python_venv()
    if not python.exists():
        raise RuntimeError("Ambiente Python ausente. Rode make setup primeiro.")
    run([str(python), "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-v"])


def print_help():
    print("Cantina Inteligente — atalhos de desenvolvimento")
    print("  make setup    cria/completa o .env e prepara o ambiente Python")
    print("  make up       inicia o MySQL, aplica migrações e sobe o sistema em http://127.0.0.1:5000")
    print("  make admin    cria (ou redefine) o administrador com os dados ADMIN_* do .env")
    print("  make demo     produtos de exemplo + administrador + cliente com crédito")
    print("  make credenciais  mostra matrícula e senha dos usuários de demonstração")
    print("  make seed     insere produtos de exemplo se a tabela estiver vazia")
    print("  make backup   grava uma cópia do banco em backups/")
    print("  make restore ARQUIVO=backups/arquivo.sql  restaura uma cópia")
    print("  make migrate  aplica migrações MySQL pendentes")
    print("  make test     executa os testes automatizados")
    print("  make status   mostra o que está rodando")
    print("  make down     para o MySQL sem apagar os dados")
    print("  make db-up    inicia somente o MySQL")


def main():
    # Mostra as mensagens na ordem certa mesmo quando a saída vai para outro programa.
    sys.stdout.reconfigure(line_buffering=True)
    actions = {
        "help": print_help,
        "setup": setup,
        "up": run_services,
        "db-up": lambda: start_database(ensure_env_file()),
        "db-down": database_down,
        "migrate": ensure_database,
        "seed": seed,
        "api": run_services,
        "admin": criar_admin,
        "demo": demo,
        "credenciais": credenciais,
        "backup": backup,
        "restore": restore,
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
