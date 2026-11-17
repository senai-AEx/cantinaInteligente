# Roteiro do vídeo de demonstração

Vídeo **sem áudio**, de **6 a 8 minutos**, gravado da tela. Ele é enviado na AV05 e narrado **ao vivo** na banca (AV06). Por isso, cada cena tem uma frase curta para quem estiver narrando.

Ordem do vídeo: cadastro → login → crédito → compra → saldo insuficiente → histórico → segurança → painel administrativo → relatórios → banco de dados → celular.

## Critérios que o vídeo precisa mostrar

| Sigla | Critério | Onde vale |
| --- | --- | --- |
| **BD** | Integração com o banco de dados | AV05 — 40% |
| **VAL** | Validação de campos e máscaras | AV05 — 20% |
| **INT** | Interface | AV05 — 10% |
| **DEMO** | Demonstração da aplicação | AV06 — 50% |
| **ACESS** | Acessibilidade (checklist ABNT NBR 17225:2025) | AV06 — 10% |

O Documento do Sistema (30% da AV05) não aparece no vídeo; ele é enviado em PDF.

## Antes de gravar

- [ ] Banco limpo, só com os produtos de exemplo: `make up`, `make seed` e `make admin`. Sem compras, créditos ou clientes antigos, para os valores do roteiro baterem.
- [ ] Ter rodado o [roteiro de testes manuais](testes-manuais.md) sem falhas que apareçam no vídeo.
- [ ] Duas janelas do navegador: uma normal para o **cliente** e uma anônima para o **administrador**. Assim não é preciso sair e entrar a cada troca.
- [ ] Janela do navegador em 1280 × 720, zoom 100% (ou 110% se o texto ficar pequeno), sem barra de favoritos e sem outras abas.
- [ ] Uma consulta pronta no MySQL Workbench (cena 13), com a tela já conectada.
- [ ] Senhas: a do administrador está no `.env` (`ADMIN_SENHA`); a da cliente é escolhida por quem grava. O campo de senha fica oculto; **não marque "Mostrar senha" durante a gravação**.
- [ ] Notificações do computador desligadas. Gravar com o OBS Studio ou outro gravador de tela, **sem microfone**.
- [ ] Movimentos lentos do mouse e uma pausa de 1 a 2 segundos em cada resultado importante, para dar tempo de narrar.

Dados usados na gravação (fictícios):

| Dado | Valor |
| --- | --- |
| Cliente | Maria Souza · matrícula `202612345` · CPF `111.444.777-35` · `maria@exemplo.com` |
| Crédito declarado | R$ 20,00 |
| Compra 1 | 1 Suco de Laranja (R$ 7,50) + 1 Maçã (R$ 3,00) = **R$ 10,50** → saldo **R$ 9,50** |
| Compra bloqueada | 1 Sanduíche Natural (R$ 12,00) com saldo de R$ 9,50 |
| Produto novo | Água Mineral 500 ml · Bebidas · compra R$ 1,50 · venda R$ 3,00 · estoque 10 |
| Ajuste do administrador | + R$ 5,00 · motivo "Depósito conferido na caixa" → saldo **R$ 14,50** |

## Cenas

