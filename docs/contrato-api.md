# Contrato da API — Cantina Inteligente

Fonte única para backend e frontend. Produtos estão detalhados em [contrato-api-produtos.md](contrato-api-produtos.md); este documento cobre login, carteira, compras e administração.

## Convenções

- Telas e API saem do mesmo servidor Flask (`http://127.0.0.1:5000`). No frontend use sempre caminhos relativos: `/api/...`, `/html/...`.
- JSON em UTF-8. Dinheiro em **centavos inteiros** (`450` = R$ 4,50). Datas em UTC, ISO terminado em `Z`.
- Login por **cookie de sessão** (`HttpOnly`, `SameSite=Lax`). O frontend não guarda token.
- Erros: `{"erro": "mensagem", "campos": {"campo": "mensagem"}, "codigo": "CODIGO", "detalhes": {...}}` (só `erro` é sempre presente).

| Status | Quando |
| --- | --- |
| `400` | Corpo não é JSON válido |
| `401` | Sem login (`NaoAutenticado`) ou credenciais incorretas |
| `403` | Logado, mas sem permissão (`SemPermissao`) |
| `404` | Registro não existe ou não pertence ao usuário |
| `409` | Regra de negócio (`ErroNegocio`), com `codigo` |
| `422` | Campos inválidos (`ErroValidacao`), com `campos` |
| `503` | Banco indisponível |

**Idempotência:** operações que mexem em saldo recebem `chave_idempotencia` (UUID gerado pela tela com `Cantina.novaChave()`). Reenviar a mesma chave devolve o registro já criado, com status `200` em vez de `201`, sem duplicar.

## Objetos

```json
// usuario (nunca inclui senha nem CPF completo)
{"id_usuario": 7, "nome": "Maria Souza", "matricula": "202612345", "email": "maria@exemplo.com",
 "cpf_mascarado": "***.456.789-**", "perfil": "CLIENTE", "status": "ATIVO",
 "saldo_centavos": 1550, "criado_em": "2026-11-17T22:48:21.454404Z"}

// carteira
{"id_carteira": 7, "saldo_centavos": 1550, "atualizado_em": "2026-11-17T22:48:21.454404Z"}

// movimentacao — valor_centavos tem sinal: CREDITO > 0, DEBITO < 0, AJUSTE ≠ 0
{"id_movimentacao": 31, "tipo": "DEBITO", "valor_centavos": -450, "saldo_apos_centavos": 1550,
 "descricao": "Compra #12", "id_compra": 12, "data_hora": "2026-11-17T22:50:03.120000Z"}

// compra
{"id_compra": 12, "valor_total_centavos": 450, "data_hora": "2026-11-17T22:50:03.120000Z",
 "itens": [{"id_produto": 3, "nome": "Suco de uva 200 ml", "quantidade": 1,
            "preco_unitario_centavos": 450, "subtotal_centavos": 450}]}
```

`perfil`: `ADMINISTRADOR` ou `CLIENTE`. `status`: `ATIVO` ou `INATIVO`.

## Autenticação — `src/backend/usuarios/`

| Rota | Acesso | Corpo | Sucesso |
| --- | --- | --- | --- |
| `POST /api/auth/cadastro` | público | `nome`, `matricula`, `cpf`, `email`, `senha`, `confirmar_senha` | `201 {"usuario"}` e já inicia a sessão (perfil `CLIENTE`, carteira com saldo 0) |
| `POST /api/auth/login` | público | `identificador` (matrícula, e-mail ou CPF), `senha` | `200 {"usuario"}` |
| `POST /api/auth/logout` | público | — | `200 {"mensagem"}` |
| `GET /api/auth/eu` | público | — | `200 {"usuario": {...}}` ou `{"usuario": null}` |
| `PUT /api/auth/senha` | login | `senha_atual`, `nova_senha`, `confirmar_senha` | `200 {"mensagem": "Senha alterada."}` |

Regras dos campos (iguais na tela e no servidor):

| Campo | Regra |
| --- | --- |
| `nome` | 3 a 100 caracteres, com pelo menos uma letra |
| `matricula` | só números, 4 a 20 dígitos; única |
| `cpf` | 11 dígitos (aceita com máscara), dígitos verificadores válidos; único |
| `email` | formato de e-mail, até 150 caracteres; gravado em minúsculas; único |
| `senha` | 8 a 72 caracteres, com letra e número |
| `confirmar_senha` | igual a `senha` |

Troca de senha (`PUT /api/auth/senha`): `senha_atual` precisa conferir (senão `422` em `senha_atual`: "Senha atual incorreta."); `nova_senha` segue a regra de senha e deve ser diferente da atual; `confirmar_senha` igual a `nova_senha`. A sessão continua aberta.

