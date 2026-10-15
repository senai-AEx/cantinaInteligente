# Cantina Inteligente — AV04 (Grupo 4)

Base de trabalho para apresentar **Manter Produto** com banco de dados. A stack definida pelo grupo é **Python + Flask + MySQL**. O backend fornece o CRUD de produto, validações, persistência e auditoria; a interface permanece com a equipe de frontend.

## Entrega

Projeto Aplicado II do Centro Universitário SENAI Santa Catarina para a Cantina da Honestidade, unidade Fraiburgo (SC), Grupo 4. Apresentação da AV04: **15/10/2026 às 20h40**.

Acompanhe as tarefas no [Kanban AV04](https://github.com/orgs/senai-AEx/projects/1) e no [marco AV04 — CRUD de Produto](https://github.com/senai-AEx/cantinaInteligente/milestone/1).

## Estrutura de Produto

O modelo comum está em [docs/modelo-produto.md](docs/modelo-produto.md); as regras da entrega estão em [docs/requisitos-av04.md](docs/requisitos-av04.md). A tabela MySQL mantém código único, preço positivo em centavos, quantidades válidas, validade, foto, selos, situação e datas. A exclusão do CRUD será inativação para preservar o produto e a auditoria.

A migração antiga `001_produtos.sql` é específica para **SQLite**. Para a stack do grupo, use as migrações MySQL `002_produtos_mysql.sql`, `003_auditoria_produtos_mysql.sql` e `004_auditoria_exclusao_mysql.sql`, nessa ordem.

## Preparar o ambiente no Windows

Faça a preparação inicial uma vez por computador. Os comandos abaixo devem ser executados no PowerShell, na pasta principal do repositório (a que contém `requirements.txt`). Para acompanhar o frontend chamando a API, use o VS Code com a extensão Live Server ou Vite.

### 1. Instalar as dependências Python

Confirme que o Python está instalado e crie o ambiente virtual do projeto:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Se `python` não for reconhecido, instale o Python e abra um novo PowerShell. O ambiente `.venv` e as dependências não precisam ser recriados a cada execução.

### 2. Preparar o MySQL

O caminho recomendado para desenvolvimento é Docker Desktop com MySQL 8.4. Abra o Docker Desktop e espere ele iniciar.

Se já existir um container chamado `cantina-mysql`, inicie-o:

```powershell
docker start cantina-mysql
```

Se ainda não existir, crie-o uma única vez:

```powershell
docker run --name cantina-mysql -e MYSQL_ROOT_PASSWORD=rootCantinaLocal123! -e MYSQL_DATABASE=cantina_inteligente -e MYSQL_USER=cantina_app -e MYSQL_PASSWORD=appCantinaLocal123! -p 3306:3306 -d mysql:8.4
```

As senhas acima são exemplos apenas para desenvolvimento local. Se você já tiver um container, não o recrie: use no `.env` a senha configurada nele. Se a porta `3306` estiver ocupada, será necessário liberar essa porta ou mapear outra porta do computador e usar o mesmo número em `MYSQL_PORT` no `.env`.

### 3. Configurar a conexão da aplicação

Crie o arquivo local `.env` a partir do exemplo e abra para edição:

```powershell
Copy-Item .env.example .env
notepad .env
```

Para o container criado no passo anterior, deixe os valores assim:

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=cantina_inteligente
MYSQL_USER=cantina_app
MYSQL_PASSWORD=appCantinaLocal123!
```

Salve o arquivo. Ele é ignorado pelo Git; não o envie ao GitHub.

### 4. Criar as tabelas do banco

Faça este passo uma única vez para cada banco. Em um banco novo, execute as três migrações na ordem. Se `produtos` e `auditoria_produtos` já existem, execute somente a migração `004` para habilitar a exclusão definitiva e manter a auditoria.

Para um banco novo, na pasta principal do projeto, copie os três arquivos para o container e conecte como root:

```powershell
docker cp .\database\migrations\002_produtos_mysql.sql cantina-mysql:/tmp/002_produtos_mysql.sql
docker cp .\database\migrations\003_auditoria_produtos_mysql.sql cantina-mysql:/tmp/003_auditoria_produtos_mysql.sql
docker cp .\database\migrations\004_auditoria_exclusao_mysql.sql cantina-mysql:/tmp/004_auditoria_exclusao_mysql.sql
docker exec -it cantina-mysql mysql -u root -p
```

Digite a senha de root do container. No prompt `mysql>`, rode cada linha para um banco novo:

```sql
source /tmp/002_produtos_mysql.sql;
source /tmp/003_auditoria_produtos_mysql.sql;
source /tmp/004_auditoria_exclusao_mysql.sql;
SHOW TABLES;
exit;
```

Devem aparecer `produtos` e `auditoria_produtos`. Não execute as migrações novamente nesse mesmo banco.

Se as duas tabelas já existem, copie e execute **somente** a migração 004:

```powershell
docker cp .\database\migrations\004_auditoria_exclusao_mysql.sql cantina-mysql:/tmp/004_auditoria_exclusao_mysql.sql
docker exec -it cantina-mysql mysql -u root -p
```

No prompt `mysql>`, rode:

```sql
source /tmp/004_auditoria_exclusao_mysql.sql;
exit;
```

A migração `004` remove a restrição que impediria excluir um produto e amplia as ações de auditoria; os registros históricos são preservados. `001_produtos.sql` é uma migração antiga de SQLite.

### 5. Iniciar o backend (faça isso quando for testar)

Em um PowerShell na pasta principal do projeto, inicie o container se estiver parado e depois a API:

```powershell
docker start cantina-mysql
.\.venv\Scripts\python.exe -m flask --app src.backend.app run --debug
```

Se o Docker responder que o container já está em execução, pode seguir. Deixe essa janela aberta enquanto usa a API. Para parar o Flask, pressione `Ctrl+C` nessa janela.

### 6. Iniciar o frontend e testar a conexão

Abra o frontend pelo Live Server do VS Code (normalmente `http://localhost:5500`) ou pelo Vite (normalmente `http://localhost:5173`). Não abra o HTML diretamente como arquivo (`file://`): o navegador precisa servir a tela por uma dessas origens para a chamada à API funcionar.

Com o Flask aberto, visite estes endereços:

- `http://127.0.0.1:5000/api/health` — confirma que o Flask iniciou.
- `http://127.0.0.1:5000/api/health/db` — confirma a conexão MySQL; a resposta deve indicar `"banco": "conectado"` e `"resultado": 1`.

Se o segundo endereço falhar, confira se o container está rodando e se usuário, senha e porta no `.env` correspondem ao MySQL local. Cada pessoa tem seu próprio banco local: os dados cadastrados no computador de uma integrante não aparecem automaticamente no computador das outras.

A preparação do Python, do `.env` e das tabelas é feita uma vez por computador/banco. Nas próximas sessões, basta iniciar o Docker, iniciar o Flask e abrir o frontend pelo servidor local.

### Rotas da API

Com o backend iniciado, estas rotas ficam disponíveis:

- `GET /` — mensagem de que a API iniciou.
- `GET /api/health` — saúde do Flask.
- `GET /api/health/db` — verifica a conexão MySQL com `SELECT 1`.
- `GET /api/produtos?q=&status=` — lista, busca e filtra produtos.
- `GET /api/produtos/<id>` — consulta detalhes.
- `POST /api/produtos` — cadastra produto.
- `PUT /api/produtos/<id>` — edita produto.
- `PATCH /api/produtos/<id>/inativar` — tira do catálogo, mantendo o produto para reativação.
- `PATCH /api/produtos/<id>/reativar` — reativa produto.
- `DELETE /api/produtos/<id>` — exclui definitivamente o produto e preserva o histórico de auditoria.
- `GET /api/produtos/<id>/auditoria` — consulta o histórico de alterações.

Para nomes de campos, exemplos de JSON e regras de erro, consulte o [contrato da API](docs/contrato-crud.md). Faça operações administrativas em ambiente local; não publique a API sem autenticação e autorização.

## Decisões e materiais da entrega

- [Decisões da stack e do produto](docs/decisoes.md)
- [Contrato do CRUD](docs/contrato-crud.md)
- [Checklist manual](docs/testes-manuais-av04.md)
- [Roteiro da apresentação](docs/roteiro-apresentacao-av04.md)
- [Contribuir: branches, commits e PRs](CONTRIBUTING.md)

As telas e o ensaio integrado seguem com a equipe de frontend. Use o [checklist manual](docs/testes-manuais-av04.md) para conferir inclusão, consulta, edição, inativação, reativação, persistência e validações antes da apresentação.
