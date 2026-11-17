# Apresentação para a banca (AV06)

Esqueleto dos slides e da fala. A banca é em **24/11/2026**, com **10 a 15 minutos** de apresentação, **todos os cinco integrantes falando** e a demonstração feita com o **vídeo sem áudio, narrado ao vivo**. Os slides devem ser montados no modelo "Template P.I UniSENAI" do AVA.

Critérios da AV06, conforme o AVA: demonstração da aplicação (50%), checklist da ABNT NBR 17225:2025 (10%), qualidade da apresentação (20%), detalhamento da solução (20%) e clareza e tempo (10%).

## Distribuição do tempo

| Bloco | Slides | Tempo | Quem fala |
| --- | --- | --- | --- |
| Abertura, problema e demanda | 1 a 3 | 1 min 30 s | Integrante 1 |
| Solução, atores e requisitos | 4 a 6 | 1 min 45 s | Integrante 2 |
| Dados, arquitetura e consistência | 7 a 9 | 2 min 15 s | Integrante 3 |
| Demonstração — parte do cliente | 10 (vídeo, cenas 1 a 10) | 4 min 10 s | Integrante 4 |
| Demonstração — parte do administrador | 10 (vídeo, cenas 11 a 16) | 2 min 30 s | Integrante 5 |
| Acessibilidade | 11 | 45 s | Integrante 5 |
| Resultados, próximos passos e encerramento | 12 e 13 | 1 min | Integrante 1 |
| **Total** | | **13 min 55 s** | |

O vídeo completo tem cerca de 7 min 45 s. Os tempos acima consideram a versão encurtada, de cerca de 6 min 40 s, com os cortes indicados no [roteiro do vídeo](roteiro-video-demonstracao.md). Com o vídeo completo, a apresentação chega a 15 minutos, sem folga. Meta de ensaio: **terminar em 14 minutos**, com 1 minuto de folga.

**[CONFIRMAR: trocar "Integrante 1 a 5" pelos nomes, conforme o grupo combinar. Sugestão: cada um apresenta a parte em que mais trabalhou.]**

## Slides

### Slide 1 — Capa (Integrante 1)

- Cantina Inteligente — Projeto Aplicado II
- Centro Universitário SENAI Santa Catarina — Análise e Desenvolvimento de Sistemas
- Equipe 4: os cinco nomes
- Professora: Janice Deters
- Diagrama: nenhum (logotipo do template)

### Slide 2 — O problema (Integrante 1)

- Cantina da Honestidade do SENAI Fraiburgo: sem atendente, pagamento em uma caixa
- Produtos retirados sem pagamento
- Sem controle de quem comprou, o quê e por quanto
- Sem troco para quem paga
- Diagrama: nenhum (uma foto ou ilustração da cantina, se houver) **[CONFIRMAR: há foto autorizada da cantina?]**

### Slide 3 — A demanda e as restrições (Integrante 1)

- O que a demanda pede: cadastro e login, produtos e preços, créditos e saldo, compras com desconto automático, histórico, painel administrativo e relatórios
- Restrições: manter o conceito de honestidade; impedir acesso não autorizado; não gerar inconsistência entre compras e saldos; baixo custo; permitir expansão
- Fala: "Cada decisão que vamos mostrar responde a uma dessas restrições."
- Diagrama: nenhum

### Slide 4 — A solução (Integrante 2)

- Aplicação web, usada no navegador do celular, sem instalar nada
- Fluxo em três passos: **depositar e declarar o crédito → comprar pelo sistema → saldo descontado automaticamente**
- Continua self-service: ninguém libera produto
- O administrador confere a caixa pelos depósitos declarados e emite relatórios
- Diagrama: **atividades — fluxo da compra** (`atividades-compra.mmd`), reduzido, ou um desenho simples dos três passos

### Slide 5 — Quem usa o sistema (Integrante 2)

- Dois atores: Cliente e Administrador
- Cliente: conta, crédito, compra, histórico
- Administrador: produtos, usuários, movimentações, relatórios
- Repositor e Pix: evolução futura
- Diagrama: **casos de uso** (`casos-de-uso.mmd`)

### Slide 6 — Requisitos e regras de negócio (Integrante 2)

- 13 requisitos funcionais, ligados aos itens da demanda
- Correções da professora aplicadas: requisito de crédito incluído; RF06 e RF12 unificados; fornecedores e causa social retirados; validade retirada
- Regras de negócio em seção própria: saldo nunca negativo; compra não duplica; nada é apagado, só inativado; preço de venda não menor que o de compra
- Diagrama: nenhum (tabela resumida dos RFs)

### Slide 7 — Modelo de dados (Integrante 3)

- 8 tabelas no MySQL
- O crédito: `saldo` na CARTEIRA e cada lançamento na MOVIMENTAÇÃO, com tipo CRÉDITO, DÉBITO ou AJUSTE
- A compra guarda o preço do momento em cada item
- Produto: código automático, preço de compra e de venda, só quantidade em estoque
- Diagrama: **MER** (`mer.mmd`), com CARTEIRA e MOVIMENTAÇÃO destacadas

### Slide 8 — Arquitetura e tecnologias (Integrante 3)

