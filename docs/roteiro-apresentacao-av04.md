# Roteiro de apresentação da AV04

**Grupo 4 — 15/10/2026, às 20h40.**

Objetivo: demonstrar **Manter Produto** com banco de dados, incluindo cadastro, consulta, alteração e inativação, além de layout e validação dos campos. A API Flask/MySQL está pronta para integração; a equipe deve concluir e ensaiar a interface com o contrato do CRUD.

## Antes de apresentar

- [ ] Confirmar a stack com o grupo e atualizar os comandos de execução no README.
- [ ] Executar os [testes manuais](testes-manuais-av04.md) e corrigir falhas que impeçam a demonstração.
- [ ] Separar a versão que será apresentada e registrar seu commit.
- [ ] Preparar o ambiente local e um banco de desenvolvimento com dados fictícios.
- [ ] Reservar um código livre, como `CI-AV04-DEMO-001`, para cadastrar durante a apresentação.
- [ ] Abrir a aplicação e a ferramenta de consulta ao banco escolhido.
- [ ] Conferir a data do computador e preparar uma validade futura.
- [ ] Combinar quem apresenta, quem opera as telas e quem mostra os registros no banco.

A distribuição de falas fica a cargo da equipe. Todos devem conseguir explicar os quatro fluxos e as validações.

## Sequência da demonstração

| Etapa | Ação | O que mostrar |
| --- | --- | --- |
| 1. Contexto | Explicar que o administrador mantém os produtos da Cantina da Honestidade. | A funcionalidade escolhida para a AV04 e as telas que serão usadas. |
| 2. Incluir | Cadastrar o produto de exemplo dos testes manuais com o código reservado para a apresentação. | Confirmação, produto na lista e registro no banco. |
| 3. Consultar | Buscar pelo nome e pelo código; abrir os detalhes. | Dados recuperados do banco e filtros da listagem. |
| 4. Alterar | Mudar o preço de R$ 4,50 para R$ 5,00 e o estoque de 10 para 12. | Mesmo identificador, valores atualizados na tela e no banco. |
| 5. Validar | Tentar salvar preço zero; corrigir. Depois tentar cadastrar um código duplicado. | Mensagens junto aos campos, preservação do formulário e ausência de gravação inválida. |
| 6. Inativar | Acionar inativação e confirmar. Consultar os filtros de ativos e inativos. | Produto inativo, linha preservada no banco e histórico mantido. |
| 7. Reativar | Reativar o produto. | Retorno à lista de ativos com o mesmo identificador. |
| 8. Conferir persistência | Reiniciar a aplicação e consultar o produto novamente. | Dados preservados no mesmo banco e registros de auditoria das operações. |
| 9. Mostrar layout | Abrir o formulário e a lista em 360 × 800 px e em desktop. | Legibilidade, acesso às ações, mensagens de validação e ausência de rolagem horizontal. |

## Pontos para explicar

- **CRUD (50%):** cada operação demonstrada altera ou consulta dados persistidos no banco.
- **Layout e validação (50%):** os campos orientam o preenchimento e os erros aparecem de forma compreensível.
- **Exclusão adotada:** a inativação remove o produto da lista de ativos e preserva seu histórico, conforme a decisão registrada em [requisitos](requisitos-av04.md).
- **Auditoria:** mostrar inclusão, alteração, inativação e reativação com autor, origem, data/hora e valores antes/depois.
- **Stack:** apresentar as tecnologias efetivamente escolhidas pelo grupo e usadas na demonstração.

## Ensaio e ajustes

Cronometrar a sequência conforme o tempo disponibilizado pelo professor. Evitar instalar dependências ou preparar o banco durante a apresentação.

Se ocorrer uma falha no ensaio, registrar o passo e o resultado obtido na issue correspondente. Após corrigir, repetir o fluxo afetado e conferir a persistência.
