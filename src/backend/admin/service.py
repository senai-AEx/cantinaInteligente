"""Camada de serviço da administração: usuários, movimentações e relatórios.

- Usuários nunca são apagados: "excluir" é inativar (status INATIVO).
- O administrador não inativa a si mesmo nem tira o próprio perfil de
  administrador (erro 409, código OPERACAO_PROPRIA).
- Movimentações e relatórios recebem o período em datas locais de Brasília
  (UTC−3 fixo), inclusivas. O banco guarda as datas em UTC; por isso o período
  é convertido para um intervalo UTC antes da consulta.
"""
from datetime import date, datetime, time, timedelta, timezone
import re
from typing import NamedTuple

from ..carteira import service as carteira_service
from ..erros import ErroNegocio, ErroValidacao, NaoEncontrado
from ..http import validar_chave_idempotencia
from ..seguranca import PERFIL_ADMINISTRADOR, PERFIL_CLIENTE
from ..usuarios.validacao import validar_email, validar_matricula, validar_nome
from . import repository as admin_repository
from .repository import RegistroDuplicado

FUSO_BRASILIA = timezone(timedelta(hours=-3))
# Sem `de`, o período começa 30 dias antes de `ate` (como no exemplo do contrato).
DIAS_PERIODO_PADRAO = 30
MAXIMO_DIAS_PERIODO = 366
DATA_MINIMA = date(2000, 1, 1)
DATA_MAXIMA = date(2100, 12, 31)

STATUS_FILTRO = ("TODOS", "ATIVO", "INATIVO")
PERFIS = (PERFIL_ADMINISTRADOR, PERFIL_CLIENTE)
PERFIS_FILTRO = ("TODOS",) + PERFIS
TIPOS_FILTRO = ("TODOS", "CREDITO", "DEBITO", "AJUSTE")
MAXIMO_BUSCA = 100
MAX_INT = 2_147_483_647

CAMPOS_EDITAVEIS = ("nome", "matricula", "email", "perfil")
AJUSTE_MAXIMO_CENTAVOS = 100_000
MOTIVO_MINIMO = 5
MOTIVO_MAXIMO = 150

CODIGO_OPERACAO_PROPRIA = "OPERACAO_PROPRIA"
USUARIO_NAO_ENCONTRADO = "Usuário não encontrado."
MENSAGENS_DUPLICIDADE = {
    "matricula": "Já existe um cadastro com esta matrícula.",
    "email": "Já existe um cadastro com este e-mail.",
}

_FORMATO_DATA = re.compile(r"\d{4}-\d{2}-\d{2}", re.ASCII)
_INTEIRO_POSITIVO = re.compile(r"\d{1,10}", re.ASCII)


# ---------- período (datas locais → intervalo UTC) ----------

class Periodo(NamedTuple):
    """Datas locais inclusivas e os limites UTC usados no SQL.

    `inicio_utc` (incluído) e `fim_utc` (excluído) são datetimes sem fuso, já
    em UTC, prontos para comparar com as colunas `data_hora`.
    """

    de: date
    ate: date
    inicio_utc: datetime
    fim_utc: datetime


def hoje_brasilia(agora=None):
    """Data de hoje em Brasília. `agora` (datetime com fuso) existe para os testes."""
    agora = agora or datetime.now(timezone.utc)
    return agora.astimezone(FUSO_BRASILIA).date()


def _ler_data(texto, campo, erros):
    texto = (texto or "").strip()
    if not texto:
        return None
    try:
        if not _FORMATO_DATA.fullmatch(texto):
            raise ValueError(texto)
        valor = date.fromisoformat(texto)
    except ValueError:
        erros[campo] = "Informe uma data válida no formato AAAA-MM-DD."
        return None
    if not DATA_MINIMA <= valor <= DATA_MAXIMA:
        erros[campo] = f"Informe uma data entre {DATA_MINIMA.year} e {DATA_MAXIMA.year}."
        return None
    return valor


def _meia_noite_local_em_utc(dia):
    local = datetime.combine(dia, time.min, tzinfo=FUSO_BRASILIA)
    return local.astimezone(timezone.utc).replace(tzinfo=None)


