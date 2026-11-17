# API de produtos

API JSON em `http://127.0.0.1:5000` (Python + Flask + MySQL). Ainda não há login: as rotas administrativas são para uso local até a implementação de autenticação e perfis (RNF08).

## Corpo de cadastro e edição

`POST /api/produtos` e `PUT /api/produtos/{id}` recebem:

```json
{
  "nome": "Suco de uva 200 ml",
  "descricao": "Produto de demonstração",
  "categoria": "Bebidas",
  "preco_compra_centavos": 300,
  "preco_venda_centavos": 450,
  "quantidade_estoque": 10,
  "foto_caminho": "assets/produtos/3f2a...png"
}
```

- Obrigatórios: `nome`, `categoria`, `preco_compra_centavos`, `preco_venda_centavos`.
- `descricao` vazia, `quantidade_estoque` 0 e `foto_caminho` nulo quando omitidos.
- `id_produto`, `status`, `zero_lactose` e `zero_acucar` são definidos pelo servidor. Enviá-los (ou campos antigos como `codigo_produto`, `validade`, `estoque_minimo`, `estoque_maximo`) gera erro `422` "Campo não permitido".
- `PUT` substitui todos os dados editáveis: envie o produto completo.

Resposta de sucesso: `{"produto": {...}}` com todos os campos do [modelo](modelo-produto.md).

## Rotas

| Método e rota | Uso | Sucesso |
| --- | --- | --- |
| `GET /api/health` | Verificar o Flask | `200` |
| `GET /api/health/db` | Verificar o MySQL (`SELECT 1`) | `200`; banco fora: `503` |
| `GET /api/produtos?q=&status=` | Listar; `q` busca por nome, categoria ou código (id); `status` = `TODOS` (padrão), `ATIVO` ou `INATIVO` | `200` com lista |
| `GET /api/produtos/{id}` | Consultar um produto | `200`; não existe: `404` |
| `POST /api/produtos` | Cadastrar | `201` + cabeçalho `Location` |
| `PUT /api/produtos/{id}` | Alterar | `200`; não existe: `404` |
| `PATCH /api/produtos/{id}/inativar` | **Excluir** (exclusão lógica: fica `INATIVO`) | `200` |
| `PATCH /api/produtos/{id}/reativar` | Reativar | `200` |
| `GET /api/produtos/{id}/auditoria` | Últimas 100 ações do produto | `200` com `{"auditorias": [...]}` |
| `POST /api/uploads/produtos` | Enviar foto (`multipart/form-data`, campo `imagem`; JPG/PNG/WebP até 5 MB) | `201` com `{"foto_caminho": "assets/produtos/..."}` |

Não existe `DELETE /api/produtos/{id}`: a chamada responde `405`.

## Erros

Campos inválidos respondem `422`:

```json
{
  "erro": "Revise os campos informados.",
  "campos": {
    "preco_venda_centavos": "O preço de venda não pode ser menor que o preço de compra."
  }
}
```

JSON malformado ou sem `Content-Type: application/json`: `400`. Produto inexistente: `404`. Banco indisponível ou `.env` incompleto: `503`.

## Auditoria e autor

Toda inclusão, alteração, inativação e reativação grava a auditoria na mesma transação. O cabeçalho opcional `X-Actor` identifica o operador (padrão `administrador-local`); é apenas informativo enquanto não houver login.

## Uso pelo frontend

CORS aceita `localhost`/`127.0.0.1` nas portas 5500, 5501 (Live Server) e 5173 (Vite). Para fotos, a tela envia o arquivo para `/api/uploads/produtos` antes do `POST`/`PUT` e inclui o `foto_caminho` retornado.