Duplicidade responde `422` com o campo: `{"campos": {"matricula": "Já existe um cadastro com esta matrícula."}}`. Login incorreto responde `401` com a mesma mensagem para qualquer causa; usuário inativo responde `403`.

## Carteira — `src/backend/carteira/` (login obrigatório)

| Rota | Corpo / parâmetros | Sucesso |
| --- | --- | --- |
| `GET /api/carteira` | — | `200 {"carteira"}` |
| `GET /api/carteira/movimentacoes` | `?limite=50` (1 a 200) | `200 {"movimentacoes": [...]}` mais recentes primeiro |
| `POST /api/carteira/creditos` | `valor_centavos`, `chave_idempotencia` | `201 {"movimentacao", "carteira"}` |

Crédito = o usuário declara que depositou o valor na caixa da cantina. `valor_centavos` inteiro entre `100` (R$ 1,00) e `50000` (R$ 500,00). Descrição gravada: `"Depósito declarado na caixa"`.

## Compras — `src/backend/compras/` (login obrigatório)

| Rota | Corpo / parâmetros | Sucesso |
| --- | --- | --- |
| `POST /api/compras` | `itens: [{"id_produto", "quantidade"}]`, `chave_idempotencia` | `201 {"compra", "carteira"}` |
| `GET /api/compras` | `?limite=50` | `200 {"compras": [...]}` do usuário logado, mais recentes primeiro |
| `GET /api/compras/{id}` | — | `200 {"compra"}`; de outro usuário: `404` (administrador vê qualquer uma) |

Regras do `POST`: 1 a 50 itens; `id_produto` sem repetição; `quantidade` inteiro de 1 a 99. Tudo em **uma transação**: bloqueia a carteira e os produtos, confere estoque e saldo, grava compra e itens (com o preço de venda e o custo do momento), baixa o estoque, debita o saldo e grava a movimentação `DEBITO` com descrição `"Compra #<id>"`. Qualquer falha desfaz tudo.

Erros `409`:

| `codigo` | `detalhes` |
| --- | --- |
| `SALDO_INSUFICIENTE` | `{"saldo_centavos": 300, "total_centavos": 450}` |
| `ESTOQUE_INSUFICIENTE` | `{"produtos": [{"id_produto": 3, "nome": "...", "disponivel": 0, "solicitado": 2}]}` |
| `PRODUTO_INDISPONIVEL` | `{"produtos": [{"id_produto": 9}]}` (inexistente ou inativo) |

## Administração — `src/backend/admin/` (somente `ADMINISTRADOR`)

### Usuários

| Rota | Corpo / parâmetros | Sucesso |
| --- | --- | --- |
| `GET /api/admin/usuarios` | `?q=` (nome, matrícula ou e-mail), `?status=TODOS\|ATIVO\|INATIVO`, `?perfil=TODOS\|ADMINISTRADOR\|CLIENTE` | `200 {"usuarios": [...]}` por nome |
| `GET /api/admin/usuarios/{id}` | — | `200 {"usuario"}` |
| `PUT /api/admin/usuarios/{id}` | `nome`, `matricula`, `email`, `perfil` | `200 {"usuario"}` |
| `PATCH /api/admin/usuarios/{id}/inativar` | — | `200 {"usuario"}` |
| `PATCH /api/admin/usuarios/{id}/reativar` | — | `200 {"usuario"}` |
| `POST /api/admin/usuarios/{id}/senha` | `nova_senha`, `confirmar_senha` | `200 {"usuario"}` |
| `POST /api/admin/usuarios/{id}/ajustes` | `valor_centavos` (com sinal, ≠ 0, módulo até 100000), `motivo` (5 a 150 caracteres), `chave_idempotencia` | `201 {"movimentacao", "carteira"}` |

Redefinir senha: o administrador define uma senha provisória (mesma regra de senha) e a informa ao usuário pessoalmente; depois o usuário troca em "Minha conta". Erros `422` em `nova_senha` ou `confirmar_senha`.

Regras: usuários não são apagados. O administrador não pode inativar a si mesmo nem tirar o próprio perfil de administrador (`409`, `codigo: "OPERACAO_PROPRIA"`). CPF não é editável. Ajuste que deixaria o saldo negativo responde `409` `SALDO_INSUFICIENTE`. Descrição do ajuste: `"Ajuste da administração: <motivo>"`.

### Movimentações

`GET /api/admin/movimentacoes?de=AAAA-MM-DD&ate=AAAA-MM-DD&tipo=TODOS|CREDITO|DEBITO|AJUSTE&id_usuario=&limite=200` →

