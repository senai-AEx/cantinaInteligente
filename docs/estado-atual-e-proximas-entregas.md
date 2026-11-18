# Estado atual e próximas entregas — Cantina Inteligente

**Atualizado em 17/11/2026**  
**Equipe:** Grupo 4 · SENAI Fraiburgo  
**Board:** [Kanban da Cantina Inteligente](https://github.com/orgs/senai-AEx/projects/1/views/1)

## Onde estamos

A stack confirmada é **Python + Flask + MySQL**, com HTML/CSS/JavaScript no frontend. Um único servidor Flask entrega as telas e a API em `http://127.0.0.1:5000`.

**17/11/2026 (noite) — sistema completo implementado na develop.** Os 12 itens da demanda estão no código:

| Item da demanda | Situação |
| --- | --- |
| Cadastro de usuários; login por matrícula, e-mail ou CPF | Feito (issue #11) |
| Cadastro de produtos; consulta de preços | Feito (issue #10) |
| Créditos na carteira; consulta de saldo e extrato | Feito (issue #12) |
| Registro de compras com desconto do saldo e baixa do estoque | Feito (issue #13) |
| Histórico de compras | Feito (issue #14) |
| Troca e redefinição de senha | Feito (não estava na demanda; evita usuário preso sem acesso) |
| Painel administrativo: usuários, produtos e movimentações | Feito (issues #11 e #14) |
| Relatórios de vendas, saldos, estoque, depósitos declarados e compras por usuário | Feito (issue #14) |
| QR Code para facilitar o registro | Feito: QR da cantina e de cada produto, gerados no painel |

Como foi verificado em 17/11: 120 testes automatizados passando; 131 conferências da API contra o MySQL real (incluindo dois usuários disputando o último item e clique duplo simultâneo); e os fluxos do cliente e do administrador percorridos no navegador, em 1280 px e em 360 px.

**O que ainda falta para a AV05 (21/11):**

- Liberar o acesso ao repositório para a professora.
- Passar o [Documento do Sistema](documento-do-sistema.md) para o template, resolver os itens `[CONFIRMAR]`, exportar os diagramas de [diagramas/](diagramas/README.md) e gerar o PDF.
- Executar o [roteiro de testes manuais](testes-manuais.md) e registrar o resultado.
- Gravar o vídeo conforme o [roteiro](roteiro-video-demonstracao.md).
- Aplicar o checklist da ABNT NBR 17225 e registrar em `docs/checklist-acessibilidade-nbr17225.md` (10% da banca). As cores e o foco já foram ajustados para contraste mínimo de 4,5:1, mas o checklist completo não foi percorrido.
- Commits próprios de todos os integrantes (hoje falta a Ana Cecília).

**17/11/2026 — devolutiva do produto aplicada na develop** (issue #10): código automático, preço de compra e de venda, só quantidade em estoque, sem validade, sem caixas de zero lactose (selos automáticos para frutas), gravação apenas pelo botão Salvar e exclusão lógica (sem exclusão definitiva). O backend do Luan (controller/service/repository) foi unificado com o da AV04, eliminando o conflito entre `src/app.py` e `src/backend/app.py`. Banco atualizado pela migração `005`. Testes automatizados (17) passando e fluxo testado na tela com MySQL. Falta preencher o [checklist manual](testes-manuais.md) com evidências.

A **AV04 foi apresentada em 15/10/2026 e recebeu 85/100**. Isso registra o resultado da apresentação, mas não significa que todos os testes integrados ou o sistema completo estejam concluídos.

- [Issue #1 — base e banco](https://github.com/senai-AEx/cantinaInteligente/issues/1): concluída.
- [Issues #2 e #4 — API de inclusão/consulta e telas](https://github.com/orgs/senai-AEx/projects/1/views/1): em revisão; implementação publicada, critérios ainda sem evidência completa.
- [Issue #3 — edição, inativação e auditoria](https://github.com/senai-AEx/cantinaInteligente/issues/3): exclusão física removida em 17/11; pronta para revisão.
- [Issue #5 — teste integrado e roteiro](https://github.com/senai-AEx/cantinaInteligente/issues/5): em “A fazer”. Cinco testes automatizados locais passaram (upload de imagem e exclusão/auditoria), mas ainda não há rodada ponta a ponta do CRUD com MySQL nem checklist manual preenchido.

O board deve refletir código integrado, teste e revisão. Não marcar como concluído só porque existe documentação ou tela.

## Devolutivas da professora a incorporar

- Refazer partes interessadas conforme o template.
- Incluir crédito do estudante e débito do saldo após compra; a entidade/atributo também precisa constar no MER.
- Unificar RF06/RF12, retirar RF04/RF10 fora do escopo e remover validade do RF03.
- Reorganizar RNF e regras de negócio conforme o template.
- ✅ No produto: ID automático, sem código manual; remover validade e estoque mínimo/máximo; incluir preço de compra e de venda; manter somente quantidade em estoque.
- ✅ Para fruta, aplicar automaticamente os selos zero lactose e zero açúcar (implementado para a categoria *Frutas*; confirmar com a cantina se há outras).
- ✅ Preservar produto e histórico por inativação; exclusão física removida da API e da tela.
- ✅ Gravar somente ao clicar em Salvar (Enter não envia o formulário).
- ⏳ **"Equipe deverá implementar o projeto na íntegra"** (feedback da AV04 no AVA): entregar todas as funcionalidades da demanda — usuários, login, créditos, compras, histórico, painel e relatórios —, não só o CRUD de produto. Ver o [plano de execução](plano-de-execucao.md).

A [issue #8](https://github.com/senai-AEx/cantinaInteligente/issues/8) concentra requisitos/MER. A [issue #10](https://github.com/senai-AEx/cantinaInteligente/issues/10) acompanha o novo cadastro e catálogo, incluindo mudanças coordenadas em banco, API, telas e testes. Os documentos da AV04 foram movidos para `docs/historico/av04/` e descrevem o modelo antigo.

## Próxima entrega — AV05

**Prazo no AVA: 21/11/2026, 23:59** (conferido em 17/11). Avaliação: integração ao banco (40%), validação/máscaras (20%), interface (10%) e versão final do Documento do Sistema com a seção de solução tecnológica (30%). Pré-requisitos: README com a execução, repositório com acesso liberado e vídeo de demonstração. O Plano de Trabalho Discente foi enviado em 11/11/2026.

**O passo a passo até a banca está no [plano de execução](plano-de-execucao.md).**

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

**Banca em 24/11/2026 (terça), entre 18:30 e 21:30; confirmar o horário do Grupo 4.** Critérios: demonstração 50%, checklist ABNT NBR 17225 10%, qualidade da apresentação 20%, detalhamento da solução 20%, clareza e tempo 10%. As issues [#16–#18](https://github.com/orgs/senai-AEx/projects/1/views/1) cobrem confirmação do checklist/pesos, congelamento e demonstração ponta a ponta, slides e defesa. O roteiro de estudos pede slides, diagramas, decisões técnicas, gravação silenciosa de 10–15 minutos e ensaio.

Os pesos descritos para a AV06 parecem somar 110%; confirmar o total com a professora.

## Referências

- [README e execução local](../README.md)
- [Decisões de stack e produto](decisoes.md)
- [Modelo de produto](modelo-produto.md)
- [Arquitetura e pastas](arquitetura.md)
- [API de produtos](contrato-api-produtos.md)
- [Checklist manual AV05](testes-manuais.md)
- [Registros da AV04](historico/av04/)
- [Issues e milestones](https://github.com/senai-AEx/cantinaInteligente/issues)