def interpretar_periodo(de_texto, ate_texto, hoje):
    """Converte `de` e `ate` (AAAA-MM-DD, datas de Brasília) em um Periodo.

    Sem `ate`, vale `hoje`; sem `de`, vale 30 dias antes de `ate`. O intervalo
    UTC vai da meia-noite local de `de` até a meia-noite local do dia seguinte
    a `ate`. Função pura: `hoje` é recebido para facilitar os testes.
    """
    erros = {}
    de = _ler_data(de_texto, "de", erros)
    ate = _ler_data(ate_texto, "ate", erros)
    if erros:
        raise ErroValidacao(erros)

    if ate is None:
        ate = hoje
    if de is None:
        de = ate - timedelta(days=DIAS_PERIODO_PADRAO)
    if de > ate:
        raise ErroValidacao({"de": "A data inicial não pode ser depois da data final."})
    if (ate - de).days + 1 > MAXIMO_DIAS_PERIODO:
        raise ErroValidacao(
            {"ate": f"O período pode ter no máximo {MAXIMO_DIAS_PERIODO} dias."}
        )
    return Periodo(
        de=de,
        ate=ate,
        inicio_utc=_meia_noite_local_em_utc(de),
        fim_utc=_meia_noite_local_em_utc(ate + timedelta(days=1)),
    )


def periodo_json(periodo):
    return {"de": periodo.de.isoformat(), "ate": periodo.ate.isoformat()}


# ---------- filtros das consultas ----------

def _ler_opcao(valor, opcoes, campo, erros):
    """Normaliza um filtro de lista fixa; vazio vale a primeira opção (TODOS)."""
    texto = (valor or "").strip().upper() or opcoes[0]
    if texto not in opcoes:
        erros[campo] = f"Use {', '.join(opcoes[:-1])} ou {opcoes[-1]} na consulta."
    return texto


def validar_filtros_usuarios(q, status, perfil):
    """Devolve (termo, status, perfil) normalizados ou lança ErroValidacao."""
    erros = {}
    termo = (q or "").strip()
    if len(termo) > MAXIMO_BUSCA:
        erros["q"] = f"A busca pode ter no máximo {MAXIMO_BUSCA} caracteres."
    status = _ler_opcao(status, STATUS_FILTRO, "status", erros)
    perfil = _ler_opcao(perfil, PERFIS_FILTRO, "perfil", erros)
    if erros:
        raise ErroValidacao(erros)
    return termo, status, perfil


def _ler_id_usuario(valor, erros):
    """Filtro opcional ?id_usuario=: vazio vale None (todos os usuários)."""
    texto = (valor or "").strip()
    if not texto:
        return None
    if _INTEIRO_POSITIVO.fullmatch(texto) and 1 <= int(texto) <= MAX_INT:
        return int(texto)
    erros["id_usuario"] = "Informe um identificador de usuário válido."
    return None


def validar_filtros_movimentacoes(tipo, id_usuario):
    """Devolve (tipo, id_usuario ou None) ou lança ErroValidacao."""
    erros = {}
    tipo = _ler_opcao(tipo, TIPOS_FILTRO, "tipo", erros)
    id_filtrado = _ler_id_usuario(id_usuario, erros)
    if erros:
        raise ErroValidacao(erros)
    return tipo, id_filtrado


def validar_filtros_compras(id_usuario):
    """Devolve o id_usuario do filtro (ou None) ou lança ErroValidacao."""
    erros = {}
    id_filtrado = _ler_id_usuario(id_usuario, erros)
    if erros:
        raise ErroValidacao(erros)
    return id_filtrado


# ---------- usuários ----------

def listar_usuarios(q, status, perfil):
    termo, status, perfil = validar_filtros_usuarios(q, status, perfil)
    return admin_repository.listar_usuarios(termo, status, perfil)


def consultar_usuario(id_usuario):
    usuario = admin_repository.consultar_usuario(id_usuario)
    if usuario is None:
        raise NaoEncontrado(USUARIO_NAO_ENCONTRADO)
    return usuario


