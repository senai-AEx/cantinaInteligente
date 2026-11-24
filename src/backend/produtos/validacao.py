"""Validação dos dados de entrada do cadastro de produtos.

O identificador (`id_produto`) é gerado pelo banco (AUTO_INCREMENT) e a
situação (`status`) e os selos são controlados pelo servidor; por isso esses
campos não fazem parte do formulário.

`validar_produto` chama uma função para cada tipo de campo e junta os erros.
"""

MAX_INT = 2_147_483_647

CAMPOS_EDITAVEIS = (
    "nome",
    "descricao",
    "categoria",
    "preco_compra_centavos",
    "preco_venda_centavos",
    "quantidade_estoque",
    "foto_caminho",
)
CAMPOS_OBRIGATORIOS = {
    "nome",
    "categoria",
    "preco_compra_centavos",
    "preco_venda_centavos",
}

# campo -> (mínimo, máximo) de caracteres
REGRAS_TEXTO = {
    "nome": (2, 100),
    "categoria": (2, 50),
    "descricao": (0, 500),
}
# campo -> (mínimo, máximo) do número inteiro
REGRAS_INTEIRO = {
    "preco_compra_centavos": (1, MAX_INT),
    "preco_venda_centavos": (1, MAX_INT),
    "quantidade_estoque": (0, MAX_INT),
}


def validar_produto(payload):
    """Devolve (dados normalizados, erros por campo)."""
    if not isinstance(payload, dict):
        return {}, {"_geral": "Envie um objeto JSON com os dados do produto."}

    erros = _campos_fora_do_formulario(payload)
    dados = {}
    _validar_textos(payload, erros, dados)
    _validar_numeros(payload, erros, dados)
    _validar_precos(dados, erros)
    _validar_foto_do_produto(payload, erros, dados)
    return dados, erros


def _campos_fora_do_formulario(payload):
    """Campos que não podem ser enviados e campos obrigatórios que faltam."""
    erros = {}
    for campo in sorted(payload.keys() - set(CAMPOS_EDITAVEIS)):
        erros[campo] = "Campo não permitido."
    for campo in sorted(CAMPOS_OBRIGATORIOS - payload.keys()):
        erros[campo] = "Campo obrigatório."
    return erros


def _validar_textos(payload, erros, dados):
    for campo, (minimo, maximo) in REGRAS_TEXTO.items():
        if campo in erros:
            continue
        valor = payload.get(campo)
        if valor is None and campo not in CAMPOS_OBRIGATORIOS:
            valor = ""
        if not isinstance(valor, str):
            erros[campo] = "Informe um texto válido."
            continue
        valor = valor.strip()
        if minimo <= len(valor) <= maximo:
            dados[campo] = valor
        else:
            erros[campo] = f"Informe entre {minimo} e {maximo} caracteres."


def _validar_numeros(payload, erros, dados):
    for campo, (minimo, maximo) in REGRAS_INTEIRO.items():
        if campo in erros:
            continue
        valor = payload.get(campo, 0)
        if isinstance(valor, bool) or not isinstance(valor, int):
            erros[campo] = "Informe um número inteiro válido."
        elif not minimo <= valor <= maximo:
            erros[campo] = (
                "Informe um valor maior que zero."
                if minimo == 1
                else "O valor não pode ser negativo."
            )
        else:
            dados[campo] = valor


def _validar_precos(dados, erros):
    """O preço de venda não pode ser menor que o de compra (só confere se os dois são válidos)."""
    compra = dados.get("preco_compra_centavos")
    venda = dados.get("preco_venda_centavos")
    if compra is not None and venda is not None and venda < compra:
        erros["preco_venda_centavos"] = (
            "O preço de venda não pode ser menor que o preço de compra."
        )


def _validar_foto_do_produto(payload, erros, dados):
    foto, erro_foto = _validar_foto(payload.get("foto_caminho"))
    if erro_foto:
        erros["foto_caminho"] = erro_foto
    else:
        dados["foto_caminho"] = foto


def _validar_foto(foto):
    if foto in (None, ""):
        return None, None
    if not isinstance(foto, str):
        return None, "Informe um caminho de imagem válido."
    foto = foto.strip().replace("\\", "/")
    if not foto:
        return None, None
    if len(foto) > 255:
        return None, "O caminho pode ter no máximo 255 caracteres."
    partes = foto.split("/")
    if (
        foto.startswith("/")
        or not foto.startswith("assets/produtos/")
        or ".." in partes
        or not partes[-1]
    ):
        return None, "Use um caminho relativo dentro de assets/produtos/."
    return foto, None
