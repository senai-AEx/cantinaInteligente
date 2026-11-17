"""Camada de serviço: cadastro de usuário e autenticação.

- A senha é guardada apenas como hash (werkzeug.security); nunca em texto puro.
- O login aceita matrícula, e-mail ou CPF no mesmo campo.
- Todo usuário novo nasce com perfil CLIENTE e uma carteira com saldo zero,
  criados na mesma transação.
"""
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

from ..erros import ErroValidacao, NaoAutenticado, SemPermissao
from . import repository as usuario_repository
from .validacao import somente_digitos, validar_cadastro

MENSAGEM_LOGIN_INVALIDO = "Matrícula, e-mail, CPF ou senha incorretos."

# Nome da restrição UNIQUE do banco -> campo e mensagem mostrados na tela.
DUPLICIDADES = {
    "uq_usuarios_matricula": ("matricula", "Já existe um cadastro com esta matrícula."),
    "uq_usuarios_cpf": ("cpf", "Já existe um cadastro com este CPF."),
    "uq_usuarios_email": ("email", "Já existe um cadastro com este e-mail."),
}

# Hash usado quando o identificador não existe, para o tempo de resposta do
# login não revelar se a matrícula/e-mail/CPF está cadastrado.
_HASH_FALSO = generate_password_hash("senha-inexistente")


def erro_de_duplicidade(exc):
    """Converte o erro 1062 do MySQL em ErroValidacao no campo certo, ou None."""
    if getattr(exc, "errno", None) != 1062:
        return None
    mensagem = str(exc)
    for restricao, (campo, texto) in DUPLICIDADES.items():
        if restricao in mensagem:
            return ErroValidacao({campo: texto})
    return ErroValidacao({"_geral": "Já existe um cadastro com estes dados."})


def cadastrar(payload, perfil="CLIENTE"):
    dados, erros = validar_cadastro(payload)
    if erros:
        raise ErroValidacao(erros)

    senha_hash = generate_password_hash(dados["senha"])
    try:
        with usuario_repository.transacao() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                id_usuario = usuario_repository.inserir(cursor, dados, senha_hash, perfil)
                usuario_repository.criar_carteira(cursor, id_usuario)
                usuario = usuario_repository.carregar(cursor, id_usuario)
            finally:
                cursor.close()
    except mysql.connector.Error as exc:
        duplicidade = erro_de_duplicidade(exc)
        if duplicidade:
            raise duplicidade from exc
        raise
    return usuario


def autenticar(payload):
    identificador = payload.get("identificador") if isinstance(payload, dict) else None
    senha = payload.get("senha") if isinstance(payload, dict) else None

    erros = {}
    if not isinstance(identificador, str) or not identificador.strip():
        erros["identificador"] = "Informe sua matrícula, e-mail ou CPF."
    if not isinstance(senha, str) or not senha:
        erros["senha"] = "Informe a senha."
    if erros:
        raise ErroValidacao(erros)

    identificador = identificador.strip()
    if "@" in identificador:
        email, digitos = identificador.lower()[:150], ""
    else:
        email, digitos = "", somente_digitos(identificador)[:20]

    candidatos = usuario_repository.buscar_credenciais(email, digitos)
    encontrado = None
    for candidato in candidatos:
        if check_password_hash(candidato["senha_hash"], senha):
            encontrado = candidato
            break
    if encontrado is None:
        if not candidatos:
            check_password_hash(_HASH_FALSO, senha)
        raise NaoAutenticado(MENSAGEM_LOGIN_INVALIDO)

    if encontrado["status"] != "ATIVO":
        raise SemPermissao("Este cadastro está inativo. Procure a administração da cantina.")

    return usuario_repository.buscar_por_id(encontrado["id_usuario"])


def garantir_administrador(dados):
    """Cria o administrador ou, se a matrícula já existir, redefine senha e perfil.

    Usado pelo comando `make admin`. Devolve (usuario, criado).
    """
    dados_validos, erros = validar_cadastro({**dados, "confirmar_senha": dados.get("senha")})
    if erros:
        raise ErroValidacao(erros)

    senha_hash = generate_password_hash(dados_validos["senha"])
    try:
        with usuario_repository.transacao() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                id_usuario = usuario_repository.buscar_id_por_matricula(
                    cursor, dados_validos["matricula"]
                )
                criado = id_usuario is None
                if criado:
                    id_usuario = usuario_repository.inserir(
                        cursor, dados_validos, senha_hash, "ADMINISTRADOR"
                    )
                else:
                    usuario_repository.atualizar_acesso(
                        cursor, id_usuario, senha_hash, "ADMINISTRADOR"
                    )
                usuario_repository.criar_carteira(cursor, id_usuario)
                usuario = usuario_repository.carregar(cursor, id_usuario)
            finally:
                cursor.close()
    except mysql.connector.Error as exc:
        duplicidade = erro_de_duplicidade(exc)
        if duplicidade:
            raise duplicidade from exc
        raise
    return usuario, criado
