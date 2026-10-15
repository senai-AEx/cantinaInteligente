"""Validação do contrato de entrada dos produtos da AV04."""
from datetime import date


MAX_INT = 2_147_483_647
EDITABLE_FIELDS = {
    "codigo_produto",
    "nome",
    "descricao",
    "categoria",
    "preco_centavos",
    "quantidade_estoque",
    "estoque_minimo",
    "estoque_maximo",
    "validade",
    "foto_caminho",
    "zero_lactose",
    "zero_acucar",
}
REQUIRED_FIELDS = {"codigo_produto", "nome", "categoria", "preco_centavos"}


def validar_produto(payload):
    """Retorna (dados normalizados, erros por campo)."""
    if not isinstance(payload, dict):
        return {}, {"_geral": "Envie um objeto JSON com os dados do produto."}

    errors = {}
    for field in payload.keys() - EDITABLE_FIELDS:
        errors[field] = "Campo não permitido."
    for field in REQUIRED_FIELDS - payload.keys():
        errors[field] = "Campo obrigatório."

    result = {}
    text_rules = {
        "codigo_produto": (3, 32),
        "nome": (2, 100),
        "categoria": (2, 50),
        "descricao": (0, 500),
    }
    for field, (minimum, maximum) in text_rules.items():
        value = payload.get(field, "" if field == "descricao" else None)
        if value is None and field not in REQUIRED_FIELDS:
            value = ""
        if not isinstance(value, str):
            errors[field] = "Informe um texto válido."
            continue
        value = value.strip()
        if len(value) < minimum or len(value) > maximum:
            errors[field] = f"Informe entre {minimum} e {maximum} caracteres."
        else:
            result[field] = value

    integer_rules = {
        "preco_centavos": (1, MAX_INT),
        "quantidade_estoque": (0, MAX_INT),
        "estoque_minimo": (0, MAX_INT),
        "estoque_maximo": (0, MAX_INT),
    }
    for field, (minimum, maximum) in integer_rules.items():
        default = None if field == "preco_centavos" else 0
        value = payload.get(field, default)
        if isinstance(value, bool) or not isinstance(value, int):
            errors[field] = "Informe um número inteiro válido."
        elif value < minimum or value > maximum:
            errors[field] = "O valor está fora do limite permitido."
        else:
            result[field] = value

    if "estoque_minimo" in result and "estoque_maximo" in result:
        if result["estoque_maximo"] < result["estoque_minimo"]:
            errors["estoque_maximo"] = "Deve ser maior ou igual ao estoque mínimo."

    validity = payload.get("validade")
    if validity in (None, ""):
        result["validade"] = None
    elif not isinstance(validity, str):
        errors["validade"] = "Informe uma data no formato AAAA-MM-DD."
    else:
        try:
            parsed = date.fromisoformat(validity)
            if parsed.isoformat() != validity:
                raise ValueError
            result["validade"] = parsed
        except ValueError:
            errors["validade"] = "Informe uma data existente no formato AAAA-MM-DD."

    photo = payload.get("foto_caminho")
    if photo in (None, ""):
        result["foto_caminho"] = None
    elif not isinstance(photo, str):
        errors["foto_caminho"] = "Informe um caminho de imagem válido."
    else:
        photo = photo.strip()
        if not photo:
            result["foto_caminho"] = None
        elif len(photo) > 255:
            errors["foto_caminho"] = "O caminho pode ter no máximo 255 caracteres."
        else:
            normalized_path = photo.replace("\\", "/")
            path_parts = normalized_path.split("/")
            if (
                normalized_path.startswith("/")
                or not normalized_path.startswith("assets/produtos/")
                or ".." in path_parts
                or not path_parts[-1]
            ):
                errors["foto_caminho"] = (
                    "Use um caminho relativo dentro de assets/produtos/."
                )
            else:
                result["foto_caminho"] = normalized_path

    for field in ("zero_lactose", "zero_acucar"):
        value = payload.get(field, False)
        if not isinstance(value, bool):
            errors[field] = "Informe verdadeiro ou falso."
        else:
            result[field] = value

    return result, errors
