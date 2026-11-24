# Roteiro de testes manuais — Cantina Inteligente

Roteiro para conferir o sistema completo com o MySQL ligado, antes da entrega da AV05 e da gravação do vídeo. Marque apenas o que foi realmente observado. Se um caso falhar, anote o que aconteceu e abra uma issue.

| Informação | Preenchimento |
| --- | --- |
| Data e responsável | |
| Commit testado | |
| Navegador e versão | |
| Tamanho de tela | |

## 1. Preparação

1. Confira se o MySQL está ligado (veja [como-rodar.md](como-rodar.md)). No terminal, dentro da pasta do repositório, rode `python instalar.py` (só na primeira vez) e depois `python iniciar.py`.
2. Em outro terminal, rode `python scripts/banco.py semear` (produtos de exemplo) e `python scripts/criar_admin.py` (administrador de demonstração).
3. Abra `http://127.0.0.1:5000/api/health/db`: deve responder `"banco": "conectado"`.
4. Abra `http://127.0.0.1:5000/`.

Para os testes de valores baterem com este roteiro, comece com o banco sem compras nem créditos. Os produtos do `python scripts/banco.py semear` são:

| Produto | Categoria | Preço de compra | Preço de venda | Estoque |
| --- | --- | --- | --- | --- |
| Suco de Laranja | Bebidas | R$ 4,80 | R$ 7,50 | 20 |
| Sanduíche Natural | Lanches | R$ 8,00 | R$ 12,00 | 15 |
| Barra de Cereal | Doces | R$ 2,50 | R$ 4,50 | 40 |
| Maçã | Frutas | R$ 1,50 | R$ 3,00 | 25 |

### Usuários de demonstração

| Usuário | Como é criado | Onde estão os dados de acesso |
| --- | --- | --- |
| Administrador | `python scripts/criar_admin.py` | No arquivo `.env` do seu computador: `ADMIN_MATRICULA`, `ADMIN_EMAIL`, `ADMIN_CPF` e `ADMIN_SENHA`. |
| Cliente de teste (Maria Souza) | No caso A01 deste roteiro | Matrícula `202612345`, e-mail `maria@exemplo.com`, CPF `111.444.777-35`. A senha é escolhida por quem testa. |
| Segundo cliente (João Lima) | No caso A09 | Matrícula `202654321`, e-mail `joao@exemplo.com`, CPF `390.533.447-05`. |

As senhas não são escritas neste roteiro. A do administrador fica só no `.env`, que não vai para o GitHub. Para os clientes de teste, use uma senha de teste com pelo menos 8 caracteres, letra e número, e nunca uma senha pessoal. Os dados acima são fictícios: os CPFs são números de exemplo que apenas passam na conferência dos dígitos.

### Como testar a API sem a tela

Alguns casos pedem uma chamada direta à API. Com o sistema aberto no navegador, pressione F12, abra a aba **Console** e cole o comando indicado. Exemplo, que mostra só o código de resposta:

```js
fetch("/api/carteira").then((resposta) => console.log(resposta.status));
```

Para enviar dados:

```js
fetch("/api/carteira/creditos", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ valor_centavos: 0, chave_idempotencia: crypto.randomUUID() }),
}).then(async (resposta) => console.log(resposta.status, await resposta.json()));
```

O navegador envia o cookie da sessão aberta naquela aba. Para testar "sem login", use uma janela anônima.

## 2. Cadastro e login (RF01, RF02)

Tela: `http://127.0.0.1:5000/html/cadastro.html` e `http://127.0.0.1:5000/html/login.html`.

