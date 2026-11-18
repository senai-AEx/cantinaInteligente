"""Camada de repositório: todo o SQL de usuários usado no cadastro e no login."""
from ..conexao import conectar, transacao  # noqa: F401  (transacao é usada pelo service)
from ..http import data_utc

ID_TIPO = {"ADMINISTRADOR": 1, "CLIENTE": 2}

# Usuário + perfil + saldo da carteira. Nunca inclui o hash da senha.
SELECT_USUARIO = """
    SELECT u.id_usuario, u.nome, u.matricula, u.cpf, u.email,
           t.nome AS perfil, u.status,
           COALESCE(c.saldo_centavos, 0) AS saldo_centavos, u.criado_em
    FROM usuarios u
    JOIN tipos_usuario t ON t.id_tipo_usuario = u.id_tipo_usuario
    LEFT JOIN carteiras c ON c.id_usuario = u.id_usuario
"""


def _fechar(connection, cursor):
    if cursor is not None:
        cursor.close()
    if connection is not None and connection.is_connected():
        connection.close()


def _linha(row):
    if row is None:
        return None
    usuario = dict(row)
    usuario["saldo_centavos"] = int(usuario.get("saldo_centavos") or 0)
    usuario["criado_em"] = data_utc(usuario.get("criado_em"))
    return usuario


def mascarar_cpf(cpf):
    """123.456.789-09 vira ***.456.789-**: identifica sem expor o documento."""
    if not cpf or len(cpf) != 11:
        return ""
    return f"***.{cpf[3:6]}.{cpf[6:9]}-**"


def usuario_json(usuario):
    """Objeto público enviado à tela: sem senha e sem o CPF completo."""
    if usuario is None:
        return None
    return {
        "id_usuario": usuario["id_usuario"],
        "nome": usuario["nome"],
        "matricula": usuario["matricula"],
        "email": usuario["email"],
        "cpf_mascarado": mascarar_cpf(usuario.get("cpf")),
        "perfil": usuario["perfil"],
        "status": usuario["status"],
        "saldo_centavos": int(usuario.get("saldo_centavos") or 0),
        "criado_em": data_utc(usuario.get("criado_em")),
    }


# ---------- consultas com conexão própria ----------

def buscar_por_id(id_usuario):
    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(SELECT_USUARIO + " WHERE u.id_usuario = %s", (id_usuario,))
        return _linha(cursor.fetchone())
    finally:
        _fechar(connection, cursor)


def buscar_credenciais(email, digitos):
    """Candidatos ao login: quem tem este e-mail, esta matrícula ou este CPF.

    Devolve [(id_usuario, senha_hash, status)]. Normalmente uma linha só; pode
    haver duas se a matrícula de alguém coincidir com o CPF de outra pessoa.
    """
    condicoes = []
    params = []
    if email:
        condicoes.append("email = %s")
        params.append(email)
    if digitos:
        condicoes.append("matricula = %s")
        params.append(digitos)
        if len(digitos) == 11:
            condicoes.append("cpf = %s")
            params.append(digitos)
    if not condicoes:
        return []

    connection = cursor = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, senha_hash, status FROM usuarios WHERE "
            + " OR ".join(condicoes)
            + " ORDER BY id_usuario LIMIT 3",
            params,
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        _fechar(connection, cursor)


# ---------- operações dentro de uma transação (recebem o cursor) ----------

def carregar(cursor, id_usuario):
    cursor.execute(SELECT_USUARIO + " WHERE u.id_usuario = %s", (id_usuario,))
    return _linha(cursor.fetchone())


def inserir(cursor, dados, senha_hash, perfil="CLIENTE"):
    cursor.execute(
        """INSERT INTO usuarios (nome, matricula, cpf, email, senha_hash, id_tipo_usuario)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (
            dados["nome"],
            dados["matricula"],
            dados["cpf"],
            dados["email"],
            senha_hash,
            ID_TIPO[perfil],
        ),
    )
    return cursor.lastrowid


def criar_carteira(cursor, id_usuario):
    cursor.execute(
        "INSERT IGNORE INTO carteiras (id_usuario, saldo_centavos) VALUES (%s, 0)",
        (id_usuario,),
    )


def buscar_id_por_matricula(cursor, matricula):
    cursor.execute("SELECT id_usuario FROM usuarios WHERE matricula = %s", (matricula,))
    row = cursor.fetchone()
    return row["id_usuario"] if row else None


def atualizar_acesso(cursor, id_usuario, senha_hash, perfil):
    """Redefine senha e perfil e reativa o usuário (usado pelo `make admin`)."""
    cursor.execute(
        """UPDATE usuarios
           SET senha_hash = %s, id_tipo_usuario = %s, status = 'ATIVO'
           WHERE id_usuario = %s""",
        (senha_hash, ID_TIPO[perfil], id_usuario),
    )


def buscar_senha_hash(cursor, id_usuario, bloquear=False):
    """Hash da senha do usuário, ou None se ele não existir."""
    sql = "SELECT senha_hash FROM usuarios WHERE id_usuario = %s"
    if bloquear:
        sql += " FOR UPDATE"
    cursor.execute(sql, (id_usuario,))
    row = cursor.fetchone()
    return row["senha_hash"] if row else None


def atualizar_senha(cursor, id_usuario, senha_hash):
    cursor.execute(
        "UPDATE usuarios SET senha_hash = %s WHERE id_usuario = %s",
        (senha_hash, id_usuario),
    )