- Python + Flask no servidor; MySQL no banco; HTML, CSS e JavaScript nas telas
- Tudo gratuito: atende ao baixo custo
- Um servidor entrega as telas e a API na mesma porta
- Camadas: rotas → controle → serviço → repositório, um módulo por assunto: atende à expansão futura
- Git e GitHub para o trabalho em equipe; Docker para o banco igual em todos os computadores
- Diagrama: **componentes** (`componentes.mmd`) ou **topologia** (`topologia.mmd`)

### Slide 9 — Consistência e segurança (Integrante 3)

- Compra em uma única transação: registra, baixa o estoque e debita o saldo, ou não grava nada
- Carteira e produtos bloqueados durante a operação
- Chave única por operação: duplo clique não gera compra nem crédito repetido
- Senha guardada como hash; sessão por cookie que o JavaScript não lê; permissão conferida no servidor
- Diagrama: **sequência — finalizar compra** (`sequencia-compra.mmd`), reduzido aos passos principais

### Slide 10 — Demonstração (Integrantes 4 e 5)

- Vídeo em tela cheia, sem áudio, narrado ao vivo
- Integrante 4 narra a parte do cliente: catálogo, cadastro com validações, login, crédito, compra, saldo insuficiente, histórico e bloqueio do painel
- Integrante 5 narra a parte do administrador: produtos, usuários e ajuste, movimentações, relatórios, banco de dados e tela de celular
- As frases de cada cena estão no [roteiro do vídeo](roteiro-video-demonstracao.md)
- Diagrama: nenhum (o vídeo)

### Slide 11 — Acessibilidade: ABNT NBR 17225:2025 (Integrante 5)

- Checklist da norma aplicado às telas
- O que foi atendido: navegação por teclado, link "Pular para o conteúdo", rótulos nos campos, erro junto ao campo, contraste de cores
- O que foi corrigido depois do checklist e o que ficou justificado
- Números: itens atendidos, não atendidos e não aplicáveis **[CONFIRMAR: preencher com o resultado do arquivo `docs/checklist-acessibilidade-nbr17225.md`]**
- Diagrama: nenhum (tabela-resumo do checklist ou um print da ferramenta)

### Slide 12 — Resultados e próximos passos (Integrante 1)

- Itens da demanda entregues: cadastro, login, produtos, preços, créditos, saldo, compras, desconto automático, histórico, painel e relatórios
- QR Code **[CONFIRMAR: entregue ou previsto]**
- Para o Projeto Aplicado III: publicação em servidor com HTTPS, crédito por Pix, perfil de repositor, exportação dos relatórios e backup automático **[CONFIRMAR com o grupo quais itens citar]**
- Diagrama: nenhum (tabela "demanda × entregue")

### Slide 13 — Encerramento (Integrante 1)

- Repositório: https://github.com/senai-AEx/cantinaInteligente
- Agradecimento e abertura para perguntas
- Diagrama: nenhum

## Diagramas usados

| Slide | Diagrama | Arquivo em `docs/diagramas/` |
| --- | --- | --- |
| 4 | Atividades — fluxo da compra | `atividades-compra.mmd` |
| 5 | Casos de uso | `casos-de-uso.mmd` |
| 7 | MER | `mer.mmd` |
| 8 | Componentes ou topologia | `componentes.mmd` / `topologia.mmd` |
| 9 | Sequência — finalizar compra | `sequencia-compra.mmd` |

Os diagramas de sequência e o MER têm muito texto. No slide, amplie a parte que será explicada ou use uma versão recortada; o diagrama completo fica no Documento do Sistema.

## Perguntas prováveis e respostas

**1. Por que o crédito é declarado pelo próprio usuário, e não lançado por um atendente?**
Porque a cantina é da honestidade e não tem atendente. Se alguém precisasse conferir cada depósito na hora, o conceito mudaria e a cantina passaria a depender de uma pessoa presente. O usuário continua depositando na caixa, como hoje, e declara o valor no sistema.

**2. E se alguém declarar um crédito que não depositou?**
Hoje a pessoa já pode levar o produto sem pagar, e ninguém fica sabendo. Com o sistema, cada declaração fica registrada com usuário, valor, data e hora. O administrador compara o total de depósitos declarados com o dinheiro da caixa e, se houver diferença, lança um ajuste com motivo ou inativa o cadastro. O sistema não elimina a confiança; ele dá rastreabilidade.

**3. Como o saldo nunca fica inconsistente com as compras?**
Por quatro proteções. A compra, os itens, a baixa do estoque e o débito são gravados em uma única transação: ou tudo, ou nada. A carteira e os produtos ficam bloqueados enquanto a operação acontece, então duas compras ao mesmo tempo não usam o mesmo saldo. O próprio banco recusa saldo ou estoque negativo. E cada lançamento guarda o saldo após a operação, então o extrato sempre explica o saldo.

**4. O que acontece se o usuário clicar duas vezes em "confirmar" ou a internet cair no meio?**
A tela gera uma chave única para cada operação. Se a mesma chave chegar de novo, o servidor devolve a compra que já foi registrada, sem cobrar outra vez. Se a conexão cair antes de gravar, a transação é desfeita e nada é cobrado.

