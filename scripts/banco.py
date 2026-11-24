"""Banco de dados do projeto: instalar, migrar, semear, fazer backup e restaurar.

Não usa Docker. Precisa só de um servidor MySQL 8 instalado e ligado no computador.
Tudo é feito pela biblioteca mysql-connector-python, então não é preciso instalar
o programa de linha de comando "mysql".

Uso (de qualquer pasta):
    python scripts/banco.py instalar     cria o banco, o usuário do sistema e as tabelas
    python scripts/banco.py migrar       aplica só as migrações que faltam
    python scripts/banco.py semear       insere os produtos de exemplo (se a tabela estiver vazia)
    python scripts/banco.py testar       confere se o sistema consegue falar com o banco
    python scripts/banco.py backup       grava uma cópia em backups/
    python scripts/banco.py restaurar ARQUIVO
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import getpass
import os
import re
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _ambiente import RAIZ, garantir_venv, ler_env  # noqa: E402

garantir_venv()

import mysql.connector  # noqa: E402
from mysql.connector.conversion import MySQLConverter  # noqa: E402

PASTA_MIGRACOES = RAIZ / "database" / "migrations"
ARQUIVO_SEMENTE = RAIZ / "database" / "seeds" / "produtos_exemplo.sql"
PASTA_BACKUPS = RAIZ / "backups"
MIGRACOES = [
    "002_produtos_mysql.sql",
    "003_auditoria_produtos_mysql.sql",
    "004_auditoria_exclusao_mysql.sql",
    "005_produto_av05_mysql.sql",
    "006_usuarios_carteira_compras_mysql.sql",
]
NOME_VALIDO = re.compile(r"^[A-Za-z0-9_]{1,64}$")


class ErroBanco(Exception):
    """Problema com o banco que a pessoa consegue resolver. A mensagem explica o que fazer."""


# ---------- configuração e conexão ----------

def configuracao() -> dict:
    env = ler_env()
    try:
        porta = int(env.get("MYSQL_PORT") or 3306)
    except ValueError as erro:
        raise ErroBanco("MYSQL_PORT no .env precisa ser um número, por exemplo 3306.") from erro
    banco = env.get("MYSQL_DATABASE") or "cantina_inteligente"
    if not NOME_VALIDO.match(banco):
        raise ErroBanco("MYSQL_DATABASE no .env deve ter só letras, números e _.")
    return {
        "host": env.get("MYSQL_HOST") or "127.0.0.1",
        "porta": porta,
        "banco": banco,
        "usuario": env.get("MYSQL_USER") or "cantina_app",
        "senha": env.get("MYSQL_PASSWORD") or "",
        "usuario_root": env.get("MYSQL_ROOT_USER") or "root",
    }


def _traduzir(erro: mysql.connector.Error, cfg: dict, usuario: str) -> ErroBanco:
    codigo = getattr(erro, "errno", None)
    if codigo == 2003:
        return ErroBanco(
            f"Não encontrei o MySQL em {cfg['host']}:{cfg['porta']}.\n"
            "  Confira se o MySQL está instalado e ligado:\n"
            "    Windows: abra 'Serviços' (services.msc) e inicie o serviço MySQL80 (ou MySQL84).\n"
            "    macOS: rode 'brew services start mysql'.\n"
            "    Linux: rode 'sudo systemctl start mysql'.\n"
            "  Se o MySQL usa outra porta, ajuste MYSQL_PORT no .env."
        )
    if codigo == 1045:
        if usuario == cfg["usuario_root"]:
            return ErroBanco(
                "A senha do usuário root do MySQL está errada. Rode 'python instalar.py' de novo "
                "e digite a senha que você criou ao instalar o MySQL."
            )
        return ErroBanco(
            f"O usuário '{usuario}' do sistema não consegue entrar no banco. "
            "Rode 'python instalar.py' para recriar o acesso."
        )
    if codigo == 1049:
        return ErroBanco(f"O banco '{cfg['banco']}' ainda não existe. Rode 'python instalar.py'.")
    return ErroBanco(f"O MySQL respondeu com um erro: {erro.msg}")


def _conectar(usuario: str, senha: str, banco: str | None = None, cfg: dict | None = None):
    cfg = cfg or configuracao()
    parametros = {
        "host": cfg["host"],
        "port": cfg["porta"],
        "user": usuario,
        "password": senha,
        "charset": "utf8mb4",
        "connection_timeout": 5,
        "autocommit": True,
    }
    if banco:
        parametros["database"] = banco
    try:
        return mysql.connector.connect(**parametros)
    except mysql.connector.Error as erro:
        raise _traduzir(erro, cfg, usuario) from erro


def _conectar_app() -> object:
    cfg = configuracao()
    return _conectar(cfg["usuario"], cfg["senha"], cfg["banco"], cfg)


# ---------- execução de arquivos SQL ----------

def separar_instrucoes(sql: str) -> list[str]:
    """Divide um arquivo SQL em instruções.

    Respeita textos entre aspas (um ';' dentro de um texto não encerra a instrução)
    e ignora comentários "-- ..." e "/* ... */".
    """
    instrucoes: list[str] = []
    atual: list[str] = []
    aspas = None
    i = 0
    n = len(sql)
    while i < n:
        c = sql[i]
        if aspas is None and sql.startswith("--", i):
            fim = sql.find("\n", i)
            i = n if fim == -1 else fim
            continue
        if aspas is None and sql.startswith("/*", i):
            fim = sql.find("*/", i + 2)
            i = n if fim == -1 else fim + 2
            continue
        if aspas:
            atual.append(c)
            if c == "\\" and i + 1 < n:
                atual.append(sql[i + 1])
                i += 2
                continue
            if c == aspas:
                aspas = None
        elif c in "'\"`":
            aspas = c
            atual.append(c)
        elif c == ";":
            texto = "".join(atual).strip()
            if texto:
                instrucoes.append(texto)
            atual = []
        else:
            atual.append(c)
        i += 1
    texto = "".join(atual).strip()
    if texto:
        instrucoes.append(texto)
    return instrucoes


def _sem_criacao_de_banco(instrucao: str) -> bool:
    """O usuário do sistema não cria bancos: essas instruções ficam com o instalar."""
    primeira = instrucao.lstrip().upper()
    return primeira.startswith("CREATE DATABASE") or primeira.startswith("USE ")


def executar_sql(cursor, sql: str) -> None:
    for instrucao in separar_instrucoes(sql):
        if _sem_criacao_de_banco(instrucao):
            continue
        cursor.execute(instrucao)
        if cursor.with_rows:
            cursor.fetchall()


def _ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8-sig")


# ---------- instalação ----------

def _criar_banco_e_acesso(conexao, cfg: dict) -> None:
    """Cria o banco e o usuário do sistema. Pode rodar de novo: não quebra se já existirem."""
    banco, usuario, senha = cfg["banco"], cfg["usuario"], cfg["senha"]
    if not senha:
        raise ErroBanco("MYSQL_PASSWORD está vazio no .env. Rode 'python instalar.py' para gerar a senha.")
    cursor = conexao.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{banco}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
    )
    for host in ("localhost", "127.0.0.1"):
        cursor.execute("CREATE USER IF NOT EXISTS %s@%s IDENTIFIED BY %s", (usuario, host, senha))
        cursor.execute("ALTER USER %s@%s IDENTIFIED BY %s", (usuario, host, senha))
        cursor.execute(f"GRANT ALL PRIVILEGES ON `{banco}`.* TO %s@%s", (usuario, host))
    cursor.execute("FLUSH PRIVILEGES")
    cursor.close()


def pedir_senha_root() -> str:
    """Usa MYSQL_ROOT_PASSWORD do .env se existir; senão pergunta, sem mostrar o que foi digitado."""
    senha = ler_env().get("MYSQL_ROOT_PASSWORD")
    if senha:
        return senha
    pergunta = "Senha do usuário 'root' do MySQL (a que você criou ao instalar o MySQL): "
    if not sys.stdin.isatty():
        # Sem terminal (por exemplo, um script): lê a linha da entrada, sem exibir nada.
        return sys.stdin.readline().rstrip("\r\n")
    return getpass.getpass(pergunta)


def verificar_servidor(cfg: dict) -> None:
    """Confere se o MySQL responde na porta antes de pedir qualquer senha."""
    import socket

    try:
        with socket.create_connection((cfg["host"], cfg["porta"]), timeout=3):
            return
    except OSError as erro:
        raise _traduzir(mysql.connector.Error(msg=str(erro), errno=2003), cfg, cfg["usuario_root"]) from erro


def instalar(senha_root: str | None = None) -> None:
    cfg = configuracao()
    verificar_servidor(cfg)
    senha_root = senha_root or pedir_senha_root()
    with contextlib.closing(_conectar(cfg["usuario_root"], senha_root, cfg=cfg)) as conexao:
        _criar_banco_e_acesso(conexao, cfg)
    print(f"  Banco '{cfg['banco']}' e usuário '{cfg['usuario']}' prontos.")
    aplicar_migracoes()
    print("  Tabelas prontas.")
    semear()


# ---------- migrações ----------

def _estado_004(cursor, banco: str) -> bool:
    """True se a migração 004 ainda precisa rodar (chave estrangeira ainda existe)."""
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.REFERENTIAL_CONSTRAINTS "
        "WHERE CONSTRAINT_SCHEMA = %s AND TABLE_NAME = 'auditoria_produtos' "
        "AND CONSTRAINT_NAME = 'fk_auditoria_produto'",
        (banco,),
    )
    tem_fk = cursor.fetchone()[0] > 0
    cursor.execute(
        "SELECT COLUMN_TYPE FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'auditoria_produtos' AND COLUMN_NAME = 'acao'",
        (banco,),
    )
    linha = cursor.fetchone()
    tem_excluir = bool(linha) and "EXCLUIR" in linha[0]
    if tem_fk and not tem_excluir:
        return True
    if not tem_fk and tem_excluir:
        return False
    raise ErroBanco("A tabela de auditoria está parcialmente migrada. Fale com o grupo antes de continuar.")


def _estado_005(cursor, banco: str) -> bool:
    """True se a migração 005 ainda precisa rodar (coluna codigo_produto ainda existe)."""
    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'produtos' "
        "AND COLUMN_NAME IN ('codigo_produto', 'preco_compra_centavos')",
        (banco,),
    )
    colunas = {linha[0] for linha in cursor.fetchall()}
    if "codigo_produto" in colunas and "preco_compra_centavos" not in colunas:
        return True
    if "codigo_produto" not in colunas and "preco_compra_centavos" in colunas:
        return False
    raise ErroBanco("A tabela de produtos está parcialmente migrada. Fale com o grupo antes de continuar.")


def aplicar_migracoes() -> list[str]:
    """Aplica as migrações que faltam, na ordem. Pode rodar sempre: o que já existe é pulado."""
    cfg = configuracao()
    aplicadas: list[str] = []
    conexao = _conectar_app()
    try:
        cursor = conexao.cursor()
        for nome in MIGRACOES:
            if nome == "004_auditoria_exclusao_mysql.sql" and not _estado_004(cursor, cfg["banco"]):
                continue
            if nome == "005_produto_av05_mysql.sql" and not _estado_005(cursor, cfg["banco"]):
                continue
            executar_sql(cursor, _ler(PASTA_MIGRACOES / nome))
            aplicadas.append(nome)
        cursor.close()
    finally:
        conexao.close()
    return aplicadas


def migrar() -> None:
    aplicadas = aplicar_migracoes()
    if aplicadas:
        print("Migrações aplicadas: " + ", ".join(aplicadas))
    else:
        print("Nenhuma migração pendente.")


# ---------- produtos de exemplo ----------

def semear() -> None:
    conexao = _conectar_app()
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total = cursor.fetchone()[0]
        cursor.close()
        if total:
            print(f"  O banco já tem {total} produto(s); nenhum exemplo foi inserido.")
            return
        cursor = conexao.cursor()
        executar_sql(cursor, _ler(ARQUIVO_SEMENTE))
        cursor.close()
        print("  Produtos de exemplo inseridos.")
    finally:
        conexao.close()


# ---------- testar ----------

def testar() -> str:
    conexao = _conectar_app()
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT VERSION()")
        versao = cursor.fetchone()[0]
        cursor.close()
        return versao
    finally:
        conexao.close()


# ---------- backup e restauração ----------

_conversor = MySQLConverter()


def _literal(valor) -> str:
    """Escreve um valor do banco como texto de SQL (para o arquivo de backup)."""
    if valor is None:
        return "NULL"
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, (int, float, Decimal)):
        return str(valor)
    if isinstance(valor, dt.datetime):
        return f"'{valor.strftime('%Y-%m-%d %H:%M:%S.%f')}'"
    if isinstance(valor, dt.date):
        return f"'{valor.isoformat()}'"
    if isinstance(valor, (bytes, bytearray)):
        return "X'" + bytes(valor).hex() + "'"
    return "'" + _conversor.escape(str(valor)) + "'"


def fazer_backup() -> Path:
    PASTA_BACKUPS.mkdir(exist_ok=True)
    agora = dt.datetime.now()
    destino = PASTA_BACKUPS / f"cantina-{agora:%Y%m%d-%H%M%S}.sql"
    partes = [f"-- Backup da Cantina Inteligente em {agora:%d/%m/%Y %H:%M}", "SET FOREIGN_KEY_CHECKS = 0;", ""]
    conexao = _conectar_app()
    try:
        cursor = conexao.cursor()
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
        tabelas = [linha[0] for linha in cursor.fetchall()]
        for tabela in tabelas:
            cursor.execute(f"SHOW CREATE TABLE `{tabela}`")
            criacao = cursor.fetchone()[1]
            partes.append(f"DROP TABLE IF EXISTS `{tabela}`;")
            partes.append(criacao + ";")
            cursor.execute(f"SELECT * FROM `{tabela}`")
            colunas = ", ".join(f"`{d[0]}`" for d in cursor.description)
            for linha in cursor.fetchall():
                valores = ", ".join(_literal(v) for v in linha)
                partes.append(f"INSERT INTO `{tabela}` ({colunas}) VALUES ({valores});")
            partes.append("")
        cursor.close()
    finally:
        conexao.close()
    partes.append("SET FOREIGN_KEY_CHECKS = 1;")
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")
    return destino


def restaurar(arquivo: Path) -> None:
    if not arquivo.is_file():
        raise ErroBanco(f"Arquivo não encontrado: {arquivo}")
    print("Isso apaga os dados atuais do banco e volta para a cópia escolhida.")
    if input("Para continuar, digite SIM: ").strip().upper() != "SIM":
        print("Nada foi alterado.")
        return
    conexao = _conectar_app()
    try:
        cursor = conexao.cursor()
        executar_sql(cursor, _ler(arquivo))
        cursor.close()
    finally:
        conexao.close()
    print(f"Banco restaurado a partir de {arquivo.name}.")


# ---------- linha de comando ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Banco de dados da Cantina Inteligente.")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("instalar", help="cria o banco, o usuário do sistema e as tabelas")
    sub.add_parser("migrar", help="aplica as migrações que faltam")
    sub.add_parser("semear", help="insere produtos de exemplo, se a tabela estiver vazia")
    sub.add_parser("testar", help="confere a conexão com o banco")
    sub.add_parser("backup", help="grava uma cópia do banco em backups/")
    restaurar_p = sub.add_parser("restaurar", help="volta o banco para uma cópia")
    restaurar_p.add_argument("arquivo", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.comando == "instalar":
            print("Preparando o banco...")
            instalar()
        elif args.comando == "migrar":
            migrar()
        elif args.comando == "semear":
            semear()
        elif args.comando == "testar":
            print(f"Conexão OK. MySQL versão {testar()}.")
        elif args.comando == "backup":
            print(f"Backup gravado em {fazer_backup().relative_to(RAIZ)}.")
        elif args.comando == "restaurar":
            arquivo = args.arquivo if args.arquivo.is_absolute() else RAIZ / args.arquivo
            restaurar(arquivo)
    except ErroBanco as erro:
        print(f"\nERRO: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