def validar_edicao_usuario(payload):
    """Devolve {nome, matricula, email, perfil} normalizados ou lança ErroValidacao.

    CPF, senha e situação não são editáveis aqui: qualquer campo fora da lista
    é recusado.
    """
    if not isinstance(payload, dict):
        raise ErroValidacao({"_geral": "Envie um objeto JSON com os dados do usuário."})

    validadores = {
        "nome": validar_nome,
        "matricula": validar_matricula,
        "email": validar_email,
    }
    erros = {}
    dados = {}
    for campo in sorted(payload.keys() - set(CAMPOS_EDITAVEIS)):
        erros[campo] = "Campo não permitido."
    for campo in CAMPOS_EDITAVEIS:
        valor = payload.get(campo)
        if valor is None:
            erros[campo] = "Campo obrigatório."
        elif campo == "perfil":
            perfil = valor.strip().upper() if isinstance(valor, str) else ""
            if perfil in PERFIS:
                dados[campo] = perfil
            else:
                erros[campo] = "Escolha ADMINISTRADOR ou CLIENTE."
        else:
            normalizado, erro = validadores[campo](valor)
            if erro:
                erros[campo] = erro
            else:
                dados[campo] = normalizado
    if erros:
        raise ErroValidacao(erros)
    return dados


def alterar_usuario(id_usuario, payload, administrador):
    dados = validar_edicao_usuario(payload)
    if id_usuario == administrador["id_usuario"] and dados["perfil"] != PERFIL_ADMINISTRADOR:
        raise ErroNegocio(
            "Você não pode tirar o seu próprio perfil de administrador.",
            codigo=CODIGO_OPERACAO_PROPRIA,
        )
    with admin_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            if admin_repository.carregar_usuario(cursor, id_usuario, bloquear=True) is None:
                raise NaoEncontrado(USUARIO_NAO_ENCONTRADO)
            try:
                admin_repository.atualizar_usuario(cursor, id_usuario, dados)
            except RegistroDuplicado as exc:
                raise ErroValidacao({exc.campo: MENSAGENS_DUPLICIDADE[exc.campo]}) from exc
            return admin_repository.carregar_usuario(cursor, id_usuario)
        finally:
            cursor.close()


def _mudar_status(id_usuario, status_novo):
    with admin_repository.transacao() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            antes = admin_repository.carregar_usuario(cursor, id_usuario, bloquear=True)
            if antes is None:
                raise NaoEncontrado(USUARIO_NAO_ENCONTRADO)
            if antes["status"] == status_novo:
                return antes
            admin_repository.atualizar_status(cursor, id_usuario, status_novo)
            return admin_repository.carregar_usuario(cursor, id_usuario)
        finally:
            cursor.close()


def inativar_usuario(id_usuario, administrador):
    """Exclusão lógica: o usuário continua no banco, mas não consegue mais entrar."""
    if id_usuario == administrador["id_usuario"]:
        raise ErroNegocio(
            "Você não pode inativar o seu próprio usuário.",
            codigo=CODIGO_OPERACAO_PROPRIA,
        )
    return _mudar_status(id_usuario, "INATIVO")


def reativar_usuario(id_usuario):
    return _mudar_status(id_usuario, "ATIVO")


# ---------- ajuste de saldo ----------

def validar_ajuste(payload):
    """Devolve (valor_centavos, motivo, chave_idempotencia) ou lança ErroValidacao."""
    if not isinstance(payload, dict):
        raise ErroValidacao({"_geral": "Envie um objeto JSON com os dados do ajuste."})

    erros = {}
    valor = payload.get("valor_centavos")
    # bool é subclasse de int no Python; true/false não valem como valor.
    if isinstance(valor, bool) or not isinstance(valor, int):
        erros["valor_centavos"] = "Informe um número inteiro válido."
    elif valor == 0:
        erros["valor_centavos"] = "O valor do ajuste não pode ser zero."
    elif abs(valor) > AJUSTE_MAXIMO_CENTAVOS:
        erros["valor_centavos"] = "O ajuste pode ser de no máximo R$ 1.000,00."

    motivo = payload.get("motivo")
    if not isinstance(motivo, str):
        erros["motivo"] = "Informe um texto válido."
    else:
        motivo = motivo.strip()
        if not MOTIVO_MINIMO <= len(motivo) <= MOTIVO_MAXIMO:
            erros["motivo"] = f"Informe entre {MOTIVO_MINIMO} e {MOTIVO_MAXIMO} caracteres."

    chave = None
    try:
        chave = validar_chave_idempotencia(payload.get("chave_idempotencia"))
    except ErroValidacao as exc:
        erros.update(exc.campos)

    if erros:
        raise ErroValidacao(erros)
    return valor, motivo, chave


