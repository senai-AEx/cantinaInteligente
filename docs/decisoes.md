# Decisões de projeto para a AV04

## Stack definida pelo grupo

A equipe definiu **Python + Flask + MySQL** para implementar e apresentar o CRUD de Produto.

| Camada | Escolha | Uso nesta entrega |
| --- | --- | --- |
| Backend | Python com Flask | API HTTP para a aplicação e a interface. |
| Banco de dados | MySQL 8.0.16 ou superior | Persistência relacional; as restrições CHECK precisam ser aplicadas. |
| Conector Python | MySQL Connector/Python | Abrir a conexão definida no arquivo local `.env`. |
| Valores monetários | Inteiro em centavos | Evitar erros de arredondamento. |
| Datas do backend | Sessão MySQL configurada em UTC | Datas de criação, alteração e auditoria. |

As variáveis ficam em `.env`, ignorado pelo Git. Use `.env.example` como referência e não versione credenciais. Consulte o [README](../README.md) para preparar o ambiente e executar as migrações.

## Produto e comportamento do CRUD

- **Código:** `codigo_produto` único; EAN/GTIN da embalagem ou código interno.
- **Campos:** nome, descrição, categoria, preço em centavos, saldo e limites de estoque, validade, caminho da foto, selos e situação. Regras completas em [modelo-produto.md](modelo-produto.md).
- **Exclusão:** inativação reversível (`status = INATIVO`), sem apagar o produto ou suas referências.
- **Auditoria:** cada inclusão, alteração, inativação e reativação deve registrar autor, origem, data/hora e valores antes/depois na mesma transação da mudança.
- **PWA:** interface responsiva está no escopo; instalação offline fica para depois do CRUD.

A migração `001_produtos.sql` é legada, exclusiva para SQLite. Para preparar um banco MySQL novo, aplique `002_produtos_mysql.sql` e depois `003_auditoria_produtos_mysql.sql` uma única vez.

## Estado do backend

A API Flask conecta ao MySQL e implementa listagem com busca/filtro, consulta por ID, cadastro, edição, inativação/reativação e consulta de auditoria. As operações de escrita validam os dados e registram produto e auditoria na mesma transação. A interface consome o contrato em [contrato-crud.md](contrato-crud.md); sua implementação continua com a equipe de frontend.

Todas as rotas administrativas de Produto devem ficar locais para a apresentação até que autenticação e autorização estejam implementadas. `X-Actor` identifica apenas o operador informado pela interface e não substitui login.
