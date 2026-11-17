# Arquitetura e organização das pastas

```
cantinaInteligente/
├── assets/produtos/        fotos enviadas pela tela (não versionadas)
├── database/
│   ├── migrations/         alterações incrementais, aplicadas pelo `make migrate`
│   ├── seeds/              dados fictícios (`make seed`)
│   └── schema.sql          esquema completo atual, para criar o banco do zero
├── docs/                   documentação do projeto (índice em docs/README.md)
├── scripts/                atalhos de desenvolvimento usados pelo Makefile
├── src/
│   ├── backend/            API Flask
│   │   ├── app.py          cria a aplicação, CORS, health check e registra os módulos
│   │   ├── conexao.py      conexão MySQL e transações
│   │   ├── uploads.py      upload das fotos
│   │   └── produtos/       módulo de produtos em camadas (ver abaixo)
│   └── frontend/           telas HTML/CSS/JS servidas na porta 5500
└── tests/                  testes automatizados (`make test`)
```

## Camadas do backend

Cada módulo de negócio (hoje, `produtos`) segue a mesma divisão, para que novos módulos — usuários, carteira, compras — sejam adicionados sem mexer nos existentes (RNF11):

| Arquivo | Responsabilidade |
| --- | --- |
| `routes.py` | Declara as URLs e os métodos HTTP. Não tem lógica. |
| `controller.py` | Lê a requisição (JSON, parâmetros, cabeçalhos), chama o serviço e converte o resultado ou o erro em resposta HTTP. |
| `service.py` | Regras de negócio: validação, selos automáticos, exclusão lógica, auditoria na mesma transação. |
| `validacao.py` | Regras de cada campo do formulário. |
| `repository.py` | Todo o SQL. Nenhuma outra camada fala com o banco. |

Fluxo de um cadastro: `POST /api/produtos` → `routes` → `controller.incluir_produto` → `service.incluir_produto` (valida, aplica selos, abre transação) → `repository.inserir` + `repository.registrar_auditoria` → commit.

Para criar um módulo novo, copie a estrutura de `src/backend/produtos/` e registre o blueprint em `app.py`.

## Frontend

HTML, CSS e JavaScript puros, sem build. Cada tela tem seu par `css/<tela>.css` e `javascript/<tela>.js`; `base.html/css/js` contêm cabeçalho e rodapé compartilhados. As telas chamam a API em `http://127.0.0.1:5000`.

## Banco de dados

MySQL 8 (Docker pelo `make up`, ou instalação local). Duas formas de preparar o banco:

1. **`make migrate`** (recomendado): aplica as migrações `002` a `005` em ordem, conferindo o que já foi aplicado. Atualiza bancos da AV04 sem perder dados.
2. **`database/schema.sql`**: cria o banco já no formato atual, para quem usa MySQL Workbench sem Docker. Em seguida, opcionalmente, `database/seeds/produtos_exemplo.sql`.
