# Estado atual e próximas entregas — Cantina Inteligente

**Atualizado em 16/10/2026**  
**Equipe:** Grupo 4 · SENAI Fraiburgo  
**Board:** [Kanban da Cantina Inteligente](https://github.com/orgs/senai-AEx/projects/1/views/1)

## Onde estamos

A stack confirmada é **Python + Flask + MySQL**, com HTML/CSS/JavaScript no frontend. A branch develop contém aplicação, migrações, API de produtos, telas cliente/admin, busca e filtros, validações e auditoria.

A **AV04 foi apresentada em 15/10/2026 e recebeu 85/100**. Isso registra o resultado da apresentação, mas não significa que todos os testes integrados ou o sistema completo estejam concluídos.

- [Issue #1 — base e banco](https://github.com/senai-AEx/cantinaInteligente/issues/1): concluída.
- [Issues #2 e #4 — API de inclusão/consulta e telas](https://github.com/orgs/senai-AEx/projects/1/views/1): em revisão; implementação publicada, critérios ainda sem evidência completa.
- [Issue #3 — edição, inativação e auditoria](https://github.com/senai-AEx/cantinaInteligente/issues/3): em “A fazer” porque o código ainda expõe exclusão física, contrária à orientação de preservar o produto por inativação.
- [Issue #5 — teste integrado e roteiro](https://github.com/senai-AEx/cantinaInteligente/issues/5): em “A fazer”. Cinco testes automatizados locais passaram (upload de imagem e exclusão/auditoria), mas ainda não há rodada ponta a ponta do CRUD com MySQL nem checklist manual preenchido.

O board deve refletir código integrado, teste e revisão. Não marcar como concluído só porque existe documentação ou tela.

## Devolutivas da professora a incorporar

- Refazer partes interessadas conforme o template.
- Incluir crédito do estudante e débito do saldo após compra; a entidade/atributo também precisa constar no MER.
- Unificar RF06/RF12, retirar RF04/RF10 fora do escopo e remover validade do RF03.
- Reorganizar RNF e regras de negócio conforme o template.
- No produto: ID automático, sem código manual; remover validade e estoque mínimo/máximo; incluir preço de compra e de venda; manter somente quantidade em estoque.
- Para fruta, aplicar automaticamente os selos zero lactose e zero açúcar; confirmar com a cantina quais categorias acionam a regra.
- Preservar produto e histórico por inativação; retirar exclusão física do fluxo administrativo comum.

A [issue #8](https://github.com/senai-AEx/cantinaInteligente/issues/8) concentra requisitos/MER. A [issue #10](https://github.com/senai-AEx/cantinaInteligente/issues/10) acompanha o novo cadastro e catálogo, incluindo mudanças coordenadas em banco, API, telas e testes. Parte dos documentos AV04 e do esquema atual ainda descreve o modelo antigo; use-os como registro da implementação existente, não como escopo futuro.

## Próxima entrega — AV05

**Prazo Moodle: 19/11/2026.** Avaliação: integração ao banco (40%), validação/máscaras (20%), interface (10%) e Documento do Sistema com tecnologia (30%). O Plano de Trabalho Discente vence em **06/11/2026**.

Ordem sugerida no board:

1. [#8 — requisitos e MER](https://github.com/senai-AEx/cantinaInteligente/issues/8), em paralelo com [#9 — Plano de Trabalho Discente](https://github.com/senai-AEx/cantinaInteligente/issues/9).
2. [#10 — adequar cadastro e catálogo de produto](https://github.com/senai-AEx/cantinaInteligente/issues/10).
3. [#11 — usuários e perfis](https://github.com/senai-AEx/cantinaInteligente/issues/11).
4. [#12 — carteira/créditos e lançamentos](https://github.com/senai-AEx/cantinaInteligente/issues/12), incluindo a decisão de como registrar depósitos em dinheiro na caixa.
5. [#13 — compra com débito de saldo e atualização do estoque](https://github.com/senai-AEx/cantinaInteligente/issues/13).
6. [#14 — histórico e relatórios](https://github.com/senai-AEx/cantinaInteligente/issues/14).
7. [#15 — integração, testes, documentação e entrega](https://github.com/senai-AEx/cantinaInteligente/issues/15).

## Confirmações pendentes com a cantina

- Não usar Pix/cartão ou contas financeiras ligadas a CPF/CNPJ. O crédito vem de depósito físico na caixa. Confirmar quem registra/valida cada depósito e como impedir crédito sem conferência.
- Confirmar quais categorias de fruta recebem os dois selos.
- Manter simplicidade, baixo custo e o conceito da Cantina da Honestidade.

## Preparação da AV06

**Prazo Moodle: 28/11/2026; apresentações previstas entre 23 e 25/11.** As issues [#16–#18](https://github.com/orgs/senai-AEx/projects/1/views/1) cobrem confirmação do checklist/pesos, congelamento e demonstração ponta a ponta, slides e defesa. O roteiro de estudos pede slides, diagramas, decisões técnicas, gravação silenciosa de 10–15 minutos e ensaio.

Os pesos descritos para a AV06 parecem somar 110%; confirmar o total com a professora.

## Referências

- [README e execução local](../README.md)
- [Decisões de stack e produto](decisoes.md)
- [Modelo de produto](modelo-produto.md)
- [Contrato da API AV04](contrato-crud.md)
- [Checklist manual AV04](testes-manuais-av04.md)
- [Issues e milestones](https://github.com/senai-AEx/cantinaInteligente/issues)