| # | Tempo | O que mostrar na tela | O que digitar ou clicar | Fala do narrador (uma frase) | Critério |
| --- | --- | --- | --- | --- | --- |
| 1 | 0:00–0:20 | Tela inicial em `http://127.0.0.1:5000/` e, em seguida, o catálogo com os produtos e os preços. | Clicar em **Explorar produtos**; rolar a lista devagar. | "Esta é a Cantina Inteligente: o catálogo com os preços pode ser consultado por qualquer pessoa, sem login." | INT, DEMO |
| 2 | 0:20–0:50 | Tela **Criar conta** com as validações. | Clicar em **Criar conta** com tudo vazio. Depois digitar o CPF `123.456.789-00` e uma senha curta, e clicar de novo. | "O cadastro valida os campos obrigatórios, o dígito verificador do CPF e a força da senha, com a mensagem junto de cada campo." | VAL |
| 3 | 0:50–1:20 | O mesmo formulário preenchido corretamente; a máscara do CPF se formando; a lista de regras da senha ficando marcada. | Nome `Maria Souza`; matrícula `202612345`; CPF `11144477735` (a máscara formata); e-mail `maria@exemplo.com`; senha e confirmação. Clicar em **Criar conta**. | "Com os dados corretos, a conta é criada no banco, já com uma carteira de saldo zero, e a Maria entra no sistema." | VAL, BD |
| 4 | 1:20–1:50 | Cabeçalho com "Olá, Maria" e saldo R$ 0,00. Depois, a tela **Entrar**. | Clicar em **Sair**. Entrar com o **e-mail** e a senha; **Sair**; entrar com o **CPF** e a senha. | "O login aceita matrícula, e-mail ou CPF no mesmo campo, como a demanda pede." | DEMO, BD |
| 5 | 1:50–2:30 | **Minha conta**: saldo R$ 0,00, formulário de crédito, extrato vazio. | Em **Adicionar crédito**, digitar `2000` no campo **Valor depositado** (a máscara mostra `20,00`), marcar **Declaro que depositei este valor na caixa da cantina** e clicar em **Adicionar crédito**. Mostrar o saldo R$ 20,00 e a linha no extrato. | "A Maria colocou vinte reais na caixa da cantina e declarou esse valor: ele vira crédito na carteira e aparece no extrato." | BD, VAL |
| 6 | 2:30–2:45 | O mesmo formulário recusando um valor inválido. | Digitar `50` (R$ 0,50), marcar a declaração e clicar em **Adicionar crédito**. Mostrar a mensagem de erro junto ao campo. | "Valores fora do limite são recusados, na tela e também no servidor." | VAL |
| 7 | 2:45–3:35 | Catálogo, sacola e resumo da compra. | Adicionar 1 **Suco de Laranja** e 1 **Maçã**. Mostrar a sacola (total R$ 10,50). Clicar em **Finalizar compra**: mostrar **Total da compra**, **Saldo disponível** e **Saldo após a compra**. Clicar em **Confirmar compra**. Mostrar "Compra registrada!", o agradecimento e o saldo R$ 9,50 no cabeçalho. | "Na compra, o sistema confere estoque e saldo, registra a compra, baixa o estoque e desconta o total do saldo, tudo em uma única operação." | BD, DEMO |
| 8 | 3:35–4:00 | Catálogo com o estoque do Suco em 19. Depois, a compra bloqueada. | Adicionar 1 **Sanduíche Natural** (R$ 12,00) e clicar em **Finalizar compra**. Mostrar o aviso "Saldo insuficiente" (faltam R$ 2,50), o botão **Confirmar compra** desabilitado e o link **Adicionar crédito**. Fechar e limpar a sacola. | "Com saldo menor que o total, a compra é bloqueada e nada é gravado: o saldo nunca fica negativo." | BD, DEMO |
| 9 | 4:00–4:25 | **Minha conta**: quadro **Minhas compras** com a compra e os itens; quadro **Extrato** com o crédito e o débito. | Mostrar os itens da compra. Mostrar no extrato: + R$ 20,00, − R$ 10,50, saldo após R$ 9,50. | "O histórico mostra o que foi comprado e o extrato explica o saldo, lançamento por lançamento." | BD, DEMO |
| 10 | 4:25–4:40 | Tentativa de abrir o painel como cliente. | Na barra de endereço, digitar `/html/catalogo_produtos_adm.html`. Mostrar o retorno ao catálogo com o aviso de permissão. | "Um cliente não entra na área administrativa: o servidor confere o perfil em cada acesso." | DEMO |
| 11 | 4:40–5:30 | Janela do **administrador**: login e painel de produtos. | Entrar com a matrícula do administrador. Clicar em **Cadastrar produto**: `Água Mineral 500 ml`, `Bebidas`, compra `150` (1,50), venda `100` (1,00) → mostrar o erro de venda menor que compra; corrigir a venda para `300` (3,00); estoque `10`; **Salvar produto**. Mostrar o card com o código gerado. Clicar em **Excluir** na Barra de Cereal, confirmar e mostrar como **Inativo**; clicar em **Reativar**. | "O administrador mantém os produtos com preço de compra, preço de venda e estoque; o código é automático e excluir apenas inativa." | VAL, BD, INT |
| 12 | 5:30–6:05 | Tela de **usuários** do painel. | No menu do painel, abrir **Usuários**. Buscar `Maria`. Mostrar o CPF mascarado. Abrir **Ajustar saldo**: tipo acrescentar, valor `500` (R$ 5,00), motivo `Depósito conferido na caixa`; mostrar o saldo após o ajuste e clicar em **Lançar ajuste**. Mostrar o saldo R$ 14,50. | "Na gestão de usuários, o administrador pode inativar um cadastro e lançar um ajuste de saldo, sempre com motivo." | BD, DEMO |
| 13 | 6:05–6:30 | Tela de **Movimentações** do painel. | No menu, abrir **Movimentações**. Filtrar por tipo **CRÉDITO** e clicar em **Aplicar filtros**. Mostrar o quadro **Totais do período** (créditos: R$ 20,00). Clicar em **Limpar filtros** e mostrar crédito, débito e ajuste na lista. | "Todas as movimentações ficam registradas, com usuário, tipo, valor, saldo e data." | BD, DEMO |
| 14 | 6:30–7:00 | Tela de **Relatórios**: abas Vendas, Saldos, Estoque e Depósitos declarados. | Período **Hoje**. Aba **Vendas**: 1 compra, 2 itens, total R$ 10,50, lucro R$ 4,20. Aba **Saldos**: Maria com R$ 14,50. Aba **Estoque**: Suco com 19 e Maçã com 24. Aba **Depósitos declarados**: total de R$ 20,00. | "Os relatórios batem com o que acabamos de fazer, e o total de depósitos declarados é o valor que o administrador confere com o dinheiro da caixa." | BD, DEMO |
| 15 | 7:00–7:20 | MySQL Workbench com os dados gravados. | Executar a consulta abaixo e mostrar as linhas de `usuarios` (com `senha_hash`), `compras` e `movimentacoes`. | "No banco, a senha está apenas como hash e cada compra tem o seu débito correspondente." | BD |
| 16 | 7:20–7:45 | O catálogo e a **Minha conta** em 360 × 800 px (F12, modo de dispositivo). Depois, a navegação por teclado. | Alternar para 360 × 800 e rolar. Voltar ao tamanho normal, pressionar Tab e mostrar "Pular para o conteúdo" e o foco visível. | "As telas funcionam no celular, sem rolagem horizontal, e podem ser usadas pelo teclado." | INT, ACESS |

