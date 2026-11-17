> **Registro histórico da AV04 (15/10/2026).** Descreve o modelo antigo de produto. O modelo atual está em [modelo-produto.md](../../modelo-produto.md).

> **Situação em 16/10/2026:** 5 testes automatizados locais passaram (upload e exclusão/auditoria). CRUD integrado ao MySQL e responsividade ainda não têm evidências. A exclusão física presente no código é legado e não deve ser demonstrada como regra aprovada; veja [issue #10](https://github.com/senai-AEx/cantinaInteligente/issues/10).

# Testes manuais da AV04

Checklist para executar quando o CRUD estiver implementado. **Nenhum caso abaixo foi executado nesta base de estrutura.** Os passos são independentes da linguagem, do framework e do banco escolhido.

Referências: [requisitos](requisitos-av04.md), [modelo de Produto](../../modelo-produto.md) e [contrato do CRUD](../../contrato-api-produtos.md).

## Preparação e registro

- Usar um banco de desenvolvimento, com dados fictícios.
- Confirmar a stack e seguir os comandos de instalação e execução que a equipe documentar no README.
- Preparar acesso de consulta ao banco para conferir persistência e auditoria.
- Registrar o commit testado e usar um código de produto ainda não cadastrado.

| Informação | Preenchimento pela equipe |
| --- | --- |
| Data e responsável | A preencher |
| Commit testado | A preencher |
| Navegador e tamanho de tela | A preencher |
| Ambiente e banco utilizado | A preencher |

Marque a caixa somente quando o resultado esperado for observado. Para falhas, registre o ID do caso, os passos, o resultado obtido e a issue de correção. Casos ainda impossíveis de executar ficam pendentes.

## Produto de exemplo

| Campo | Valor |
| --- | --- |
| Código | `CI-AV04-001` (ou outro código livre) |
| Nome | Suco de uva 200 ml |
| Descrição | Produto fictício para demonstração |
| Categoria | Bebidas |
| Preço | R$ 4,50 |
| Estoque | 10 |
| Mínimo / máximo | 3 / 20 |
| Validade | Data válida, pelo menos 30 dias após o teste |
| Foto | Opcional; usar uma imagem local de demonstração |
| Selos | Zero lactose marcado; zero açúcar desmarcado |
| Situação inicial | Ativo |

## CRUD e persistência (50% da avaliação)

Executar na ordem, usando o mesmo produto e seu identificador.

- [ ] **T01 — Incluir:** cadastrar o produto válido. Ele aparece na lista e no banco com os valores informados, situação ativa e um identificador.
- [ ] **T02 — Consultar:** buscar pelo nome e pelo código; abrir os detalhes. Conferir preço, estoque, validade, situação e selos. Uma busca sem correspondência mostra uma mensagem de lista vazia.
- [ ] **T03 — Alterar:** mudar o preço para R$ 5,00 e o estoque para 12. Salvar e abrir novamente. O identificador é o mesmo, os valores estão atualizados e nenhum produto extra foi criado.
- [ ] **T04 — Cancelar inativação:** acionar inativar e cancelar a confirmação. O produto continua ativo.
- [ ] **T05 — Inativar:** confirmar a ação. O produto sai da consulta filtrada por ativos e aparece no filtro de inativos. A linha permanece no banco com situação inativa.
- [ ] **T06 — Reativar:** reativar o produto. Ele volta ao filtro de ativos, preservando identificador e dados.
- [ ] **T07 — Persistir:** reiniciar a aplicação usando o mesmo banco. Consultar novamente e conferir os valores finais, o identificador e o histórico.

## Validação dos campos e layout (50% da avaliação)

Em cada tentativa inválida, conferir que nada foi gravado e que os outros campos preenchidos foram preservados.

- [ ] **T08 — Obrigatórios e limites:** testar código vazio, nome vazio ou somente espaços, nome com 1 ou mais de 100 caracteres e categoria vazia. Mostrar mensagem junto ao campo correspondente.
- [ ] **T09 — Código único:** tentar cadastrar outro produto com o código de T01. Recusar sem duplicar o registro.
- [ ] **T10 — Preço:** tentar zero, valor negativo e texto inválido. Recusar os valores e exibir orientação. Um preço válido deve aparecer em reais com duas casas decimais.
- [ ] **T11 — Estoque:** testar valores negativos e fracionados em quantidade, mínimo e máximo; testar máximo menor que mínimo. Recusar. Aceitar quantidade zero e máximo igual ao mínimo.
- [ ] **T12 — Validade e opcionais:** rejeitar data inexistente, como `2026-02-30`. Aceitar validade, descrição e foto não informadas, pois são opcionais.
- [ ] **T12A — Foto do produto:** selecionar JPG, PNG e WebP válidos; conferir prévia antes de salvar e imagem no catálogo. Recusar formatos não suportados e arquivos acima de 5 MB, mantendo os demais dados digitados.
- [ ] **T13 — Validação no servidor:** enviar uma requisição inválida diretamente à API, sem depender da validação da tela. Exemplos: preço zero, código duplicado e data inexistente. Esperar HTTP 422 com mensagens por campo e nenhuma gravação.
- [ ] **T14 — Celular e desktop:** conferir listagem, formulário e confirmação em 360 × 800 px e em desktop. Não deve haver rolagem horizontal; rótulos, mensagens e botões precisam estar legíveis e acessíveis.
- [ ] **T15 — Feedback:** conferir mensagens de sucesso e erro; navegação pelo teclado com foco visível; abrir edição sem perder os valores já salvos.

## Integridade e critérios complementares

- [ ] **T16 — Auditoria:** consultar o histórico de T01, T03, T05 e T06. Conferir ação, produto, autor, origem, data/hora e valores antes/depois. Tentativas rejeitadas não devem criar uma operação bem-sucedida no histórico.
- [ ] **T17 — Registro inexistente:** consultar ou alterar pela API um identificador que não existe. Esperar HTTP 404, sem criar produto ou alterar outro registro.
- [ ] **T18 — Catálogo, quando disponível:** um produto inativo, sem estoque ou vencido não aparece no catálogo disponível, mas continua consultável pela administração. Se a tela de catálogo ainda não fizer parte da entrega, registrar como pendente.
- [ ] **T19 — Excluir definitivamente:** cadastrar um segundo produto descartável, usar a ação “Excluir definitivamente” e confirmar o aviso. O produto deve sumir da administração e do catálogo; `GET /api/produtos/{id}` deve responder `404`; `GET /api/produtos/{id}/auditoria` deve continuar mostrando as ações anteriores e `EXCLUIR`.

T11 e T12 podem mudar os dados de exemplo durante as tentativas válidas. T19 remove definitivamente o produto usado; use apenas um registro descartável criado para esse teste. Antes de ensaiar, restaurar pela aplicação o preço de R$ 5,00, estoque 12, mínimo 3, máximo 20 e validade futura.

## Resultado da rodada

| Resultado | Preenchimento pela equipe |
| --- | --- |
| Casos aprovados | A preencher |
| Falhas e links das issues | A preencher |
| Casos pendentes e motivo | A preencher |
| Evidências: imagens ou registros de consulta | A preencher |
