# Arquitetura e organização das pastas

A Cantina Inteligente é uma aplicação web cliente/servidor. Um único servidor Flask entrega as telas e a API na mesma porta (`http://127.0.0.1:5000`), e só ele acessa o MySQL. Os diagramas desta arquitetura estão em [diagramas/](diagramas/README.md) e no [Documento do Sistema](documento-do-sistema.md) (seções 7 e 8).

```
cantinaInteligente/
├── assets/produtos/        fotos enviadas pela tela (não versionadas)
├── database/
│   ├── migrations/         alterações incrementais (002 a 006), aplicadas pelo `make migrate`
│   ├── seeds/              produtos de exemplo (`make seed`)
│   └── schema.sql          esquema completo atual, para criar o banco do zero
├── docs/                   documentação do projeto (índice em docs/README.md)
├── scripts/                dev.py (atalhos do Makefile) e criar_admin.py (`make admin`)
├── src/
│   ├── backend/            aplicação Flask
│   │   ├── app.py          cria a aplicação, registra os módulos, entrega as telas e padroniza os erros
│   │   ├── conexao.py      conexão com o MySQL e transações
│   │   ├── seguranca.py    sessão de login e controle de acesso por perfil
│   │   ├── erros.py        erros de negócio convertidos em respostas JSON
│   │   ├── http.py         leitura do JSON, datas em UTC, chave de idempotência
│   │   ├── uploads.py      upload das fotos dos produtos
│   │   ├── usuarios/       cadastro e login (/api/auth)
│   │   ├── produtos/       cadastro e catálogo de produtos (/api/produtos)
│   │   ├── carteira/       saldo, extrato e créditos (/api/carteira)
│   │   ├── compras/        registro e histórico de compras (/api/compras)
│   │   └── admin/          usuários, movimentações e relatórios (/api/admin)
│   └── frontend/           telas HTML, CSS e JavaScript, servidas pelo próprio Flask
└── tests/                  testes automatizados (`make test`)
```

## Um servidor, uma porta

O `app.py` responde a dois tipos de pedido:

- `/api/...` — a API em JSON, usada pelas telas;
- qualquer outro caminho — os arquivos de `src/frontend` (telas, CSS e JavaScript) e as fotos em `/assets/produtos/...`.

Como as telas e a API têm a mesma origem, o login funciona por cookie de sessão, sem CORS e sem guardar token no navegador. Nas telas, use sempre caminhos relativos (`/api/...`, `/html/...`).

## Camadas do backend

Cada módulo de negócio segue a mesma divisão. Um módulo novo é adicionado sem alterar os existentes (RNF09 do Documento do Sistema).

| Arquivo | Responsabilidade |
| --- | --- |
| `routes.py` | Declara as URLs e os métodos HTTP. Não tem lógica. |
| `controller.py` | Exige login ou perfil (decoradores de `seguranca.py`), lê a requisição, chama o serviço e monta a resposta. |
| `service.py` | Regras de negócio e controle da transação. |
| `validacao.py` | Regras de cada campo (quando o módulo tem formulário). |
| `repository.py` | Todo o SQL. Nenhuma outra camada fala com o banco. |

Caminho de uma requisição: `routes → controller → service → repository → MySQL`. Os serviços lançam os erros de `erros.py` e o `app.py` os converte em JSON; os controllers não precisam de `try/except`.

Para criar um módulo novo, copie a estrutura de um existente e registre o blueprint em `app.py`.

## Módulos

| Módulo | Rotas | Acesso | Responsabilidade |
| --- | --- | --- | --- |
| `usuarios` | `/api/auth/cadastro`, `/login`, `/logout`, `/eu` | Público | Cadastro (perfil Cliente e carteira com saldo zero na mesma transação), login por matrícula, e-mail ou CPF, sessão. |
| `produtos` | `/api/produtos` | Consulta pública; gravação só para Administrador | CRUD com exclusão lógica, selos automáticos e auditoria. |
| `uploads.py` | `/api/uploads/produtos` | Administrador | Recebe a foto do produto (JPG, PNG ou WebP até 5 MB). |
| `carteira` | `/api/carteira`, `/movimentacoes`, `/creditos` | Login obrigatório | Saldo, extrato e crédito declarado pelo usuário. |
| `compras` | `/api/compras` | Login obrigatório | Registro da compra (estoque, saldo e movimentação em uma transação) e histórico. |
| `admin` | `/api/admin/usuarios`, `/movimentacoes`, `/relatorios/...` | Administrador | Gestão de usuários, ajuste de saldo, movimentações com filtros e relatórios de vendas, saldos e estoque. O relatório de depósitos declarados da tela usa a consulta de movimentações do tipo `CREDITO`. |

O detalhe de cada rota está no [contrato da API](contrato-api.md) e na [API de produtos](contrato-api-produtos.md).

### Dependências entre módulos

Cada módulo usa o próprio `repository`. As exceções, combinadas no contrato, são:

- `compras` usa `carteira.repository` (`bloquear_carteira` e `lancar_movimentacao`) para debitar o saldo dentro da transação da compra;
- `admin` usa `carteira.service.ajustar_saldo` para lançar ajustes e as validações de `usuarios` para editar cadastros;
- `seguranca.py` usa `usuarios.repository.buscar_por_id` para reler o usuário logado.

