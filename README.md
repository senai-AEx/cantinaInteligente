# Cantina Inteligente — AV04 (Grupo 4)

Base de trabalho para apresentar **Manter Produto** com banco de dados. A stack definida pelo grupo é **Python + Flask + MySQL**. Esta branch prepara o backend, a conexão, as tabelas e a consulta inicial de produtos; as demais operações do CRUD e as telas continuam nas issues seguintes.

## Entrega

Projeto Aplicado II do Centro Universitário SENAI Santa Catarina para a Cantina da Honestidade, unidade Fraiburgo (SC), Grupo 4. Apresentação da AV04: **15/10/2026 às 20h40**.

Acompanhe as tarefas no [Kanban AV04](https://github.com/orgs/senai-AEx/projects/1) e no [marco AV04 — CRUD de Produto](https://github.com/senai-AEx/cantinaInteligente/milestone/1).

## Estrutura de Produto

O modelo comum está em [docs/modelo-produto.md](docs/modelo-produto.md); as regras da entrega estão em [docs/requisitos-av04.md](docs/requisitos-av04.md). A tabela MySQL mantém código único, preço positivo em centavos, quantidades válidas, validade, foto, selos, situação e datas. A exclusão do CRUD será inativação para preservar o produto e a auditoria.

A migração antiga `001_produtos.sql` é específica para **SQLite**. Para a stack do grupo, use somente as migrações MySQL `002_produtos_mysql.sql` e `003_auditoria_produtos_mysql.sql`, nessa ordem.

## Preparar o ambiente no Windows

No PowerShell, na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Abra `.env` no editor e preencha as credenciais do seu MySQL local. Mantenha esse arquivo local: o Git o ignora.

O exemplo usa MySQL em Docker com container chamado `cantina-mysql` e a porta local `3306`:

```powershell
docker start cantina-mysql
```

Para criar as tabelas em uma instalação nova, copie as duas migrações para o container e aplique uma única vez. A segunda depende da primeira:

```powershell
docker cp .\database\migrations\002_produtos_mysql.sql cantina-mysql:/tmp/002_produtos_mysql.sql
docker cp .\database\migrations\003_auditoria_produtos_mysql.sql cantina-mysql:/tmp/003_auditoria_produtos_mysql.sql
docker exec -it cantina-mysql mysql -u root -p
```

No prompt do MySQL, digite a senha de root e execute:

```sql
source /tmp/002_produtos_mysql.sql;
source /tmp/003_auditoria_produtos_mysql.sql;
SHOW TABLES;
exit;
```

Isso cria o banco `cantina_inteligente` e as tabelas `produtos` e `auditoria_produtos`. Não rode as migrações de novo: os índices já terão sido criados.

## Executar

Com MySQL ligado, migrações aplicadas e `.env` preenchido:

```powershell
.\.venv\Scripts\python.exe -m flask --app src.backend.app run --debug
```

Rotas disponíveis nesta etapa:

- `GET /` — mensagem de que a API iniciou.
- `GET /api/health` — saúde do Flask.
- `GET /api/health/db` — verifica a conexão MySQL com `SELECT 1`.
- `GET /api/produtos` — consulta a lista de produtos.

Para verificar a conexão, acesse [http://127.0.0.1:5000/api/health/db](http://127.0.0.1:5000/api/health/db). A resposta esperada inclui `"banco": "conectado"` e `"resultado": 1`. A lista de produtos retorna vazia se ainda não houver itens.

## Decisões e próximas entregas

- [Decisões da stack e do produto](docs/decisoes.md)
- [Contrato do CRUD](docs/contrato-crud.md)
- [Checklist manual](docs/testes-manuais-av04.md)
- [Roteiro da apresentação](docs/roteiro-apresentacao-av04.md)
- [Contribuir: branches, commits e PRs](CONTRIBUTING.md)

As operações de cadastrar, consultar por ID, editar, inativar/reativar, auditoria pela API, validação de payload e telas seguem nas issues **02–05**. Não publique o backend administrativo em uma rede pública sem autenticação e autorização.