- [ ] **A01 — Cadastro com sucesso.** Preencha nome `Maria Souza`, matrícula `202612345`, CPF `111.444.777-35`, e-mail `maria@exemplo.com`, senha e confirmação. Clique em **Criar conta**. *Esperado:* a conta é criada, o sistema já entra com a Maria e abre o catálogo com a mensagem de boas-vindas; o cabeçalho mostra "Olá, Maria", "Minha conta" com saldo R$ 0,00 e o botão **Sair**.
- [ ] **A02 — Cadastro gravado no banco.** Consulte `SELECT id_usuario, nome, matricula, cpf, email, senha_hash, id_tipo_usuario, status FROM usuarios;` e `SELECT * FROM carteiras;`. *Esperado:* a Maria aparece com perfil 2 (Cliente) e status `ATIVO`; `senha_hash` não é a senha digitada; existe uma carteira dela com `saldo_centavos = 0`.
- [ ] **A03 — Máscara do CPF.** No cadastro, digite `11144477735` no CPF. *Esperado:* o campo mostra `111.444.777-35`; letras são ignoradas e não entram mais de 11 dígitos.
- [ ] **A04 — Matrícula só com números.** Digite letras e símbolos na matrícula. *Esperado:* só os números ficam no campo.
- [ ] **A05 — Campos obrigatórios.** Clique em **Criar conta** com tudo vazio. *Esperado:* aparece uma mensagem junto a cada campo, o foco vai para o primeiro campo com erro e nada é gravado.
- [ ] **A06 — CPF inválido.** Tente `123.456.789-00` e depois `111.111.111-11`. *Esperado:* os dois são recusados com mensagem no campo CPF.
- [ ] **A07 — E-mail inválido.** Tente `maria@` e `maria.exemplo.com`. *Esperado:* recusado com mensagem no campo e-mail.
- [ ] **A08 — Regras da senha.** Tente uma senha com menos de 8 caracteres, uma só com letras e uma só com números; depois uma senha válida com a confirmação diferente. *Esperado:* a lista de regras abaixo do campo marca o que já foi cumprido; cada tentativa é recusada com mensagem no campo certo.
- [ ] **A09 — Duplicidade.** Saia e tente criar a conta do João Lima usando, uma de cada vez, a matrícula, o CPF e o e-mail da Maria. *Esperado:* cada tentativa é recusada com a mensagem no campo repetido (por exemplo, "Já existe um cadastro com esta matrícula."). Depois, cadastre o João com os dados dele.
- [ ] **A10 — Enter não grava o cadastro.** Preencha o cadastro de um terceiro usuário e pressione Enter em vários campos. *Esperado:* nada é enviado; só o clique em **Criar conta** grava.
- [ ] **A11 — Login por matrícula.** Na tela **Entrar**, informe `202612345` e a senha. *Esperado:* entra e mostra "Olá, Maria".
- [ ] **A12 — Login por e-mail.** Saia e entre com `maria@exemplo.com`; repita com `MARIA@EXEMPLO.COM`. *Esperado:* entra nas duas formas.
- [ ] **A13 — Login por CPF.** Saia e entre com `111.444.777-35`; repita com `11144477735`. *Esperado:* entra nas duas formas.
- [ ] **A14 — Login incorreto.** Tente a matrícula da Maria com senha errada e, depois, uma matrícula que não existe. *Esperado:* a mesma mensagem nas duas situações ("Matrícula, e-mail, CPF ou senha incorretos."), sem revelar qual dado está errado.
- [ ] **A15 — Login com campos vazios.** Clique em **Entrar** sem preencher. *Esperado:* mensagem junto a cada campo.
- [ ] **A16 — Sair.** Clique em **Sair**. *Esperado:* volta para o início; o cabeçalho mostra **Entrar** e **Criar conta**; "Minha conta" e o saldo somem.
- [ ] **A17 — Página protegida leva ao login e volta.** Sem login, abra `http://127.0.0.1:5000/html/minha_conta.html`. *Esperado:* vai para a tela de login com o aviso "Entre com a sua conta para continuar."; depois de entrar, volta para Minha conta.
- [ ] **A18 — Validação no servidor.** No Console, envie um cadastro inválido direto para a API:
  ```js
  fetch("/api/auth/cadastro", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome: "A", matricula: "abc", cpf: "123", email: "x", senha: "1", confirmar_senha: "2" }),
  }).then(async (resposta) => console.log(resposta.status, await resposta.json()));
  ```
  *Esperado:* status `422` e o objeto `campos` com uma mensagem para cada campo; nada é gravado.
- [ ] **A19 — Dados sensíveis não voltam.** No Console, logado: `fetch("/api/auth/eu").then((r) => r.json()).then(console.log)`. *Esperado:* o usuário vem com `cpf_mascarado` (`***.444.777-**`), sem senha e sem CPF completo.

## 3. Produtos (RF03, RF04)

Entre como **administrador**: o sistema abre o painel (**Início**). Clique em **Produtos** no menu lateral (ou abra `http://127.0.0.1:5000/html/catalogo_produtos_adm.html`).

### Devolutivas da AV04

- [ ] **D01 — Sem código manual:** o formulário não pede código. Após salvar, o card mostra "Código: N", gerado pelo banco.
- [ ] **D02 — Preço de compra e de venda:** o formulário tem os dois campos; o card mostra os dois valores.
- [ ] **D03 — Só quantidade em estoque:** não existem campos de estoque mínimo/máximo nem de validade.
- [ ] **D04 — Sem rótulos de zero lactose:** o formulário não tem as caixas de zero lactose/zero açúcar. Um produto da categoria *Frutas* aparece com os dois selos; um de *Bebidas*, sem selos.
- [ ] **D05 — Enter não grava:** preencha o cadastro e pressione Enter em vários campos. O modal continua aberto e nada é salvo (confira a lista e o banco).
- [ ] **D06 — Grava só no botão:** clique em **Salvar produto**. O produto aparece na lista e no banco.
- [ ] **D07 — Inativar não apaga:** clique em **Inativar** e confirme. O produto aparece como *Inativo*, some do catálogo do cliente e continua na tabela `produtos` com `status = 'INATIVO'`. Não existe opção de exclusão definitiva.
- [ ] **D08 — Reativar:** clique em **Reativar**; o produto volta aos ativos com o mesmo código.