def ajustar_saldo(id_usuario, payload, administrador):
    """Devolve (movimentacao, carteira, criado). `criado` é False se a chave já foi usada."""
    valor_centavos, motivo, chave = validar_ajuste(payload)
    consultar_usuario(id_usuario)  # 404 se o usuário não existir
    return carteira_service.ajustar_saldo(
        id_usuario, valor_centavos, motivo, administrador["id_usuario"], chave
    )


# ---------- movimentações ----------

def listar_movimentacoes(de, ate, tipo, id_usuario, limite, hoje=None):
    periodo = interpretar_periodo(de, ate, hoje or hoje_brasilia())
    tipo, id_usuario = validar_filtros_movimentacoes(tipo, id_usuario)
    movimentacoes, totais = admin_repository.listar_movimentacoes(
        periodo.inicio_utc, periodo.fim_utc, tipo, id_usuario, limite
    )
    return {
        "periodo": periodo_json(periodo),
        "movimentacoes": movimentacoes,
        "totais": totais,
    }


# ---------- compras registradas ----------

def listar_compras(de, ate, id_usuario, limite, hoje=None):
    """Quem comprou o quê no período. `total_compras` ignora o limite da página."""
    periodo = interpretar_periodo(de, ate, hoje or hoje_brasilia())
    id_usuario = validar_filtros_compras(id_usuario)
    compras, total_compras = admin_repository.listar_compras(
        periodo.inicio_utc, periodo.fim_utc, id_usuario, limite
    )
    return {
        "periodo": periodo_json(periodo),
        "total_compras": total_compras,
        "compras": compras,
    }


# ---------- relatórios ----------

def montar_resumo_vendas(quantidade_compras, itens_vendidos, total_centavos, custo_centavos):
    """Lucro = total − custo; ticket médio = total ÷ compras (divisão inteira)."""
    return {
        "quantidade_compras": quantidade_compras,
        "itens_vendidos": itens_vendidos,
        "total_centavos": total_centavos,
        "custo_centavos": custo_centavos,
        "lucro_centavos": total_centavos - custo_centavos,
        "ticket_medio_centavos": (
            total_centavos // quantidade_compras if quantidade_compras else 0
        ),
    }


def relatorio_vendas(de, ate, hoje=None):
    periodo = interpretar_periodo(de, ate, hoje or hoje_brasilia())
    totais, por_produto, por_dia, por_usuario = admin_repository.relatorio_vendas(
        periodo.inicio_utc, periodo.fim_utc
    )
    return {
        "periodo": periodo_json(periodo),
        "resumo": montar_resumo_vendas(**totais),
        "por_produto": por_produto,
        "por_dia": por_dia,
        "por_usuario": por_usuario,
    }


def relatorio_saldos():
    usuarios = admin_repository.listar_saldos(PERFIL_CLIENTE)
    return {
        "quantidade_usuarios": len(usuarios),
        "total_saldos_centavos": sum(usuario["saldo_centavos"] for usuario in usuarios),
        "usuarios": usuarios,
    }


def resumir_estoque(produtos):
    """Totais do estoque. `sem_estoque` conta só produtos ATIVOS com quantidade zero."""
    return {
        "quantidade_produtos": len(produtos),
        "sem_estoque": sum(
            1
            for produto in produtos
            if produto["status"] == "ATIVO" and produto["quantidade_estoque"] == 0
        ),
        "total_itens": sum(produto["quantidade_estoque"] for produto in produtos),
        "valor_estoque_centavos": sum(
            produto["valor_estoque_centavos"] for produto in produtos
        ),
        "produtos": produtos,
    }


def relatorio_estoque():
    return resumir_estoque(admin_repository.listar_estoque())
