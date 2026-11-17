# Cantina Inteligente — Grupo 4

Sistema web para a **Cantina da Honestidade do SENAI Fraiburgo (SC)**. O usuário se cadastra, declara os depósitos que fez na caixa da cantina (créditos em uma carteira virtual) e registra as próprias compras, que são descontadas do saldo. A administração gerencia produtos e usuários, acompanha as movimentações e emite relatórios.

Projeto Aplicado II — Centro Universitário SENAI Santa Catarina. Stack: **Python + Flask + MySQL**, com telas em HTML, CSS e JavaScript.

## O que o sistema faz

| Para o cliente | Para a administração |
| --- | --- |
| Cadastro e login por matrícula, e-mail ou CPF | Cadastro de produtos (preço de compra e de venda, estoque, foto) |
| Catálogo com preços e sacola de compras | Gestão de usuários (editar, inativar, ajustar saldo) |
| Carteira: adicionar crédito e consultar saldo e extrato | Movimentações financeiras com filtros |
| Compra com desconto automático do saldo e baixa do estoque | Relatórios de vendas, saldos, estoque e depósitos declarados |
| Histórico de compras | Auditoria das alterações de produtos |

Nada é apagado do banco: excluir um produto ou um usuário apenas o deixa inativo.

## Executar localmente

Pré-requisitos: **Python 3**, **Docker Desktop** (aberto) e **GNU Make**. No terminal, dentro da pasta do repositório:

```sh
make setup
```

Cria o `.env` a partir do `.env.example` (ou completa o seu com as chaves novas), gera a chave de sessão e a senha do administrador de demonstração, e instala as dependências em `.venv`. O `.env` é só seu e não vai para o GitHub.

```sh
make up
```

Inicia o MySQL (container `cantina-mysql`, dados no volume `cantina-mysql-data`), aplica as migrações pendentes e sobe o sistema em **http://127.0.0.1:5000**. `Ctrl+C` para o servidor; o MySQL continua ligado até `make down`.

Na primeira vez, em outro terminal:

```sh
make seed
```

```sh
make admin
```

O primeiro insere produtos de exemplo; o segundo cria o administrador de demonstração com os dados `ADMIN_*` do seu `.env` (a matrícula e a senha estão lá).

| Endereço | Tela |
| --- | --- |
| http://127.0.0.1:5000/ | Início |
| http://127.0.0.1:5000/html/catalogo_produtos.html | Catálogo e sacola |
| http://127.0.0.1:5000/html/cadastro.html | Criar conta |
| http://127.0.0.1:5000/html/login.html | Entrar |
| http://127.0.0.1:5000/html/minha_conta.html | Saldo, créditos, extrato e compras |
| http://127.0.0.1:5000/html/catalogo_produtos_adm.html | Painel administrativo |
| http://127.0.0.1:5000/api/health/db | Teste da conexão com o banco |

### Comandos

| Comando | Ação |
| --- | --- |
| `make setup` | Prepara o `.env` e o ambiente Python |
| `make up` | Banco + migrações + sistema |
| `make admin` | Cria ou redefine o administrador (dados `ADMIN_*` do `.env`) |
| `make seed` | Insere produtos de exemplo se a tabela estiver vazia |
| `make migrate` | Aplica migrações pendentes |
| `make test` | Testes automatizados |
| `make status` | Mostra o que está rodando |
| `make down` | Para o MySQL preservando os dados |

### Problemas comuns

- **"A porta 3306 já está em uso"**: há outro MySQL no computador. Troque `MYSQL_PORT` para `3307` no `.env` e rode `make up` de novo.
- **"Não consegui acessar o Docker"**: abra o Docker Desktop e espere ele ficar pronto.
- **Login cai ao reiniciar o servidor**: falta `SECRET_KEY` no `.env`; rode `make setup`.

### Sem Docker (MySQL instalado no computador)

1. No MySQL Workbench, execute [`database/schema.sql`](database/schema.sql) e, se quiser, [`database/seeds/produtos_exemplo.sql`](database/seeds/produtos_exemplo.sql).
2. Crie um usuário do MySQL com acesso ao banco `cantina_inteligente` e informe-o no `.env` (`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_PORT`).
3. Rode `make setup` e depois:

```sh
.venv/Scripts/python scripts/criar_admin.py
```

```sh
.venv/Scripts/python -m flask --app src.backend.app run --debug
```

(No macOS/Linux, troque `.venv/Scripts/python` por `.venv/bin/python`.)

## Organização

```
assets/produtos/   fotos enviadas pela tela (não versionadas)
database/          migrations/, seeds/ e schema.sql
docs/              documentação (índice em docs/README.md)
scripts/           atalhos usados pelo Makefile
src/backend/       API Flask: usuarios, produtos, carteira, compras e admin,
                   cada módulo em camadas routes → controller → service → repository
src/frontend/      telas HTML, CSS e JavaScript (servidas pelo próprio Flask)
tests/             testes automatizados
```

- [Arquitetura e pastas](docs/arquitetura.md)
- [Contrato da API](docs/contrato-api.md) e [API de produtos](docs/contrato-api-produtos.md)
- [Documento do Sistema](docs/documento-do-sistema.md)
- [Roteiro de testes manuais](docs/testes-manuais.md)
- [Plano de execução AV05/AV06](docs/plano-de-execucao.md)

## Segurança

- Senhas guardadas apenas como hash; sessão por cookie `HttpOnly`.
- As rotas administrativas exigem perfil de administrador no servidor (não basta esconder o botão na tela).
- Compra e crédito acontecem em transação: saldo, estoque e extrato nunca ficam em desacordo.
- O ambiente local usa credenciais de demonstração. Antes de publicar em um servidor real, troque as senhas do `.env` e sirva o sistema por HTTPS.

## Equipe

Equipe 4 (integrantes listados no Documento do Sistema). Fluxo de trabalho em [CONTRIBUTING.md](CONTRIBUTING.md).