### Validação e máscaras

- [ ] **V01 — Máscara de moeda:** digitar `450` no preço mostra `4,50`; letras são ignoradas.
- [ ] **V02 — Obrigatórios:** salvar com nome, categoria ou preços vazios mostra mensagem junto a cada campo.
- [ ] **V03 — Venda menor que compra:** compra 5,00 e venda 4,00 é recusado com mensagem no campo de venda.
- [ ] **V04 — Estoque:** quantidade negativa é recusada; zero é aceito e o card mostra "Sem estoque".
- [ ] **V05 — Foto:** JPG/PNG/WebP até 5 MB têm prévia; outros formatos ou arquivos maiores são recusados mantendo os demais dados digitados.
- [ ] **V06 — Validação no servidor:** pela API, logado como administrador, `POST /api/produtos` com `preco_venda_centavos` menor que o de compra, ou com `codigo_produto`, responde `422` e nada é gravado.

### Persistência e auditoria

- [ ] **P01 — Alterar:** mude o preço de venda e a quantidade; após recarregar a página os valores persistem.
- [ ] **P02 — Reiniciar:** pare e suba a aplicação de novo; os dados continuam.
- [ ] **P03 — Auditoria:** `GET /api/produtos/{id}/auditoria` lista `INCLUIR`, `ALTERAR`, `INATIVAR` e `REATIVAR` com antes/depois. O autor registrado é o administrador logado.
- [ ] **P04 — Layout:** listagem, formulário e confirmação funcionam em 360 × 800 px e no desktop sem rolagem horizontal.

### Catálogo do cliente

Abra `http://127.0.0.1:5000/html/catalogo_produtos.html`.

- [ ] **K01 — Catálogo sem login.** Em uma janela anônima, abra o catálogo. *Esperado:* os produtos ativos aparecem com nome, preço de venda, foto (quando houver) e disponibilidade, mesmo sem login.
- [ ] **K02 — Selos.** *Esperado:* a Maçã (Frutas) mostra zero lactose e zero açúcar; os demais não mostram selos.
- [ ] **K03 — Inativo não aparece.** Inative um produto no painel e recarregue o catálogo. *Esperado:* o produto some do catálogo. Reative ao final.
- [ ] **K04 — Produto esgotado.** Coloque o estoque de um produto em zero. *Esperado:* o card mostra "Esgotado" e o botão de adicionar fica desabilitado. Volte o estoque ao final.
- [ ] **K05 — Busca e categorias.** Busque "suco" e filtre por "Frutas". *Esperado:* a lista mostra só os produtos correspondentes.
- [ ] **K06 — Preço de compra não aparece para o cliente.** *Esperado:* o card do catálogo mostra apenas o preço de venda.

## 4. Carteira e créditos (RF06, RF07)

Entre como **Maria** e abra `http://127.0.0.1:5000/html/minha_conta.html`.

- [ ] **C01 — Saldo inicial.** *Esperado:* saldo R$ 0,00 na tela e no cabeçalho; extrato vazio.
- [ ] **C02 — Máscara de moeda.** No campo **Valor depositado**, digite `2000`. *Esperado:* o campo mostra `20,00`; letras são ignoradas. Os atalhos **R$ 5**, **R$ 10**, **R$ 20** e **R$ 50** preenchem o campo.
- [ ] **C03 — Adicionar crédito.** Informe R$ 20,00, marque **Declaro que depositei este valor na caixa da cantina** e clique em **Adicionar crédito**. *Esperado:* mensagem de sucesso; saldo R$ 20,00 na tela e no cabeçalho; o extrato mostra um CRÉDITO de + R$ 20,00, descrição "Depósito declarado na caixa" e saldo após de R$ 20,00.
- [ ] **C04 — Persistência.** Recarregue a página, saia e entre de novo. *Esperado:* o saldo continua R$ 20,00. No banco, `SELECT * FROM movimentacoes;` mostra a linha `CREDITO` com `valor_centavos = 2000` e `saldo_apos_centavos = 2000`.
- [ ] **C05 — Valor vazio, zero ou sem declaração.** Tente adicionar sem valor, com `0,00` e, depois, com R$ 10,00 sem marcar a declaração de depósito. *Esperado:* recusado nas três vezes, com a mensagem junto ao campo ou à declaração; o saldo não muda.
- [ ] **C06 — Limites.** Tente `0,99` e `500,01`. *Esperado:* recusados ("O valor deve ficar entre R$ 1,00 e R$ 500,00."). **Não** é preciso testar os valores aceitos nos limites, para não alterar o saldo do roteiro.
- [ ] **C07 — Duplo clique não duplica o crédito.** Em um usuário de teste à parte (por exemplo, o João), informe R$ 5,00, marque a declaração e dê dois cliques rápidos em **Adicionar crédito**. *Esperado:* o saldo sobe só R$ 5,00 e o extrato mostra um único lançamento.
- [ ] **C08 — Mesma chave pela API.** Logado como João, envie duas vezes o mesmo corpo, com a mesma chave:
  ```js
  const corpo = JSON.stringify({ valor_centavos: 300, chave_idempotencia: crypto.randomUUID() });
  const enviar = () => fetch("/api/carteira/creditos", { method: "POST", headers: { "Content-Type": "application/json" }, body: corpo })
    .then((resposta) => console.log(resposta.status));
  await enviar(); await enviar();
  ```
  *Esperado:* a primeira responde `201` e a segunda `200`; o saldo sobe só R$ 3,00.
