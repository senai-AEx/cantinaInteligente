# Cantina Inteligente — Grupo 4

Sistema web para a **Cantina da Honestidade do SENAI Fraiburgo (SC)**: cadastro de produtos, catálogo para os clientes e, nas próximas entregas, usuários, carteira de créditos, compras e relatórios. Projeto Aplicado II — Centro Universitário SENAI Santa Catarina.

Stack: **Python + Flask + MySQL**, com HTML/CSS/JavaScript no frontend.

## Situação

- AV04 (CRUD de produto) apresentada em 15/10/2026 — nota 85/100.
- Devolutiva do produto aplicada na `develop` em 17/11/2026: código automático, preço de compra e de venda, só quantidade em estoque, sem validade, selos automáticos para frutas, gravação só pelo botão Salvar e exclusão lógica (o produto fica inativo e permanece no banco).
- Próximas entregas e prazos: [estado atual e próximas entregas](docs/estado-atual-e-proximas-entregas.md).

## Executar localmente

Pré-requisitos: **Python 3**, **Docker Desktop** e **GNU Make**. Abra o Docker Desktop e, no terminal, entre na pasta do repositório.

Primeira vez no computador:

```sh
make setup
```

Cria o `.env` a partir do `.env.example` (se não existir) e instala as dependências em `.venv`. O `.env` é local e não vai para o GitHub.

Para trabalhar:

```sh
make up
```

Inicia o MySQL (container `cantina-mysql`, dados no volume `cantina-mysql-data`), aplica as migrações pendentes e sobe a API e as telas. `Ctrl+C` para os servidores; o MySQL continua ligado até `make down`.

Para ter produtos de exemplo num banco vazio:

```sh
make seed
```

| Endereço | Tela |
| --- | --- |
| http://127.0.0.1:5500/ | Início |
| http://127.0.0.1:5500/html/catalogo_produtos.html | Catálogo do cliente |
| http://127.0.0.1:5500/html/catalogo_produtos_adm.html | Painel administrativo |
| http://127.0.0.1:5000/api/health/db | Teste de conexão da API com o banco |

### Comandos

| Comando | Ação |
| --- | --- |
| `make setup` | Prepara `.env` e o ambiente Python |
| `make up` | Banco + migrações + API + telas |
| `make api` / `make web` | Somente a API / somente as telas |
| `make migrate` | Aplica migrações pendentes (atualiza bancos da AV04) |
| `make seed` | Insere produtos de exemplo se a tabela estiver vazia |
| `make test` | Testes automatizados |
| `make status` | Mostra o que está rodando |
| `make down` | Para o MySQL preservando os dados |

### Sem Docker (MySQL instalado no computador)

1. No MySQL Workbench, execute [`database/schema.sql`](database/schema.sql) (e, se quiser, [`database/seeds/produtos_exemplo.sql`](database/seeds/produtos_exemplo.sql)).
2. Crie um usuário com acesso ao banco `cantina_inteligente` e informe-o no `.env` (`MYSQL_USER`, `MYSQL_PASSWORD`).
3. Rode a API e as telas:

```sh
.venv/Scripts/python -m flask --app src.backend.app run --debug
```

```sh
.venv/Scripts/python scripts/serve_frontend.py 5500
```

(No macOS/Linux, troque `.venv/Scripts/python` por `.venv/bin/python`.) Se o seu banco ainda está no formato da AV04, aplique [`database/migrations/005_produto_av05_mysql.sql`](database/migrations/005_produto_av05_mysql.sql) uma vez.

Abra as telas pelo servidor da porta 5500, não como arquivo `file://`. Cada integrante tem seu próprio banco local.

## Organização

```
assets/produtos/   fotos enviadas pela tela
database/          migrations/, seeds/ e schema.sql
docs/              documentação (índice em docs/README.md)
scripts/           atalhos usados pelo Makefile
src/backend/       API Flask (produtos em camadas: routes → controller → service → repository)
src/frontend/      telas HTML, CSS e JavaScript
tests/             testes automatizados
```

Detalhes em [docs/arquitetura.md](docs/arquitetura.md). A API está descrita em [docs/contrato-api-produtos.md](docs/contrato-api-produtos.md) e o modelo de produto em [docs/modelo-produto.md](docs/modelo-produto.md).

Ainda não há login: não publique a API fora do ambiente local antes de implementar autenticação e perfis.

## Equipe

Equipe 4 (integrantes listados no Documento do Sistema). Fluxo de trabalho em [CONTRIBUTING.md](CONTRIBUTING.md).
