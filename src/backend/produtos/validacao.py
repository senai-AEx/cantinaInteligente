"""Validação dos dados de entrada do cadastro de produtos.

O identificador (`id_produto`) é gerado pelo banco (AUTO_INCREMENT) e a
situação (`status`) e os selos são controlados pelo servidor; por isso esses
campos não fazem parte do formulário.
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

REGRAS_TEXTO = {
    "nome": (2, 100),
    "categoria": (2, 50),
    "descricao": (0, 500),
}
REGRAS_INTEIRO = {
    "preco_compra_centavos": (1, MAX_INT),
    "preco_venda_centavos": (1, MAX_INT),
    "quantidade_estoque": (0, MAX_INT),
}


def validar_produto(payload):
    """Retorna (dados normalizados, erros por campo)."""
    if not isinstance(payload, dict):
        return {}, {"_geral": "Envie um objeto JSON com os dados do produto."}

    erros = {}
    for campo in sorted(payload.keys() - set(CAMPOS_EDITAVEIS)):
        erros[campo] = "Campo não permitido."
    for campo in sorted(CAMPOS_OBRIGATORIOS - payload.keys()):
        erros[campo] = "Campo obrigatório."

    dados = {}
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
        if not minimo <= len(valor) <= maximo:
            erros[campo] = f"Informe entre {minimo} e {maximo} caracteres."
        else:
            dados[campo] = valor

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

    if (
        "preco_compra_centavos" in dados
        and "preco_venda_centavos" in dados
        and dados["preco_venda_centavos"] < dados["preco_compra_centavos"]
    ):
        erros["preco_venda_centavos"] = (
            "O preço de venda não pode ser menor que o preço de compra."
        )

    foto, erro_foto = _validar_foto(payload.get("foto_caminho"))
    if erro_foto:
        erros["foto_caminho"] = erro_foto
    else:
        dados["foto_caminho"] = foto

    return dados, erros


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