- [ ] **C09 — Validação no servidor.** Pela API, envie `valor_centavos` igual a `0`, `-100`, `50001` e `"abc"`. *Esperado:* `422` em todos, com mensagem em `campos.valor_centavos`.
- [ ] **C10 — Extrato em ordem.** *Esperado:* os lançamentos mais recentes aparecem primeiro, com data e hora no horário local.

## 5. Compra (RF05, RF08, RF09)

Entre como **Maria** (saldo R$ 20,00) e abra o catálogo.

- [ ] **CP01 — Sacola.** Adicione 1 Suco de Laranja e 2 Maçãs; diminua a Maçã para 1; adicione e remova uma Barra de Cereal. *Esperado:* a sacola mostra 1 Suco e 1 Maçã, total R$ 10,50, e o contador da sacola acompanha.
- [ ] **CP02 — Limite pelo estoque.** Tente aumentar a quantidade de um item além do estoque. *Esperado:* o botão de aumentar desabilita no limite.
- [ ] **CP03 — Finalizar exige login.** Em uma janela anônima, monte uma sacola e clique em **Finalizar compra**. *Esperado:* a janela da compra avisa que é preciso entrar na conta e mostra o botão **Entrar para finalizar**; depois do login, o sistema volta ao catálogo com a sacola preservada e o aviso de que é só finalizar a compra.
- [ ] **CP04 — Resumo antes de confirmar.** Como Maria, clique em **Finalizar compra**. *Esperado:* a janela mostra os itens, o **Total da compra** (R$ 10,50), o **Saldo disponível** (R$ 20,00) e o **Saldo após a compra** (R$ 9,50).
- [ ] **CP05 — Compra com sucesso.** Clique em **Confirmar compra**. *Esperado:* aparece "Compra registrada!" com a mensagem de agradecimento e o número da compra; a sacola fica vazia; o cabeçalho mostra saldo R$ 9,50; no catálogo, o Suco passa de 20 para 19 unidades e a Maçã de 25 para 24.
- [ ] **CP06 — Compra no banco.** Consulte `compras`, `itens_compra`, `movimentacoes` e `produtos`. *Esperado:* uma compra de `1050` centavos; dois itens com `preco_unitario_centavos` 750 e 300 e `custo_unitario_centavos` 480 e 150; uma movimentação `DEBITO` de `-1050` com `saldo_apos_centavos = 950` e o `id_compra` preenchido; estoque atualizado.
- [ ] **CP07 — Saldo insuficiente na tela.** Com saldo R$ 9,50, coloque 1 Sanduíche Natural (R$ 12,00) na sacola e clique em **Finalizar compra**. *Esperado:* a janela mostra "Saldo insuficiente", informa que faltam R$ 2,50, deixa o botão **Confirmar compra** desabilitado e oferece o link **Adicionar crédito**. Nada muda: saldo R$ 9,50, estoque do Sanduíche em 15, nenhuma compra nova no histórico.
- [ ] **CP07b — Saldo insuficiente no servidor.** Ainda como Maria, envie a mesma compra direto pela API (troque o `id_produto` pelo código do Sanduíche Natural):
  ```js
  fetch("/api/compras", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ itens: [{ id_produto: 2, quantidade: 1 }], chave_idempotencia: crypto.randomUUID() }),
  }).then(async (resposta) => console.log(resposta.status, await resposta.json()));
  ```
  *Esperado:* status `409` com `codigo` igual a `SALDO_INSUFICIENTE`; saldo, estoque e histórico não mudam.