**5. Por que não existe exclusão física de produtos e usuários?**
Porque as compras e as movimentações apontam para eles. Apagar um produto ou um usuário quebraria o histórico e os relatórios. Por isso "excluir" é inativar: o produto sai do catálogo, o usuário não consegue mais entrar e os registros continuam no banco. Foi também uma orientação da devolutiva da AV04.

**6. Como é a segurança do sistema?**
A senha tem regra mínima e é guardada apenas como hash; nem o administrador a vê. O login cria uma sessão em cookie que o JavaScript da página não consegue ler. Cada rota restrita confere no servidor se há login e qual é o perfil: sem login responde 401 e sem permissão responde 403. Esconder o botão na tela não é a proteção; a proteção está no servidor. O CPF aparece mascarado.

**7. Por que Python, Flask e MySQL?**
São gratuitos, o que atende ao baixo custo, e a equipe já conhecia. O Flask é simples e permite separar o sistema em módulos. O MySQL é relacional e tem transações e restrições, que são necessárias para lidar com saldo e estoque.

**8. Por que os valores são guardados em centavos?**
Porque números com casas decimais podem gerar erro de arredondamento. Guardando R$ 4,50 como 450, todas as contas são feitas com inteiros e fecham exatamente.

**9. O que mudou no documento depois das devolutivas?**
As partes interessadas voltaram ao formato do template. Entrou o requisito de crédito. Os antigos RF06 e RF12 viraram um só. Fornecedores e causa social saíram. A validade saiu. Idempotência e auditoria deixaram de ser requisitos não funcionais e viraram regras de negócio. O MER passou a mostrar o crédito na carteira e nas movimentações. E os diagramas UML e a solução tecnológica foram preenchidos.

**10. Por que não tem Pix, fornecedores, validade e repositor?**
Fornecedores, causa social e validade foram retirados por orientação da professora. Pix e repositor não constam nos itens obrigatórios da demanda e aumentariam o custo e a complexidade; ficaram registrados como evolução futura.

**11. O que fica para o Projeto Aplicado III?**
Publicar o sistema em um servidor com HTTPS para uso real na unidade; crédito automático por Pix; perfil de repositor para a entrada de mercadorias; exportação dos relatórios; e backup automático do banco. Como a API já devolve JSON, ela pode ser reaproveitada por um aplicativo mobile no Projeto Aplicado IV. **[CONFIRMAR com o grupo.]**

**12. Como o sistema seria instalado na unidade?**
Em um computador ligado à rede da unidade, rodando o Flask e o MySQL. Os usuários acessam pelo navegador do celular. Antes disso, é preciso trocar as senhas de demonstração e usar HTTPS.

**13. Como vocês testaram?**
Com testes automatizados do servidor, executados com `make test`, e com um roteiro de testes manuais que cobre cadastro, login, crédito, compra, relatórios, segurança e layout em 360 × 800 px. **[CONFIRMAR: informar quantos testes automatizados existem e se o roteiro manual foi executado por completo.]**

**14. Como atenderam à norma de acessibilidade?**
Aplicamos o checklist da ABNT NBR 17225:2025 nas telas e registramos o resultado. Os pontos principais são a navegação por teclado, os rótulos dos campos, as mensagens de erro em texto junto ao campo e o contraste das cores. **[CONFIRMAR com o resultado do checklist.]**

**15. Como cada integrante contribuiu?**
Cada um fala da sua parte e mostra os commits no GitHub. **[CONFIRMAR: preparar um slide de apoio ou abrir a página de contribuições do repositório, se a banca pedir.]**

**16. E o QR Code da demanda?**
A demanda trata o QR Code como uma possibilidade para facilitar o registro. **[CONFIRMAR: se foi implementado, mostrar no vídeo; se não, responder que está previsto como RF13 e que o registro pelo catálogo no celular já cumpre o objetivo de facilitar a compra.]**

## Antes da banca

- [ ] Confirmar o horário do Grupo 4 com a professora.
- [ ] Slides no "Template P.I UniSENAI", com os diagramas exportados em PNG.
- [ ] Vídeo salvo no computador (não depender da internet) e também publicado.
- [ ] Sistema rodando no computador como plano B, caso a banca peça para ver algo ao vivo.
- [ ] Ensaio cronometrado com os cinco integrantes, pelo menos duas vezes.
- [ ] Cada integrante sabe responder às perguntas 1, 3, 5 e 6.
- [ ] Checklist da NBR 17225 preenchido e disponível para mostrar.

## Itens a confirmar

- **[CONFIRMAR]** nomes dos integrantes em cada bloco.
- **[CONFIRMAR]** conteúdo exigido pelo "Template P.I UniSENAI" (o arquivo do AVA não foi consultado para escrever este esqueleto).
- **[CONFIRMAR]** os pesos da AV06 citados no AVA somam 110%; conferir com a professora.
- **[CONFIRMAR]** resultado do checklist da NBR 17225 para o slide 11.
- **[CONFIRMAR]** situação do QR Code e lista de itens para o Projeto Aplicado III.
