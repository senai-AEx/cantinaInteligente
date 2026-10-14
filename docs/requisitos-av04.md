# Requisitos fechados para a AV04

## Objetivo da demonstração

A AV04 exige **incluir, alterar, consultar e excluir (ou inativar conforme RF)** uma funcionalidade integrada a banco de dados. Para o Grupo 4, a funcionalidade é **Manter Produto**. O enunciado divide a avaliação entre as quatro operações (50%) e o layout das telas com validação dos campos (50%). Apresentação: **15/10/2026, às 20h40**.

## Recorte dos documentos do grupo

| Fonte | Requisito considerado |
| --- | --- |
| AV03 RF02 | Administrador cadastra, consulta, edita e exclui produtos do estoque. |
| AV03 RF03 | Catálogo mostra nome, preço, validade, foto e selos alimentares quando aplicáveis. |
| AV03 RNF07 | Interface a partir de 360 × 800 px e desktop sem rolagem horizontal. |
| AV03 RNF09/RNF10 | Registrar alterações e evitar exclusões indevidas. |
| AV02 RF04 | Nome, categoria, preço, código, imagem, estoque mínimo/máximo e situação; código único, preço positivo, máximo ≥ mínimo. |
| AV02 RNF05/RNF09 | Dinheiro em centavos/decimal fixo e restrições de integridade no banco. |

A numeração dos RFs mudou entre AV02 e AV03. Esta especificação usa **RF02 da AV03** como requisito principal da AV04 e aproveita os critérios de produto da AV02.

## Comportamento escolhido

1. **Incluir:** formulário salva um produto válido; o registro aparece na lista e permanece após reiniciar a aplicação.
2. **Consultar:** lista com busca por nome/código e filtro por situação. Mostrar nome, código, categoria, preço, estoque, validade e situação; foto e selos quando informados.
3. **Alterar:** editar os campos do produto; a lista e o banco refletem os novos valores. Alteração de preço fica na auditoria.
4. **Excluir:** executar **inativação** com confirmação. O produto sai da lista de ativos e do catálogo disponível, permanece no banco e pode ser reativado.

Somente **Administrador** altera produtos. O catálogo de cliente é somente leitura. A implementação de autenticação e autorização deverá proteger as rotas administrativas quando o sistema ganhar login; não se deve expor o CRUD em uma implantação pública sem essa proteção.

## Aceite para a equipe conferir

- [ ] Inclusão, consulta, alteração e inativação/reativação funcionam com SQLite, inclusive após reiniciar a aplicação.
- [ ] Código duplicado, preço não positivo, estoque negativo e máximo menor que mínimo são recusados.
- [ ] Campos obrigatórios e data inválida têm mensagem junto ao campo; o banco também contém restrições para os dados que consegue validar.
- [ ] Inativar preserva o registro; a lista de ativos e o catálogo não o exibem.
- [ ] A interface funciona em 360 × 800 px e desktop sem rolagem horizontal.
- [ ] Cada inclusão, alteração, inativação e reativação gera registro de auditoria na mesma transação.

Fontes: `AV03_GRUPO_4.pdf`, `AV02_Cantina_Inteligente_Solucao_e_Requisitos.pdf` e enunciado da AV04.