- [ ] **CP08 — Estoque insuficiente.** Deixe 2 Barras de Cereal na sacola da Maria. Em outra janela, como administrador, altere o estoque da Barra de Cereal para 1. Volte à janela da Maria, sem recarregar, e finalize. *Esperado:* a compra é bloqueada e a mensagem informa o produto, a quantidade disponível (1) e a pedida (2). Saldo, estoque e histórico não mudam. Volte o estoque para 40 ao final.
- [ ] **CP09 — Produto inativado durante a compra.** Deixe 1 Barra de Cereal na sacola da Maria; como administrador, inative a Barra de Cereal; volte à janela da Maria e finalize. *Esperado:* a compra é bloqueada com o aviso de que o produto não está mais à venda. Reative o produto ao final.
- [ ] **CP10 — Duplo clique não duplica a compra.** Com 1 Maçã na sacola (R$ 3,00), dê dois cliques rápidos em **Confirmar compra**. *Esperado:* uma única compra no histórico, um único débito no extrato e o saldo cai só R$ 3,00 (de R$ 9,50 para R$ 6,50).
- [ ] **CP11 — Preço do momento.** Como administrador, altere o preço de venda da Maçã para R$ 3,50. *Esperado:* no histórico da Maria, as compras antigas continuam mostrando a Maçã a R$ 3,00. Volte o preço para R$ 3,00 ao final.
- [ ] **CP12 — Validação no servidor.** Pela API, logado, envie `POST /api/compras` com: lista de itens vazia; quantidade `0`; quantidade `100`; o mesmo `id_produto` duas vezes. *Esperado:* `422` em todos, sem gravar nada.
- [ ] **CP13 — Preço não vem da tela.** Como João (para não alterar o saldo da Maria), envie pela API a compra de 1 Maçã com um campo extra de preço:
  ```js
  fetch("/api/compras", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ itens: [{ id_produto: 4, quantidade: 1, preco_unitario_centavos: 1 }], chave_idempotencia: crypto.randomUUID() }),
  }).then(async (resposta) => console.log(resposta.status, await resposta.json()));
  ```
  Troque o `id_produto` pelo código da Maçã no seu banco. *Esperado:* o campo extra é ignorado; a compra é registrada pelo preço de venda do banco (R$ 3,00), e não por R$ 0,01.

## 6. Histórico e extrato (RF07, RF10)

Como **Maria**, em Minha conta.

- [ ] **H01 — Minhas compras.** *Esperado:* cada compra aparece com data e hora, produtos, quantidades, preço unitário, subtotal e total; as mais recentes primeiro.
- [ ] **H02 — Extrato com os débitos.** *Esperado:* o extrato mostra o crédito de + R$ 20,00 e um DÉBITO para cada compra, com a descrição "Compra #N" e o saldo após cada lançamento.
- [ ] **H03 — Saldo confere com o extrato.** Some os créditos, os débitos e os ajustes do extrato. *Esperado:* o resultado é igual ao saldo mostrado, e o "saldo após" da linha mais recente também.
- [ ] **H04 — Compra de outro usuário.** Como João, no Console: `fetch("/api/compras/1").then((r) => console.log(r.status))`, usando o número de uma compra da Maria. *Esperado:* `404`.
- [ ] **H05 — Histórico vazio.** Entre com um usuário que nunca comprou. *Esperado:* a tela informa que ainda não há compras, sem erro.

## 7. Painel administrativo — usuários (RF11)

Entre como **administrador** e abra `http://127.0.0.1:5000/html/usuarios_adm.html`.

- [ ] **U01 — Lista e busca.** *Esperado:* a lista mostra os usuários por nome; a busca encontra por nome, matrícula e e-mail; os filtros de situação (ativos/inativos) e de perfil funcionam.
- [ ] **U02 — CPF mascarado.** *Esperado:* o CPF aparece como `***.444.777-**`; a senha não aparece em lugar nenhum.
- [ ] **U03 — Editar usuário.** Altere o nome e o e-mail do João. *Esperado:* os dados são salvos e continuam após recarregar. O CPF não pode ser editado.
- [ ] **U04 — Duplicidade na edição.** Tente colocar no João a matrícula ou o e-mail da Maria. *Esperado:* recusado com mensagem no campo.
- [ ] **U05 — Ajuste de saldo positivo.** Em **Ajustar saldo**, escolha acrescentar, informe R$ 5,00 e o motivo "Depósito conferido na caixa" e clique em **Lançar ajuste**. *Esperado:* a janela mostra o saldo após o ajuste antes de gravar; o saldo da Maria sobe R$ 5,00; no extrato dela aparece um AJUSTE com a descrição "Ajuste da administração: Depósito conferido na caixa".
- [ ] **U06 — Ajuste inválido.** Tente: valor zero; motivo com menos de 5 caracteres; valor acima de R$ 1.000,00; ajuste do tipo descontar maior que o saldo do usuário. *Esperado:* todos recusados com mensagem clara; o último informa saldo insuficiente. Nenhum saldo muda.
- [ ] **U07 — Mudar perfil.** Mude o perfil do João para Administrador. *Esperado:* ao entrar, o João vê o item **Administração** no cabeçalho. Volte o perfil para Cliente ao final.
- [ ] **U08 — Inativar usuário.** Com o João logado em outra janela, inative o João. *Esperado:* ele aparece como Inativo na lista e continua na tabela `usuarios`; na janela dele, a próxima ação pede login; ao tentar entrar, aparece o aviso de cadastro inativo.
- [ ] **U09 — Reativar usuário.** Reative o João. *Esperado:* ele volta a entrar, com o mesmo saldo e histórico.
- [ ] **U10 — Operação em si mesmo.** Tente inativar o próprio administrador logado e tirar o próprio perfil de administrador. *Esperado:* as duas operações são recusadas.
- [ ] **U11 — Sem exclusão de usuário.** *Esperado:* não existe botão de apagar usuário; a única opção é inativar.

