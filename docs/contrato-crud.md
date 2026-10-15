# API de Produtos — contrato para o frontend

Backend da AV04: Python + Flask + MySQL. A API usa JSON e fica em `http://127.0.0.1:5000`. Os endpoints administrativos são para execução local na apresentação; ainda não há login nem autorização por perfil.

## Produto e convenções

Os nomes de campo seguem [o modelo de Produto](modelo-produto.md). `preco_centavos` é inteiro: R$ 4,50 é enviado como `450`, sem ponto flutuante. `validade` usa `AAAA-MM-DD` ou `null`; `foto_caminho` é um caminho relativo em `assets/produtos/` ou `null`. Selos são booleanos JSON. A API responde datas de auditoria em UTC com sufixo `Z`.

Exemplo de corpo para `POST` e `PUT`:

```json
{
  "codigo_produto": "CI-AV04-001",
  "nome": "Suco de uva 200 ml",
  "descricao": "Produto de demonstração",
  "categoria": "Bebidas",
  "preco_centavos": 450,
  "quantidade_estoque": 10,
  "estoque_minimo": 3,
  "estoque_maximo": 20,
  "validade": "2026-12-15",
  "foto_caminho": "assets/produtos/suco-uva.jpg",
  "zero_lactose": true,
  "zero_acucar": false
}
```

`codigo_produto`, `nome`, `categoria` e `preco_centavos` são obrigatórios. A descrição começa vazia, estoque e mínimos/máximos começam em zero, validade e foto começam nulas e selos começam falsos quando omitidos. `PUT` substitui os dados editáveis: a tela deve enviar o produto completo que está editando. A situação (`status`) e os identificadores são controlados pelo servidor.

## Rotas

| Método e rota | Uso | Sucesso |
| --- | --- | --- |
| `GET /api/health` | Verificar Flask | `200` `{"status":"ok"}` |
| `GET /api/health/db` | Verificar MySQL com `SELECT 1` | `200`; indisponível: `503` |
| `GET /api/produtos?q=suco&status=ATIVO` | Listar e filtrar por código, nome ou categoria e situação | `200` com uma lista JSON; sem resultados: `[]` |
| `GET /api/produtos/{id}` | Abrir detalhes para visualizar/editar | `200` com `{"produto": {...}}`; não existe: `404` |
| `POST /api/produtos` | Cadastrar | `201` com `{"produto": {...}}` e cabeçalho `Location` |
| `PUT /api/produtos/{id}` | Salvar edição | `200` com `{"produto": {...}}`; não existe: `404` |
| `DELETE /api/produtos/{id}` | Inativar após confirmação da interface | `200` com o produto inativo; não existe: `404` |
| `PATCH /api/produtos/{id}/reativar` | Reativar produto | `200` com o produto ativo; não existe: `404` |
| `GET /api/produtos/{id}/auditoria` | Consultar até 100 alterações mais recentes | `200` com `{"auditorias": [...]}`; não existe: `404` |

O filtro `status` aceita `TODOS`, `ATIVO` ou `INATIVO`; o padrão é `TODOS`, para a tela administrativa poder localizar itens inativos. `q` é opcional. As rotas de catálogo devem exibir apenas produtos ativos, com estoque maior que zero e validade não vencida; a listagem administrativa continua mostrando todos.

`DELETE` é uma inativação lógica, não remove a linha do banco. Inativar um produto já inativo ou reativar um já ativo não duplica registros de auditoria.

## Respostas de erro

Campos inválidos respondem `422` e indicam o problema por campo:

```json
{
  "erro": "Revise os campos informados.",
  "campos": {
    "preco_centavos": "O valor está fora do limite permitido.",
    "estoque_maximo": "Deve ser maior ou igual ao estoque mínimo."
  }
}
```

O front deve mostrar `campos[nome_do_campo]` junto ao respectivo controle e preservar os outros valores digitados. Código duplicado, texto fora dos limites, preço não positivo, quantidade negativa, máximo menor que mínimo, data inválida e chaves desconhecidas são recusados. JSON malformado ou tipo de conteúdo incorreto responde `400`; identificador inexistente responde `404`; banco indisponível ou não configurado responde `503`.

## Auditoria e transações

Inclusão, edição, inativação e reativação registram ação, produto, autor, origem, horário UTC e valores antes/depois. Cada alteração e seu registro de auditoria ficam na mesma transação MySQL; se uma falhar, ambas são revertidas. A interface pode enviar `X-Actor` para identificar o operador na demonstração; sem o cabeçalho, fica `administrador-local`. Esse valor é informativo e não comprova identidade enquanto o sistema não tiver autenticação.

## Integração local do frontend

Para desenvolvimento separado, CORS aceita as origens de Live Server `http://localhost:5500` e `http://127.0.0.1:5500`, e Vite `http://localhost:5173` e `http://127.0.0.1:5173`. A interface pode usar `fetch("http://127.0.0.1:5000/api/produtos")`, enviar/receber JSON e tratar códigos HTTP. Não abra o CRUD administrativo para uma rede pública antes de adicionar autenticação e autorização de Administrador.

Exemplo de chamada do navegador:

```js
const resposta = await fetch("http://127.0.0.1:5000/api/produtos", {
  method: "POST",
  headers: { "Content-Type": "application/json", "X-Actor": "administrador-local" },
  body: JSON.stringify(produto), // preco_centavos deve ser inteiro, por exemplo 450
});
const resultado = await resposta.json();

if (!resposta.ok) {
  // Exiba resultado.campos perto dos campos inválidos, quando existir.
  throw new Error(resultado.erro);
}
```
