"""Validação dos dados de usuário.

Cada função recebe o valor bruto e devolve (valor_normalizado, mensagem_de_erro).
Quando não há erro, a mensagem é None. As mesmas regras são aplicadas na tela
(src/frontend/javascript/base.js); aqui é a validação que vale.
"""
import re

_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
_TEM_LETRA = re.compile(r"[A-Za-zÀ-ÿ]")
_TEM_NUMERO = re.compile(r"\d")

CAMPOS_CADASTRO = ("nome", "matricula", "cpf", "email", "senha", "confirmar_senha")


def somente_digitos(valor):
    return re.sub(r"\D", "", valor) if isinstance(valor, str) else ""


def validar_nome(valor):
    if not isinstance(valor, str):
        return None, "Informe o nome completo."
    nome = " ".join(valor.split())
    if not 3 <= len(nome) <= 100:
        return None, "Informe o nome com 3 a 100 caracteres."
    if not _TEM_LETRA.search(nome):
        return None, "O nome precisa ter letras."
    return nome, None


def validar_matricula(valor):
    if not isinstance(valor, str):
        return None, "Informe a matrícula."
    matricula = valor.strip()
    if not matricula.isdigit() or not matricula.isascii():
        return None, "A matrícula deve ter apenas números."
    if not 4 <= len(matricula) <= 20:
        return None, "A matrícula deve ter de 4 a 20 dígitos."
    return matricula, None


def cpf_valido(cpf):
    """Confere os dois dígitos verificadores de um CPF com 11 dígitos."""
    if len(cpf) != 11 or not cpf.isdigit() or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[tamanho]):
            return False
    return True


def validar_cpf(valor):
    if not isinstance(valor, str):
        return None, "Informe o CPF."
    cpf = somente_digitos(valor)
    if len(cpf) != 11:
        return None, "O CPF deve ter 11 dígitos."
    if not cpf_valido(cpf):
        return None, "CPF inválido. Confira os números digitados."
    return cpf, None


def validar_email(valor):
    if not isinstance(valor, str):
        return None, "Informe o e-mail."
    email = valor.strip().lower()
    if len(email) > 150 or not _EMAIL.match(email):
        return None, "Informe um e-mail válido, como nome@exemplo.com."
    return email, None


def validar_senha(valor):
    if not isinstance(valor, str):
        return None, "Informe a senha."
    if not 8 <= len(valor) <= 72:
        return None, "A senha deve ter de 8 a 72 caracteres."
    if not _TEM_LETRA.search(valor) or not _TEM_NUMERO.search(valor):
        return None, "A senha deve ter pelo menos uma letra e um número."
    return valor, None


def validar_cadastro(payload):
    """Valida o cadastro completo. Devolve (dados, erros por campo)."""
    if not isinstance(payload, dict):
        return {}, {"_geral": "Envie um objeto JSON com os dados do cadastro."}

    erros = {}
    for campo in sorted(payload.keys() - set(CAMPOS_CADASTRO)):
        erros[campo] = "Campo não permitido."

    dados = {}
    regras = (
        ("nome", validar_nome),
        ("matricula", validar_matricula),
        ("cpf", validar_cpf),
        ("email", validar_email),
        ("senha", validar_senha),
    )
    for campo, validar in regras:
        valor, erro = validar(payload.get(campo))
        if erro:
            erros[campo] = erro
        else:
            dados[campo] = valor

    if "senha" in dados and payload.get("confirmar_senha") != dados["senha"]:
        erros["confirmar_senha"] = "A confirmação não é igual à senha."

    return dados, erros