## 8. Painel administrativo — movimentações (RF11)

Abra `http://127.0.0.1:5000/html/movimentacoes_adm.html`.

- [ ] **M01 — Lista geral.** *Esperado:* aparecem os créditos, os débitos e os ajustes de todos os usuários, com usuário, tipo, valor, saldo após, descrição e data e hora.
- [ ] **M02 — Filtro por tipo.** Filtre por CRÉDITO, depois por DÉBITO e por AJUSTE, clicando em **Aplicar filtros**. *Esperado:* a lista mostra só o tipo escolhido; **Limpar filtros** volta à lista completa.
- [ ] **M03 — Filtro por período.** Informe o dia de hoje como início e fim; depois um período anterior ao teste. *Esperado:* o primeiro mostra os lançamentos do teste; o segundo fica vazio, com os totais zerados.
- [ ] **M04 — Filtro por usuário.** Filtre pela Maria. *Esperado:* a lista é igual ao extrato dela.
- [ ] **M05 — Totais do período.** *Esperado:* no quadro **Totais do período**, o total de créditos, o de débitos e o de ajustes são iguais à soma das linhas de cada tipo.
- [ ] **M06 — Período inválido.** Informe a data inicial depois da final. *Esperado:* mensagem de erro, sem quebrar a tela.

## 9. Relatórios (RF12)

Abra `http://127.0.0.1:5000/html/relatorios_adm.html`. Antes, anote em um papel todas as compras, créditos e ajustes feitos neste roteiro.

- [ ] **R01 — Vendas no período.** Na aba **Vendas**, escolha o período **Hoje** e clique em **Atualizar relatório**. *Esperado:* a quantidade de compras, os itens vendidos e o total vendido são iguais ao que foi anotado.
- [ ] **R02 — Custo, lucro e ticket médio.** *Esperado:* lucro = total vendido − custo; ticket médio = total vendido ÷ quantidade de compras. Para a compra de 1 Suco + 1 Maçã: total R$ 10,50, custo R$ 6,30, lucro R$ 4,20.
- [ ] **R03 — Vendas por produto e por dia.** *Esperado:* a soma dos totais por produto e a soma dos totais por dia são iguais ao total vendido.
- [ ] **R04 — Saldos.** Abra a aba **Saldos**. *Esperado:* a lista mostra os clientes com o saldo de cada um, do maior para o menor; o total de saldos é a soma da lista; o saldo da Maria é igual ao que ela vê em Minha conta.
- [ ] **R05 — Estoque.** Abra a aba **Estoque**. *Esperado:* os produtos sem estoque aparecem primeiro; o valor em estoque de cada produto é quantidade × preço de compra; o total de itens e o valor total batem com a soma das linhas.
- [ ] **R06 — Depósitos declarados × caixa.** Abra a aba **Depósitos declarados** com o período **Hoje**. *Esperado:* a lista mostra cada depósito com usuário, valor e data e hora, e o total é igual à soma dos depósitos declarados no teste e ao total de créditos da tela de Movimentações. É esse valor que o administrador compara com o dinheiro da caixa.
- [ ] **R07 — Conta geral fecha.** Considerando só os clientes, em um banco que começou vazio: créditos − vendas + ajustes = total de saldos. *Esperado:* a conta fecha, centavo por centavo.
- [ ] **R08 — Período inválido.** Data inicial depois da final. *Esperado:* mensagem de erro.
- [ ] **R09 — Imprimir.** Clique em **Imprimir** em Relatórios e em Movimentações. *Esperado:* a prévia de impressão mostra o conteúdo legível, sem o menu.

## 10. Segurança (RNF07)

