"""Camada de serviço: cadastro de usuário e autenticação.

- A senha é guardada apenas como hash (werkzeug.security); nunca em texto puro.
- O login aceita matrícula, e-mail ou CPF no mesmo campo.
- Todo usuário novo nasce com perfil CLIENTE e uma carteira com saldo zero,
  criados na mesma transação.
"""
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

from ..erros import ErroValidacao, NaoAutenticado, NaoEncontrado, SemPermissao
from . import repository as usuario_repository
from .validacao import somente_digitos, validar_cadastro, validar_senha

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

    Usado por `python scripts/criar_admin.py`. Devolve (usuario, criado).
    """
    return garantir_usuario(dados, "ADMINISTRADOR")


def _validar_nova_senha(payload):
    """Valida `nova_senha` e `confirmar_senha`. Devolve (nova_senha, erros)."""
    erros = {}
    nova_senha, erro = validar_senha(payload.get("nova_senha"))
    if erro:
        erros["nova_senha"] = erro
    elif payload.get("confirmar_senha") != nova_senha:
        erros["confirmar_senha"] = "A confirmação não é igual à nova senha."
    return nova_senha, erros


def alterar_senha(usuario, payload):
    """O próprio usuário troca a senha, confirmando a atual."""
    if not isinstance(payload, dict):
        raise ErroValidacao({"_geral": "Envie um objeto JSON."})
    nova_senha, erros = _validar_nova_senha(payload)
    senha_atual = payload.get("senha_atual")
    if not isinstance(senha_atual, str) or not senha_atual:
        erros["senha_atual"] = "Informe a senha atual."
    if erros:
        raise ErroValidacao(erros)

    with usuario_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            hash_atual = usuario_repository.buscar_senha_hash(
                cursor, usuario["id_usuario"], bloquear=True
            )
            if hash_atual is None or not check_password_hash(hash_atual, senha_atual):
                raise ErroValidacao({"senha_atual": "Senha atual incorreta."})
            if check_password_hash(hash_atual, nova_senha):
                raise ErroValidacao({"nova_senha": "A nova senha deve ser diferente da atual."})
            usuario_repository.atualizar_senha(
                cursor, usuario["id_usuario"], generate_password_hash(nova_senha)
            )
        finally:
            cursor.close()


def redefinir_senha(id_usuario, payload):
    """O administrador define uma senha provisória para o usuário. Devolve o usuário."""
    if not isinstance(payload, dict):
        raise ErroValidacao({"_geral": "Envie um objeto JSON."})
    nova_senha, erros = _validar_nova_senha(payload)
    if erros:
        raise ErroValidacao(erros)

    with usuario_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            if usuario_repository.buscar_senha_hash(cursor, id_usuario, bloquear=True) is None:
                raise NaoEncontrado("Usuário não encontrado.")
            usuario_repository.atualizar_senha(
                cursor, id_usuario, generate_password_hash(nova_senha)
            )
            return usuario_repository.carregar(cursor, id_usuario)
        finally:
            cursor.close()


def garantir_usuario(dados, perfil):
    """Cria o usuário de demonstração ou, se a matrícula já existir, redefine a senha.

    Usado por `python scripts/criar_demo.py` para o cliente. Devolve (usuario, criado).
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
                    id_usuario = usuario_repository.inserir(cursor, dados_validos, senha_hash, perfil)
                else:
                    usuario_repository.atualizar_acesso(cursor, id_usuario, senha_hash, perfil)
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
