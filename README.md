# Cantina Inteligente — AV04 (Grupo 4)

Base de trabalho para apresentar **Manter Produto** com banco de dados. A stack definida pelo grupo é **Python + Flask + MySQL**. O backend fornece o CRUD de produtos, validações, persistência e auditoria.

## Entrega

Projeto Aplicado II do Centro Universitário SENAI Santa Catarina para a Cantina da Honestidade, unidade Fraiburgo (SC), Grupo 4. Apresentação da AV04: **15/10/2026 às 20h40**.

Acompanhe as tarefas no [Kanban AV04](https://github.com/orgs/senai-AEx/projects/1) e no [marco AV04 — CRUD de Produto](https://github.com/senai-AEx/cantinaInteligente/milestone/1).

## Executar localmente

É necessário ter **Python**, **Docker Desktop** e **GNU Make** instalados. No Windows, abra o Docker Desktop e espere o serviço ficar pronto. No terminal, entre na pasta principal do repositório — a que contém este README e `requirements.txt`.

Na primeira execução daquele computador:

```sh
make setup
```

Esse comando cria `.env` a partir de `.env.example` se ainda não existir e prepara o ambiente Python em `.venv`. O arquivo `.env` é local e não deve ser enviado ao GitHub. Os valores de exemplo usam a senha `masterkey` para desenvolvimento local; se o container MySQL existente tiver outra senha root, informe a senha atual em `MYSQL_ROOT_PASSWORD` no `.env`. O comando não apaga nem recria containers existentes.

Para iniciar o banco, aplicar as migrações pendentes e subir os servidores:

```sh
make up
```

O Make cria ou inicia o container `cantina-mysql` com o volume persistente `cantina-mysql-data`, aguarda o MySQL, aplica as migrações MySQL necessárias e inicia o Flask. Quando as telas estiverem presentes na branch, inicia também um servidor local para o frontend.

- API: http://127.0.0.1:5000/api/health
- Conexão com banco: http://127.0.0.1:5000/api/health/db
- Início: http://127.0.0.1:5500/
- Catálogo cliente: http://127.0.0.1:5500/html/catalogo_produtos.html
- Login: http://127.0.0.1:5500/html/login.html
- Cadastro: http://127.0.0.1:5500/html/cadastro.html
- Painel admin: http://127.0.0.1:5500/html/catalogo_produtos_adm.html

Mantenha o terminal aberto enquanto apresenta ou testa. `Ctrl+C` encerra os servidores Flask e frontend; o MySQL continua ligado. Para parar o container e preservar os dados, use `make down`. O volume não é removido por esses comandos.

### Comandos disponíveis

| Comando | Ação |
| --- | --- |
| `make help` | Lista os comandos |
| `make setup` | Prepara `.env` e o ambiente Python |
| `make up` | Inicia banco, migrações, API e frontend disponível |
| `make api` | Inicia banco, migrações e API |
| `make web` | Serve as telas em `http://127.0.0.1:5500` |
| `make db-up` | Inicia somente o MySQL |
| `make db-down` ou `make down` | Para somente o MySQL, preservando os dados |
| `make migrate` | Inicia o MySQL se necessário e confere/aplica migrações |
| `make status` | Mostra o estado do MySQL, Flask e frontend |
| `make test` | Executa os testes automatizados |

Se a porta `3306`, `5000` ou `5500` já estiver ocupada, encerre o serviço que a utiliza antes de iniciar. O frontend chama a API Flask; por isso, abra as telas pelo servidor local (porta `5500`), não diretamente como arquivo `file://`.

Cada integrante possui seu próprio banco local. Os dados cadastrados em um computador não aparecem automaticamente nos demais.

## Estrutura de produto e banco

O modelo comum está em [docs/modelo-produto.md](docs/modelo-produto.md), e as regras da entrega em [docs/requisitos-av04.md](docs/requisitos-av04.md). A tabela MySQL mantém código único, preço positivo em centavos, quantidades válidas, validade, foto, selos, situação e datas.

A exclusão da tela administrativa deve seguir o contrato da funcionalidade e preservar a auditoria. As migrações MySQL ficam em `database/migrations`; `001_produtos.sql` é específica para SQLite e não deve ser usada no MySQL. O Make aplica `002` e `003` e, se estiver presente na branch, também confere a `004` antes de aplicá-la, evitando repetir a alteração de auditoria.

## Rotas da API

- `GET /` — confirma que a API iniciou.
- `GET /api/health` — estado do Flask.
- `GET /api/health/db` — verifica a conexão MySQL com `SELECT 1`.
- `GET /api/produtos?q=&status=` — lista, busca e filtra produtos.
- `GET /api/produtos/<id>` — consulta detalhes.
- `POST /api/produtos` — cadastra produto.
- `PUT /api/produtos/<id>` — edita produto.
- `DELETE /api/produtos/<id>` — inativa produto.
- `PATCH /api/produtos/<id>/reativar` — reativa produto.
- `GET /api/produtos/<id>/auditoria` — consulta o histórico de alterações.

Para campos, exemplos de JSON e respostas de erro, consulte o [contrato do CRUD](docs/contrato-crud.md).

## Materiais da entrega

- [Decisões da stack e do produto](docs/decisoes.md)
- [Checklist manual](docs/testes-manuais-av04.md)
- [Roteiro da apresentação](docs/roteiro-apresentacao-av04.md)
- [Contribuição, branches e commits](CONTRIBUTING.md)

Faça operações administrativas em ambiente local; não publique a API sem autenticação e autorização.