- [ ] **S01 — Cliente não abre o painel.** Como Maria, digite `http://127.0.0.1:5000/html/catalogo_produtos_adm.html` na barra de endereço. Repita com `usuarios_adm.html`, `movimentacoes_adm.html` e `relatorios_adm.html`. *Esperado:* ela é levada de volta ao catálogo com o aviso de que não tem permissão.
- [ ] **S02 — Sem login não abre o painel.** Em janela anônima, abra as mesmas páginas. *Esperado:* vai para a tela de login.
- [ ] **S03 — Menu conforme o perfil.** *Esperado:* o item **Administração** aparece só para o administrador; **Minha conta** e **Sair** só para quem está logado; **Entrar** e **Criar conta** só para quem não está.
- [ ] **S04 — API sem login responde 401.** Em janela anônima, no Console:
  ```js
  for (const rota of ["/api/carteira", "/api/compras", "/api/admin/usuarios", "/api/admin/relatorios/vendas"]) {
    fetch(rota).then((resposta) => console.log(rota, resposta.status));
  }
  ```
  *Esperado:* `401` em todas.
- [ ] **S05 — API como cliente responde 403.** Como Maria, no Console:
  ```js
  for (const rota of ["/api/admin/usuarios", "/api/admin/movimentacoes", "/api/admin/relatorios/vendas", "/api/admin/relatorios/saldos", "/api/admin/relatorios/estoque"]) {
    fetch(rota).then((resposta) => console.log(rota, resposta.status));
  }
  ```
  *Esperado:* `403` em todas.
- [ ] **S06 — Cliente não grava produto pela API.** Como Maria: `fetch("/api/produtos/1/inativar", { method: "PATCH" }).then((r) => console.log(r.status))`. *Esperado:* `403`, e o produto continua ativo.
- [ ] **S07 — Não existe exclusão física.** Como administrador: `fetch("/api/produtos/1", { method: "DELETE" }).then((r) => console.log(r.status))`. *Esperado:* `405`.
- [ ] **S08 — Cookie de sessão.** Com F12, aba **Application** (ou **Armazenamento**), em Cookies. *Esperado:* existe o cookie `cantina_sessao` com `HttpOnly` marcado e `SameSite` igual a `Lax`. No Console, `document.cookie` não mostra esse cookie.
- [ ] **S09 — Senha no banco.** `SELECT senha_hash FROM usuarios;` *Esperado:* só aparecem hashes; nenhuma senha legível.
- [ ] **S10 — Sessão sobrevive ao reinício.** Com um usuário logado, pare o servidor (`Ctrl+C`) e rode `python iniciar.py` de novo. *Esperado:* o usuário continua logado e os dados continuam os mesmos.

## 11. Layout e acessibilidade (RNF06, RNF12)

No navegador, pressione F12, ative o modo de dispositivo e escolha 360 × 800 px.

- [ ] **L01 — Início, login e cadastro em 360 × 800.** *Esperado:* sem rolagem horizontal; campos e botões inteiros na tela.
- [ ] **L02 — Catálogo e sacola em 360 × 800.** *Esperado:* os cards se reorganizam em uma coluna; a sacola e o resumo da compra cabem na tela.
- [ ] **L03 — Minha conta em 360 × 800.** *Esperado:* saldo, formulário de crédito, extrato e compras legíveis, sem cortar valores.
- [ ] **L04 — Painel administrativo em 360 × 800.** Produtos, usuários, movimentações e relatórios. *Esperado:* o menu e as listas funcionam; tabelas largas rolam dentro da própria área, sem empurrar a página.
- [ ] **L05 — Desktop.** Repita a navegação em tela cheia. *Esperado:* sem rolagem horizontal.
- [ ] **L06 — Teclado.** Com Tab, percorra o cadastro e a compra sem usar o mouse. *Esperado:* o primeiro Tab mostra o link "Pular para o conteúdo"; o foco é sempre visível; os modais podem ser fechados pelo teclado.
- [ ] **L07 — Erros anunciados.** Em um formulário com erro. *Esperado:* a mensagem aparece junto ao campo, em texto, e não só por cor.
- [ ] **L08 — Navegadores.** Repita os casos A01, C03 e CP05 em pelo menos dois navegadores da lista do RNF01. *Esperado:* mesmo comportamento. Anote quais foram testados.

O checklist completo da ABNT NBR 17225:2025 é registrado em `docs/checklist-acessibilidade-nbr17225.md`, conforme o plano de execução.

## Resultado

| Resultado | Preenchimento |
| --- | --- |
| Casos aprovados | |
| Casos reprovados e issues abertas | |
| Casos não executados e motivo | |
| Evidências (prints, vídeo) | |

## Itens a confirmar neste roteiro

- **[CONFIRMAR: nomes dos botões e das abas]** Os textos em negrito foram conferidos com as telas em 17/11/2026, quando elas ainda estavam sendo finalizadas. Se algum botão ou aba mudar de nome, ajuste o caso correspondente.
- **[CONFIRMAR: códigos dos produtos]** Os exemplos de API usam `id_produto` 2 (Sanduíche Natural) e 4 (Maçã), que são os códigos em um banco criado do zero com `python scripts/banco.py semear`. Confira os códigos no painel antes de usar.
- **[CONFIRMAR: mensagens exatas]** As mensagens de erro citadas entre aspas vêm do código de 17/11/2026; se o texto mudar, o que vale é o comportamento descrito.