## Sessão e perfis

- O login grava um cookie de sessão assinado (`cantina_sessao`), `HttpOnly` e `SameSite=Lax`, válido por 8 horas. A chave que assina o cookie é a `SECRET_KEY` do `.env`.
- O cookie guarda só o `id_usuario`. A cada requisição o usuário é relido do banco: quem é inativado ou perde o perfil de administrador perde o acesso na hora.
- Perfis: `CLIENTE` (todo cadastro feito pela tela) e `ADMINISTRADOR` (o primeiro é criado por `make admin`, com os dados `ADMIN_*` do `.env`).
- Nos controllers, `@login_obrigatorio` responde `401` para quem não está logado e `@somente_administrador` responde `403` para quem não é administrador.
- A senha é guardada apenas como hash (`werkzeug.security`). A API nunca devolve a senha e devolve o CPF mascarado.
- Nas telas, `Cantina.exigirLogin()` e `Cantina.exigirAdministrador()` redirecionam quem não tem acesso. Isso é só conveniência: a proteção de verdade está no servidor.

## Transações e consistência

Compra, crédito e ajuste alteram o saldo dentro de uma transação (`conexao.transacao()`): confirma tudo no fim ou desfaz tudo em caso de erro.

Passos de `POST /api/compras`:

1. valida os itens e a chave de idempotência;
2. abre a transação e trava a carteira do usuário (`SELECT ... FOR UPDATE`);
3. se a chave já gerou uma compra, devolve essa mesma compra (status `200`);
4. trava os produtos em ordem crescente de `id_produto`;
5. confere se os produtos estão ativos, o estoque e o saldo;
6. grava a compra e os itens (com o preço de venda e o custo do momento), baixa o estoque e lança a movimentação `DEBITO`;
7. confirma a transação e responde `201`.

A carteira é sempre travada antes dos produtos, e os produtos sempre na mesma ordem, para duas compras simultâneas não ficarem uma esperando a outra. Restrições do banco (`CHECK`) recusam saldo negativo, estoque negativo e subtotal incorreto, mesmo que a aplicação falhe.

**Idempotência:** a tela gera um UUID por operação (`Cantina.novaChave()`); as colunas `chave_idempotencia` de `compras` e `movimentacoes` são únicas. Reenviar a mesma chave devolve o registro já gravado, sem duplicar.

## Frontend

HTML, CSS e JavaScript puros, sem etapa de build. Cada tela tem seu par `css/<tela>.css` e `javascript/<tela>.js`. O `base.html` contém o cabeçalho e o rodapé compartilhados, e o `base.js` expõe o objeto `Cantina`, com as chamadas à API, a sessão, as máscaras (CPF e moeda), as validações e a exibição de erros nos formulários.

| Tela | Arquivo | Acesso |
| --- | --- | --- |
| Início | `index.html` | Público |
| Catálogo e sacola | `html/catalogo_produtos.html` | Público; finalizar a compra exige login |
| Criar conta | `html/cadastro.html` | Público |
| Entrar | `html/login.html` | Público |
| Minha conta (saldo, crédito, extrato e compras) | `html/minha_conta.html` | Login |
| Painel — produtos | `html/catalogo_produtos_adm.html` | Administrador |
| Painel — usuários | `html/usuarios_adm.html` | Administrador |
| Painel — movimentações | `html/movimentacoes_adm.html` | Administrador |
| Painel — relatórios | `html/relatorios_adm.html` | Administrador |

Padrão dos formulários: validação no JavaScript antes de enviar, mensagem de erro junto ao campo, gravação somente pelo clique no botão (Enter não envia) e exibição dos erros `campos` devolvidos pela API.

## Banco de dados

MySQL 8 (contêiner Docker `cantina-mysql` pelo `make up`, ou instalação local). O modelo completo está na seção 6 do [Documento do Sistema](documento-do-sistema.md) e em [diagramas/mer.mmd](diagramas/mer.mmd).

| Tabela | Conteúdo |
| --- | --- |
| `tipos_usuario` | Perfis: Administrador e Cliente. |
| `usuarios` | Cadastro e login; matrícula, CPF e e-mail únicos; senha como hash. |
| `carteiras` | Uma por usuário; `saldo_centavos` nunca negativo. |
| `movimentacoes` | Extrato: `CREDITO`, `DEBITO` ou `AJUSTE`, com valor, saldo após, autor e data. |
| `compras` e `itens_compra` | Compras e seus itens, com preço e custo do momento. |
| `produtos` | Produtos com preço de compra, preço de venda, estoque e situação. |
| `auditoria_produtos` | Histórico das alterações de produtos, com antes e depois. |

Dinheiro é sempre guardado em centavos inteiros e as datas em UTC.

Duas formas de preparar o banco:

1. **`make migrate`** (recomendado; o `make up` já faz): aplica as migrações `002` a `006` em ordem, conferindo o que já foi aplicado. Atualiza bancos antigos sem perder dados.
2. **`database/schema.sql`**: cria o banco já no formato atual, para quem usa o MySQL Workbench sem Docker.

Toda mudança no banco entra como uma migração nova e também no `schema.sql`.