```json
{"periodo": {"de": "2026-10-18", "ate": "2026-11-17"},
 "movimentacoes": [{"id_movimentacao": 31, "tipo": "CREDITO", "valor_centavos": 2000,
                    "saldo_apos_centavos": 2000, "descricao": "...", "id_compra": null,
                    "data_hora": "...", "usuario": {"id_usuario": 7, "nome": "Maria Souza", "matricula": "202612345"}}],
 "totais": {"creditos_centavos": 2000, "debitos_centavos": -450, "ajustes_centavos": 0}}
```

`totais` considera todo o período filtrado, não só as linhas devolvidas.

### Relatórios

Período padrão: últimos 30 dias (inclusive hoje). `de` e `ate` são datas locais de Brasília (`America/Sao_Paulo`, UTC−3), no formato `AAAA-MM-DD`, inclusivas; `de` depois de `ate` ou data inválida responde `422`.

`GET /api/admin/relatorios/vendas?de=&ate=` →

```json
{"periodo": {"de": "2026-10-18", "ate": "2026-11-17"},
 "resumo": {"quantidade_compras": 12, "itens_vendidos": 30, "total_centavos": 14250,
            "custo_centavos": 9000, "lucro_centavos": 5250, "ticket_medio_centavos": 1187},
 "por_produto": [{"id_produto": 3, "nome": "Suco de uva 200 ml", "categoria": "Bebidas",
                  "quantidade": 10, "total_centavos": 4500, "lucro_centavos": 1500}],
 "por_dia": [{"data": "2026-11-17", "quantidade_compras": 4, "total_centavos": 5100}]}
```

`por_produto` em ordem de `total_centavos` decrescente; `por_dia` em ordem de data.

O relatório de vendas traz também o consumo por usuário, em ordem de `total_centavos` decrescente:

```json
"por_usuario": [{"id_usuario": 7, "nome": "Maria Souza", "matricula": "202612345",
                 "quantidade_compras": 3, "itens": 8, "total_centavos": 4350}]
```

### Compras registradas

`GET /api/admin/compras?de=AAAA-MM-DD&ate=AAAA-MM-DD&id_usuario=&limite=100` (limite de 1 a 500) mostra quem comprou o quê:

```json
{"periodo": {"de": "2026-10-18", "ate": "2026-11-17"},
 "total_compras": 12,
 "compras": [{"id_compra": 12, "data_hora": "2026-11-17T22:50:03.120000Z", "valor_total_centavos": 450,
              "usuario": {"id_usuario": 7, "nome": "Maria Souza", "matricula": "202612345"},
              "itens": [{"id_produto": 3, "nome": "Suco de uva 200 ml", "quantidade": 1,
                         "preco_unitario_centavos": 450, "subtotal_centavos": 450}]}]}
```

Mais recentes primeiro. `total_compras` conta todas as compras do período filtrado, não só as devolvidas. Mesmas regras de período dos relatórios.

`GET /api/admin/relatorios/saldos` →

```json
{"quantidade_usuarios": 25, "total_saldos_centavos": 41200,
 "usuarios": [{"id_usuario": 7, "nome": "Maria Souza", "matricula": "202612345",
               "status": "ATIVO", "saldo_centavos": 1550}]}
```

Somente perfil `CLIENTE`, por saldo decrescente.

`GET /api/admin/relatorios/estoque` →

```json
{"quantidade_produtos": 18, "sem_estoque": 2, "total_itens": 240, "valor_estoque_centavos": 68000,
 "produtos": [{"id_produto": 3, "nome": "Suco de uva 200 ml", "categoria": "Bebidas", "status": "ATIVO",
               "quantidade_estoque": 10, "preco_compra_centavos": 300, "preco_venda_centavos": 450,
               "valor_estoque_centavos": 3000}]}
```

`valor_estoque_centavos` = quantidade × preço de compra. Ordem: `quantidade_estoque` crescente (os zerados primeiro), depois nome. `sem_estoque` conta só produtos ativos com quantidade zero.

## QR Code — `src/backend/qr/` (somente `ADMINISTRADOR`)

O QR Code facilita o registro da compra: o cliente aponta a câmera do celular e o catálogo abre já com o produto na sacola.

| Rota | Resposta |
| --- | --- |
| `GET /api/qrcode` | `200 {"url_base": "http://192.168.0.10:5000", "url_cantina": ".../html/catalogo_produtos.html", "url_produto": ".../html/catalogo_produtos.html?adicionar={id}", "somente_local": false}` |
| `GET /api/qrcode/cantina.svg` | Imagem SVG (`image/svg+xml`) com o QR do catálogo |
| `GET /api/qrcode/produtos/{id}.svg` | Imagem SVG com o QR que adiciona o produto à sacola; produto inexistente: `404` |

