"""Erros de negócio da aplicação.

Os serviços lançam estas exceções e o `app.py` as converte em respostas JSON
no formato {"erro": "...", "campos": {...}, "codigo": "...", "detalhes": {...}}.
Nenhum controller precisa de try/except para elas.
"""


class ErroAplicacao(Exception):
    status = 400
    mensagem_padrao = "Não foi possível concluir a operação."

    def __init__(self, mensagem=None, *, campos=None, codigo=None, detalhes=None):
        super().__init__(mensagem or self.mensagem_padrao)
        self.mensagem = mensagem or self.mensagem_padrao
        self.campos = campos
        self.codigo = codigo
        self.detalhes = detalhes

    def para_json(self):
        corpo = {"erro": self.mensagem}
        if self.campos:
            corpo["campos"] = self.campos
        if self.codigo:
            corpo["codigo"] = self.codigo
        if self.detalhes is not None:
            corpo["detalhes"] = self.detalhes
        return corpo


class ErroValidacao(ErroAplicacao):
    """Campos inválidos (HTTP 422). `campos` é {nome_do_campo: mensagem}."""

    status = 422
    mensagem_padrao = "Revise os campos informados."

    def __init__(self, campos, mensagem=None):
        super().__init__(mensagem, campos=campos)


class NaoAutenticado(ErroAplicacao):
    status = 401
    mensagem_padrao = "Faça login para continuar."


class SemPermissao(ErroAplicacao):
    status = 403
    mensagem_padrao = "Você não tem permissão para esta operação."


class NaoEncontrado(ErroAplicacao):
    status = 404
    mensagem_padrao = "Registro não encontrado."


class ErroNegocio(ErroAplicacao):
    """Regra de negócio impede a operação (HTTP 409). Ex.: saldo insuficiente."""

    status = 409