Duração total prevista: **7 min 45 s**.

Consultas para a cena 15 (execute uma de cada vez, já deixadas prontas em abas do Workbench):

```sql
SELECT id_usuario, nome, matricula, senha_hash, status FROM usuarios;
```

```sql
SELECT c.id_compra, c.valor_total_centavos, m.tipo, m.valor_centavos, m.saldo_apos_centavos
FROM compras c JOIN movimentacoes m ON m.id_compra = c.id_compra;
```

## Se precisar encurtar (para ficar perto de 6 minutos)

Corte nesta ordem: cena 6 (valor inválido do crédito), o segundo login da cena 4, a inativação e a reativação do produto na cena 11 e a cena 15 (banco de dados). **Não corte:** cadastro com validação, crédito, compra com débito, saldo insuficiente, histórico, bloqueio do painel para o cliente e relatórios.

## Depois de gravar

- [ ] Assistir ao vídeo inteiro conferindo: nenhuma senha visível, nenhum dado pessoal real, nenhuma mensagem de erro inesperada.
- [ ] Conferir a duração (6 a 8 minutos) e a legibilidade do texto em tela cheia.
- [ ] Publicar o vídeo e colocar o link no envio da AV05. **[CONFIRMAR: onde o vídeo será publicado (YouTube não listado, Google Drive ou outro) e se a professora consegue abrir o link.]**
- [ ] Ensaiar a narração ao vivo com o vídeo rodando, usando as frases da tabela e a divisão de falas da [apresentação da banca](apresentacao-banca.md).

## Itens a confirmar neste roteiro

- **[CONFIRMAR: nomes dos botões e das abas]** Os textos em negrito foram conferidos com as telas em 17/11/2026, quando elas ainda estavam sendo finalizadas; reconferir antes de gravar.
- **[CONFIRMAR: cena 4]** se a tela de login deve mostrar os três identificadores no vídeo (matrícula já aparece na cena 11, com o administrador) ou só dois, para economizar tempo.
- **[CONFIRMAR: QR Code]** se o RF13 for implementado, acrescentar uma cena curta depois da cena 9: abrir o QR Code da cantina e o de um produto, mostrando o item entrando na sacola.