- `url_base` vem de `URL_PUBLICA` no `.env`; sem ela, usa o endereço pelo qual o administrador está acessando.
- `somente_local` é `true` quando o endereço é `127.0.0.1` ou `localhost`: o QR só abre neste computador, não no celular. A tela deve avisar.
- Use as rotas `.svg` direto em `<img src>`; `url_produto` traz o texto `{id}` para a tela trocar pelo código do produto.

**No catálogo:** `/html/catalogo_produtos.html?adicionar=<id_produto>` coloca 1 unidade do produto na sacola (se estiver ativo e com estoque), mostra um aviso e remove o parâmetro do endereço para não repetir ao recarregar.

## Produtos e upload (resumo)

`GET /api/produtos` e `GET /api/produtos/{id}` são públicos. `POST`, `PUT`, `PATCH .../inativar`, `PATCH .../reativar`, `GET .../auditoria` e `POST /api/uploads/produtos` exigem `ADMINISTRADOR`.

## Funções Python compartilhadas entre módulos

Assinaturas que um módulo pode chamar de outro. Fora disso, cada módulo usa apenas o próprio `repository`.

```python
# src/backend/usuarios/repository.py
buscar_por_id(id_usuario) -> dict | None      # objeto "usuario" + chave interna "cpf" (11 dígitos), sem senha
usuario_json(usuario) -> dict                 # objeto "usuario" público (com cpf_mascarado, sem "cpf")

# src/backend/usuarios/validacao.py           # cada uma devolve (valor_normalizado, mensagem_de_erro | None)
validar_nome(valor); validar_matricula(valor); validar_email(valor); validar_cpf(valor); validar_senha(valor)

# src/backend/carteira/service.py
ajustar_saldo(id_usuario, valor_centavos, motivo, id_autor, chave_idempotencia) -> (movimentacao, carteira, criado: bool)

# src/backend/carteira/repository.py — para uso DENTRO de uma transação (recebem cursor dictionary=True)
bloquear_carteira(cursor, id_usuario) -> dict | None            # SELECT ... FOR UPDATE; {id_carteira, id_usuario, saldo_centavos, atualizado_em}
lancar_movimentacao(cursor, carteira, tipo, valor_centavos, descricao, id_autor,
                    id_compra=None, chave_idempotencia=None) -> dict   # atualiza o saldo, insere e devolve a movimentação (JSON)
```

`src/backend/seguranca.py`: `usuario_atual()`, `@login_obrigatorio`, `@somente_administrador`, `iniciar_sessao(usuario)`, `encerrar_sessao()`, `autor_auditoria()`.
`src/backend/http.py`: `ler_json()`, `data_utc(valor)`, `validar_chave_idempotencia(valor)`, `ler_limite(padrao, maximo)`.
`src/backend/erros.py`: `ErroValidacao(campos)`, `NaoEncontrado(msg)`, `ErroNegocio(msg, codigo=, detalhes=)`, `NaoAutenticado`, `SemPermissao`.
`src/backend/conexao.py`: `conectar()` e `transacao()` (context manager: commit no fim, rollback em erro).

## Frontend — objeto `Cantina` (`src/frontend/javascript/base.js`)

`requisitar(url, {method, json})`, `sessao()`, `atualizarSessao()`, `exigirLogin()`, `exigirAdministrador()`, `sair()`, `pronta()`, `destinoSeguro(destino, padrao)`, `formatarPreco`, `centavosParaTexto`, `textoParaCentavos`, `formatarDataHora`, `formatarData`, `novaChave()`, `somenteDigitos`, `ligarMascaraMoeda(campo)`, `ligarMascaraCpf(campo)`, `ligarSomenteDigitos(campo, maximo)`, `mascaraCpf`, `validarCpf`, `validarEmail`, `validarSenha`, `criarElemento(tag, classe, texto)`, `mostrarMensagem(elemento, texto, tipo)`, `exibirErros(formulario, erros)`, `limparErros(formulario)`, `ligarLimpezaDeErros(formulario)`, `bloquearEnvioPorEnter(formulario)`, `comBotaoOcupado(botao, texto, funcao)`, `atualizarSaldoCabecalho(centavos)`.

Padrão de página: `<div id="header-container"></div>`, `<main id="conteudo-principal">`, `<div id="footer-container"></div>`, `<script src="/javascript/base.js"></script>` antes do script da tela. Estilos compartilhados e variáveis de cor em `src/frontend/css/base.css` (seção "BASE COMPARTILHADA").

Padrão de formulário: `novalidate`; cada campo com `<small class="erro-campo" data-error-for="nome_do_campo">`; um `<p class="feedback-form" role="alert">`; validar no JavaScript antes de enviar; gravar **somente no clique do botão** (`Cantina.bloquearEnvioPorEnter`); mostrar os erros `campos` devolvidos pela API com `Cantina.exibirErros`.