## Senha, QR Code e compras por usuário

Casos acrescentados em 17/11/2026. Para os usuários de demonstração, rode `python scripts/criar_demo.py` e veja os dados de acesso com `python scripts/credenciais.py`.

### Senha (RF02 e RF11)

- [ ] **S01 — Trocar a própria senha.** Logado como cliente, abra **Minha conta > Alterar senha**, informe a senha atual, a nova e a confirmação e clique no botão. *Esperado:* mensagem de sucesso, formulário limpo e a sessão continua aberta. Saia e entre de novo: a senha antiga é recusada e a nova funciona.
- [ ] **S02 — Senha atual errada.** Informe uma senha atual incorreta. *Esperado:* erro junto ao campo "Senha atual"; nada muda.
- [ ] **S03 — Regras da nova senha.** Tente uma nova senha fraca, uma igual à atual e uma confirmação diferente. *Esperado:* cada caso é recusado com a mensagem no campo certo.
- [ ] **S04 — Enter não grava.** Pressione Enter nos campos e na caixa "Mostrar senhas". *Esperado:* nada é enviado; só o botão grava.
- [ ] **S05 — Administrador redefine a senha.** No painel, em **Usuários**, clique em **Redefinir senha** na linha de um cliente, defina uma senha provisória e confirme. *Esperado:* mensagem "Senha de ... redefinida."; o cliente entra com a senha provisória e a antiga é recusada.
- [ ] **S06 — Cliente não redefine.** Logado como cliente, no Console: `fetch("/api/admin/usuarios/1/senha", {method: "POST", headers: {"Content-Type": "application/json"}, body: "{}"}).then((r) => console.log(r.status))`. *Esperado:* `403`.

### QR Code (RF13)

- [ ] **Q01 — Tela de QR Codes.** No painel, abra **QR Codes**. *Esperado:* o cartaz da cantina e uma etiqueta por produto ativo, cada uma com nome, preço e código. Com o endereço padrão (`127.0.0.1`), a tela avisa que os códigos só funcionam neste computador.
- [ ] **Q02 — Produto pelo QR Code.** Abra `http://127.0.0.1:5000/html/catalogo_produtos.html?adicionar=1` (troque o número pelo código de um produto com estoque). *Esperado:* o catálogo abre com 1 unidade do produto na sacola e um aviso; o endereço fica sem `?adicionar`; recarregar a página não soma de novo.
- [ ] **Q03 — Produto indisponível.** Repita com o código de um produto inativo, sem estoque ou inexistente, e com `?adicionar=abc`. *Esperado:* aviso "Este produto não está disponível agora." e a sacola não muda.
- [ ] **Q04 — Compra em três passos.** Com o cliente logado e com saldo: abrir o endereço do QR Code, clicar em **Finalizar compra** e em **Confirmar compra**. *Esperado:* compra registrada.
- [ ] **Q05 — Impressão.** Use **Imprimir cartaz da cantina** e **Imprimir etiquetas dos produtos**. *Esperado:* cada botão imprime só a sua parte, sem menu; as etiquetas saem em três colunas, sem etiqueta cortada entre páginas.
- [ ] **Q06 — Pelo celular (opcional).** Com `APP_HOST=0.0.0.0` e `URL_PUBLICA` preenchida no `.env` (veja o README), reinicie o sistema, imprima ou mostre um QR Code na tela e leia com a câmera do celular na mesma rede. *Esperado:* o catálogo abre no celular com o produto na sacola.
- [ ] **Q07 — Somente administrador.** Sem login, abra `http://127.0.0.1:5000/api/qrcode/cantina.svg`. *Esperado:* resposta `401`.

### Compras registradas e consumo por usuário (RF12)

- [ ] **C01 — Aba Compras.** No painel, em **Relatórios > Compras**. *Esperado:* as compras do período, da mais recente para a mais antiga, com data, número, usuário, itens e total; o cartão "Compras no período" bate com a lista.
- [ ] **C02 — Filtro por usuário.** Escolha um usuário no filtro da aba. *Esperado:* só as compras dele; um usuário sem compras mostra a mensagem de lista vazia.
- [ ] **C03 — Consumo por usuário.** Em **Relatórios > Vendas**, confira a tabela "Consumo por usuário". *Esperado:* a soma dos totais dos usuários é igual ao "Total vendido".

### Backup (RNF04)

- [ ] **B01 — Cópia e restauração.** Rode `python scripts/banco.py backup`, faça uma compra de teste e rode `python scripts/banco.py restaurar backups/<arquivo gerado>`. *Esperado:* o arquivo aparece em `backups/`; depois da restauração, a compra de teste não existe mais.
