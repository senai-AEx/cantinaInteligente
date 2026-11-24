# Checklist de acessibilidade — ABNT NBR 17225:2025

Projeto **Cantina Inteligente** (Cantina da Honestidade) — SENAI/SC, Projeto Aplicado II, AV06.

## 1. Resumo

| | |
| --- | --- |
| **Data da auditoria** | 17/11/2026 |
| **Referência** | Checklist da ABNT NBR 17225:2025 da Academia de Acessibilidade (<https://www.academiadeacessibilidade.com.br/ferramentas/checklist-abnt/index.html>), aberto em 17/11/2026: 146 itens em 16 grupos, numerados de 5.1.1 a 5.16.6. A numeração, os títulos, a classificação (Requisito ou Recomendação) e o critério da WCAG 2.2 de cada item vêm dessa página. |
| **Escopo** | As 11 telas do sistema, em `src/frontend/`: `index.html`, `html/login.html`, `html/cadastro.html`, `html/catalogo_produtos.html`, `html/minha_conta.html`, `html/painel_adm.html` (início do painel, criada depois desta auditoria e ainda não revisada), `html/catalogo_produtos_adm.html`, `html/usuarios_adm.html`, `html/movimentacoes_adm.html`, `html/relatorios_adm.html` e `html/qrcodes_adm.html`. Inclui o cabeçalho, o rodapé e o link "Pular para o conteúdo" (`html/base.html`, colocados em todas as telas pelo `javascript/base.js`), os 7 arquivos de `css/` e o conteúdo montado pelos 12 arquivos de `javascript/` (cartões, tabelas, modais e mensagens). |
| **Método** | **Auditoria estática:** leitura do HTML, do CSS e do JavaScript de cada tela, item por item do checklist. Três conferências foram feitas por script sobre os arquivos: identificadores repetidos e referências (`for`, `aria-labelledby`, `aria-describedby`, `aria-controls`) sem alvo; sequência dos cabeçalhos e número de `<h1>` por tela; razão de contraste dos pares de cor pela fórmula da WCAG (seção 4). Esses scripts foram usados só durante a auditoria e não estão no repositório; cada evidência cita o arquivo e o elemento ou a regra para conferência direta no código. Todos os arquivos `.js` passaram em `node --check` depois das correções. |
| **Testes no navegador** | **[A PREENCHER pelo grupo]** — a auditoria foi feita sem abrir o sistema no navegador. Registrar aqui o que foi executado do roteiro da seção 5.3 (navegador e versão, leitor de tela, data e quem testou). |

Nas tabelas, cada caminho de arquivo é relativo a `src/frontend/`.

### Situação dos 146 itens

| Situação | Requisitos | Recomendações | Total |
| --- | ---: | ---: | ---: |
| Atende | 53 | 24 | 77 |
| Atende após correção (corrigido nesta auditoria) | 21 | 11 | 32 |
| Não se aplica | 21 | 10 | 31 |
| Não atende (pendente) | 2 | 4 | 6 |
| **Total** | **97** | **49** | **146** |

**Como ler:**

- **Atende** e **Atende após correção** valem para o código como está hoje. Quando a evidência termina com "Confirmar: T1" (ou outro número), o item só pode ser visto de verdade no navegador: a leitura do código indica que atende, e o teste correspondente da seção 5.3 confirma.
- **Não atende** está detalhado na seção 5.1, com o que falta. São 6 itens: 2 requisitos (5.13.11 e 5.16.2) e 4 recomendações.
- A coluna "O que foi verificado" é um resumo nosso de cada item. O texto oficial é o da norma e o do checklist.

---

## 2. Resultado por grupo

### 5.1 Interação por teclado

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.1.1 Indicador de foco visível | Requisito | Todo elemento que recebe foco mostra um contorno. | Atende | `css/base.css`, regra "Foco sempre visível": `outline: 3px solid var(--cor-primaria)` com `:focus-visible` em `a`, `button`, `input`, `select`, `textarea`, `summary` e `[tabindex]`. Nos dois campos que tiram o próprio contorno (`.busca-produtos input` e `.campo-moeda input`), o contêiner mostra o foco com `:focus-within` (`css/catalogo_produtos.css`, `css/minha_conta.css`). Confirmar: T1. |
| 5.1.2 Elemento em foco totalmente visível | Recomendação | O elemento com foco aparece inteiro, sem nada por cima. | Atende | Não há cabeçalho nem rodapé fixo. Os únicos `position: sticky` são colunas laterais (`.carrinho` em `css/catalogo_produtos.css`, `.menu-admin` em `css/admin.css`), que não ficam sobre o conteúdo. `position: fixed` só existe no fundo dos modais, e o foco fica dentro do modal. Confirmar: T1. |
| 5.1.3 Elemento em foco parcialmente visível | Requisito | O elemento com foco fica ao menos em parte visível. | Atende | Mesma evidência do 5.1.2. |
| 5.1.4 Ordem de foco previsível | Requisito | O Tab segue a ordem visual; o foco não se perde depois de uma ação. | Atende após correção | A ordem do HTML é a ordem da tela (menu, conteúdo, rodapé). Modais: o foco entra no modal e volta ao botão que o abriu (`abrirModal`/`fecharModal` em `javascript/catalogo_produtos_adm.js` e `javascript/usuarios_adm.js`; `abrirCompra`/`fecharCompra` em `javascript/catalogo_produtos.js`). Correção C24: no painel de produtos, depois de editar ou reativar, o foco ia para o começo da página; agora `focarProduto()` devolve o foco ao botão "Editar" do mesmo produto. Confirmar: T1. |
| 5.1.5 Uso de foco | Recomendação | Só recebe foco o que serve para interagir. | Atende | `tabindex="0"` só nas áreas com rolagem (`.tabela-rolagem`, lista de itens do modal de compra quando rola) e nos painéis das abas (`html/relatorios_adm.html`). `tabindex="-1"` só em destinos de foco por script (títulos, `<main>`), fora da ordem do Tab. |
| 5.1.6 Armadilha de foco | Requisito | Nenhum componente prende o teclado sem saída. | Atende | Os modais prendem o Tab de propósito e sempre têm saída: tecla Esc, botão "Fechar" e botão "Cancelar" ou "Voltar" (ouvintes `keydown` em `catalogo_produtos.js`, `catalogo_produtos_adm.js` e `usuarios_adm.js`). Fora dos modais, nenhum código cancela o Tab. Confirmar: T1. |
| 5.1.7 Conteúdo adicional | Recomendação | Não há conteúdo que apareça só com foco ou com o mouse em cima. | Atende | Não há dica flutuante nem submenu; nenhum atributo `title` nos HTML nem nos JS; os `:hover` só mudam cor, sombra e posição do cartão. |
| 5.1.8 Conteúdo adicional persistente | Requisito | Conteúdo que aparece com foco ou mouse fica na tela até ser dispensado. | Não se aplica | Não existe conteúdo desse tipo (ver 5.1.7). |
| 5.1.9 Conteúdo adicional dispensável | Requisito | Esse conteúdo pode ser dispensado sem mover o foco. | Não se aplica | Não existe conteúdo desse tipo (ver 5.1.7). |
| 5.1.10 Atalhos de teclado | Recomendação | Não há atalho de uma tecla só. | Atende | Os `keydown` tratam apenas Esc e Tab (modais), setas, Home e End (abas, só com o foco nelas) e Enter (regra de não gravar por Enter). Nenhuma letra, número ou símbolo dispara ação. |
| 5.1.11 Atalhos de teclado sem tecla modificadora | Requisito | Atalho de tecla única pode ser desligado ou remapeado. | Não se aplica | Não há atalhos de tecla única (ver 5.1.10). |
| 5.1.12 Acessibilidade por teclado total | Recomendação | Tudo funciona pelo teclado. | Atende após correção | Todos os controles são elementos nativos (`<a>`, `<button>`, `<input>`, `<select>`, `<textarea>`). Abas dos relatórios: setas, Home e End (`javascript/relatorios_adm.js`). Tabelas largas rolam pelo teclado (`tabindex="0"` em `.tabela-rolagem`). Correção C12: a lista de itens do modal "Finalizar compra" rola dentro do modal e não recebia foco; agora recebe quando há rolagem (`renderizarRevisao` em `javascript/catalogo_produtos.js`). Confirmar: T1. |
| 5.1.13 Acessibilidade por teclado parcial | Requisito | Função feita com o mouse tem equivalente no teclado. | Atende | Não há função exclusiva do mouse: nenhum arrastar, duplo clique, `mousedown` ou gesto. Todos os ouvintes de ação usam `click`, `change`, `input` ou `submit`. |
| 5.1.14 Mecanismos de entrada simultâneos | Recomendação | O sistema não limita o tipo de entrada (toque, mouse, teclado). | Atende | Nenhum código detecta ou bloqueia o tipo de dispositivo de entrada. |
| 5.1.15 Comportamento de componentes customizados | Recomendação | Componentes feitos à mão se comportam como o esperado. | Atende | Modais (Esc fecha, Tab fica dentro, foco volta), abas (`role="tablist"`, setas trocam de aba), botões de alternância (`aria-pressed`) e menu recolhível (`aria-expanded`) seguem os padrões da WAI-ARIA. Confirmar: T1 e T2. |
| 5.1.16 Instruções para componentes customizados | Requisito | Componente complexo e pouco previsível traz instruções. | Não se aplica | Não há componente de comportamento pouco previsível (ver 5.1.15). Onde a tela faz algo sozinha, isso está escrito: "A lista é atualizada enquanto você digita" (`html/usuarios_adm.html`, `html/qrcodes_adm.html`). |

### 5.2 Imagens

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.2.1 Texto alternativo para imagens de conteúdo | Requisito | Imagem com informação tem texto alternativo. | Atende | Foto do produto: `alt="Foto de <nome>"` (`criarImagem` em `javascript/catalogo_produtos.js`) e `alt="<nome>"` no painel (`criarCard` em `javascript/catalogo_produtos_adm.js`). Prévia da foto: `alt="Prévia da foto do produto"` (`html/catalogo_produtos_adm.html`). QR Codes: `alt="QR Code que abre o catálogo da Cantina da Honestidade"` (`html/qrcodes_adm.html`) e `alt="QR Code do produto <nome>"` (`criarEtiqueta` em `javascript/qrcodes_adm.js`). Confirmar: T2. |
| 5.2.2 Texto alternativo para imagens funcionais | Requisito | Imagem que é link ou botão descreve a função. | Não se aplica | Nenhuma imagem é link ou botão. Os símbolos dos botões são caracteres com `aria-hidden`, e o botão tem texto ou `aria-label` (ex.: `aria-label="Fechar"` no "×"). |
| 5.2.3 Texto alternativo para imagens decorativas | Requisito | Imagem decorativa fica escondida do leitor de tela. | Atende após correção | Emojis e símbolos decorativos têm `aria-hidden="true"`: `.abertura-ilustracao`, `.icone-passo` e `.icone-valor` (`index.html`); `.imagem-fallback` (`javascript/catalogo_produtos.js`); "←", "↓", "⌕", "⚠", "♡". Correções C21, C22 e C27: faltava no "＋" de um botão e nos números "01–03" do formulário de produto, e as marcas "✓ " feitas pelo CSS agora têm texto alternativo vazio (`content: "✓ " / ""`). Confirmar: T2. |
| 5.2.4 Descrição para imagens complexas | Requisito | Gráfico, mapa ou diagrama tem descrição detalhada. | Não se aplica | Não há gráfico, mapa nem diagrama em imagem. A barra da tabela "Vendas por dia" é decorativa (`aria-hidden` em `criarBarra`, `javascript/relatorios_adm.js`) e o valor está escrito ao lado. |
| 5.2.5 Imagens de texto | Requisito | Texto não é entregue como imagem. | Atende | Não há imagem de texto: logotipo, títulos, selos e cartaz do QR Code são texto HTML. |
| 5.2.6 Texto alternativo para mapas de imagens | Requisito | Cada área clicável de um mapa de imagem tem texto. | Não se aplica | Não há `<map>` nem `<area>`. |

### 5.3 Cabeçalhos

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.3.1 Semântica de cabeçalho | Requisito | Títulos são marcados com `<h1>` a `<h6>`. | Atende | Todos os títulos de seção usam `<h1>`, `<h2>` ou `<h3>`, inclusive os criados pelo JavaScript (nome do produto, "Compra nº …", nome na etiqueta do QR Code). Observação: o rótulo "Administração" do menu lateral é um `<p>` (`.menu-admin-titulo`); ele identifica o menu, que tem nome próprio em `<nav aria-label="Painel administrativo">`. Confirmar: T2. |
| 5.3.2 Uso de cabeçalhos | Requisito | Cabeçalho só é usado para dar título a uma seção. | Atende | Nenhum `<h*>` é usado só para deixar o texto grande; destaques sem função de título usam `<strong>`, `<span>` ou `<p>` com classe. |
| 5.3.3 Cabeçalho principal | Recomendação | Existe um, e só um, `<h1>` que identifica a tela. | Atende | Conferido por script nas 10 telas, 1 `<h1>` em cada: "Cantina da Honestidade", "Entrar na cantina", "Criar conta", "Escolha com carinho. Contribua com confiança.", "Minha conta", "Produtos", "Usuários", "Movimentações", "Relatórios" e "QR Codes". |
| 5.3.4 Seções com cabeçalhos | Recomendação | Toda seção de conteúdo tem um cabeçalho. | Atende após correção | Cada `<section>` tem `<h1>`, `<h2>` ou `<h3>` (alguns só para leitor de tela, com a classe `.somente-leitor`). Correções C08 e C18: faltava na faixa de vantagens do início (`index.html`, `#titulo-vantagens`) e no resumo, nos filtros e na lista do painel de produtos (`html/catalogo_produtos_adm.html`, `#titulo-resumo`, `#titulo-filtros`, `#titulo-lista`). |
| 5.3.5 Estrutura de cabeçalhos | Requisito | Os níveis seguem uma ordem lógica, sem saltos. | Atende após correção | Sequência conferida por script em cada tela (ex.: relatórios `h1, h2, h2, h3, h3, h3, h2, h3…`). Correção C18: no painel de produtos os cartões (`<h3>`) vinham logo depois do `<h1>`; agora há `<h2>` entre eles. Os títulos criados pelo JavaScript são `<h3>` dentro de seções com `<h2>`. |

### 5.4 Regiões

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.4.1 Semântica de região | Requisito | As regiões usam o elemento certo para a função. | Atende | `<header>`, `<nav>` e `<footer>` em `html/base.html`; `<main id="conteudo-principal">` em todas as telas; `<aside>` para a sacola e para o menu do painel; `<section>` com nome; `role="search"` nas buscas (`html/catalogo_produtos.html`, `html/usuarios_adm.html`, `html/qrcodes_adm.html`). Confirmar: T2. |
| 5.4.2 Uso de regiões | Requisito | O conteúdo é organizado em regiões pelo tipo. | Atende | Menu no `<nav>`, conteúdo da tela no `<main>`, dados da iniciativa no `<footer>`. |
| 5.4.3 Conteúdo em regiões | Recomendação | Todo o conteúdo fica dentro de alguma região. | Atende | Tudo fica dentro de `<header>`, `<main>`, `<aside>` ou `<footer>`. Ficam fora só o link "Pular para o conteúdo" (precisa ser o primeiro elemento) e os modais, que são regiões próprias (`role="dialog"` com nome). |
| 5.4.4 Regiões únicas | Recomendação | Há um só cabeçalho de página, um só `<main>` e um só rodapé. | Atende | Um `<header>` e um `<footer>` de página (de `html/base.html`) e um `<main>` por tela (conferido por script). O `<header class="cabecalho-relatorio">` fica dentro de `<section>`, então não é cabeçalho de página. |
| 5.4.5 Regiões identificadas unicamente | Requisito | Regiões do mesmo tipo têm nomes diferentes. | Atende | Navegações: "Menu principal", "Mapa do site", "Painel administrativo" e "Seções da minha conta". Seções com `aria-labelledby` apontando para títulos diferentes. Áreas de tabela com nomes diferentes (legenda ou título de cada tabela). |

### 5.5 Listas

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.5.1 Semântica de lista | Requisito | Listas são marcadas como ordenada, não ordenada ou de definição. | Atende após correção | `<ol>` nos passos de "Como funciona" e nas compras; `<ul>` nos menus, regras da senha, itens da compra e etiquetas; `<dl>` nos pares nome–valor (dados da conta, valores da compra, cartões de resumo). Correções C10 e C11: listas sem marcador (`list-style: none`) ganharam `role="list"` (regras da senha, "Minhas compras", itens de cada compra, itens do modal, menu lateral), e os cartões de produto e os itens da sacola, que eram blocos soltos, agora são `role="list"` com `role="listitem"` (`javascript/catalogo_produtos.js`, `javascript/catalogo_produtos_adm.js`). Confirmar: T2. |
| 5.5.2 Uso de listas | Requisito | Lista agrupa itens da mesma natureza, não serve para layout. | Atende | Nenhuma lista é usada só para posicionar elementos; o layout é feito com `grid` e `flex`. |

### 5.6 Tabelas

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.6.1 Semântica de tabela | Requisito | Dados tabulares usam `<table>`. | Atende | 10 tabelas: extrato (`html/minha_conta.html`), usuários (`html/usuarios_adm.html`), movimentações (`html/movimentacoes_adm.html`) e 7 nos relatórios (`html/relatorios_adm.html`), todas com `<thead>` e `<tbody>`. |
| 5.6.2 Uso de tabelas | Requisito | Tabela não é usada para layout. | Atende | Nenhuma tabela de layout. |
| 5.6.3 Cabeçalhos de tabela | Requisito | Cada célula se liga ao cabeçalho da coluna e da linha. | Atende | Todo `<th>` do `<thead>` tem `scope="col"`. Onde a linha tem um nome (usuário, produto, dia, número da compra), essa célula é `<th scope="row">` (função `celula(…, true)` em `javascript/usuarios_adm.js` e `javascript/relatorios_adm.js`). Confirmar: T2. |
| 5.6.4 Título de tabela | Recomendação | Toda tabela tem título ou legenda. | Atende | As 10 tabelas têm `<caption>` (10 ocorrências conferidas). |
| 5.6.5 Título de tabela associado | Requisito | O título está ligado à tabela no código. | Atende | O título é o próprio `<caption>`, dentro do `<table>`. |
| 5.6.6 Descrição para tabelas complexas | Recomendação | Tabela complexa tem descrição em texto. | Não se aplica | Não há tabela complexa: todas têm uma linha de cabeçalho e nenhuma célula mesclada (o `colspan` só aparece na linha "nenhum resultado"). |

### 5.7 Links e Navegação

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.7.1 Semântica de link | Requisito | Links são `<a href>`. | Atende | Todos os links são `<a>` com `href`; não há `<div>` nem `<span>` clicável. |
| 5.7.2 Uso de links | Requisito | Link serve para navegar, não para executar ação. | Atende | Links levam a telas ou a seções; ações (salvar, excluir, sair, filtrar) são `<button>`. Ver também 5.8.2. |
| 5.7.3 Propósito do link sem contexto | Recomendação | O texto do link, sozinho, diz para onde ele leva. | Atende | Textos como "Criar minha conta", "Ver produtos", "Adicionar crédito", "Ver minhas compras", "Ir para a sacola", "Pular para o conteúdo". Não há "clique aqui" nem "saiba mais". Na tabela de usuários o nome entra no rótulo: `aria-label="Movimentações de <nome>"`. |
| 5.7.4 Propósito do link no contexto | Requisito | O link, com o texto em volta, deixa claro o destino. | Atende | Coberto pelo 5.7.3. |
| 5.7.5 Links com identificação consistente | Recomendação | Links com o mesmo nome não levam a destinos diferentes. | Atende após correção | Correção C28: nas 5 telas do painel havia dois links "Produtos" — o do cabeçalho (catálogo) e o do menu lateral (gestão de produtos). O do menu lateral passou a ter o nome acessível "Produtos do painel" (texto oculto `.somente-leitor`). Ressalva: na tela, a palavra visível continua "Produtos" nos dois menus, que ficam em blocos separados. |
| 5.7.6 Links que abrem em nova guia ou janela | Recomendação | Avisa quando o link abre nova guia. | Não se aplica | Nenhum link usa `target`; nada abre em nova guia. |
| 5.7.7 Links para arquivos (não HTML) | Recomendação | Informa formato e tamanho do arquivo. | Não se aplica | Não há link para download de arquivo. |
| 5.7.8 Links para sites externos | Recomendação | Avisa quando o link sai do site. | Não se aplica | Não há link para outro site. |
| 5.7.9 Texto complementar do link | Recomendação | Não há `title` repetindo o texto do link. | Atende | Nenhum link tem atributo `title`. |
| 5.7.10 Links adjacentes | Recomendação | Links vizinhos não levam ao mesmo destino. | Atende | No cabeçalho, "Produtos" e "Minha sacola" levam a seções diferentes (`#produtos` e `#carrinho`). Não há imagem e texto como dois links seguidos para o mesmo lugar. |
| 5.7.11 Contornar blocos de conteúdo | Recomendação | Há um link para pular o menu. | Atende | `<a class="pular-conteudo" href="#conteudo-principal">Pular para o conteúdo</a>` (`html/base.html`); aparece ao receber foco (`.pular-conteudo:focus` em `css/base.css`). Confirmar: T1. |
| 5.7.12 Contornar blocos em conjunto de páginas | Requisito | O mesmo mecanismo existe em todas as telas. | Atende | `carregarLayout` em `javascript/base.js` coloca o link como primeiro elemento do `<body>` nas 10 telas (todas têm `#header-container` e `<main>`). |
| 5.7.13 Alternativas para localização | Requisito | Há mais de uma forma de chegar a cada tela. | Atende após correção | Correção C02: as telas de usuários, movimentações, relatórios e QR Codes só eram alcançadas pelo menu lateral do painel. Agora há três caminhos: menu do cabeçalho, menu lateral do painel e o "Mapa do site" no rodapé de todas as telas (`<nav class="mapa-site">` em `html/base.html`, com os itens conforme a sessão). |
| 5.7.14 Localização em conjunto de páginas | Recomendação | O sistema mostra em que tela a pessoa está. | Atende após correção | `<title>` e `<h1>` de cada tela; menu lateral com `aria-current="page"` e destaque por barra, fundo e negrito. Correção C04: o menu do cabeçalho e o mapa do site não marcavam a tela atual; agora `marcarPaginaAtual()` (`javascript/base.js`) põe `aria-current` e o CSS destaca com barra e negrito (`.navegacao a[aria-current]`). |
| 5.7.15 Navegação consistente | Requisito | Menus repetidos mantêm a mesma ordem. | Atende | Cabeçalho e rodapé vêm de um único arquivo (`html/base.html`). O menu lateral tem os mesmos 7 itens (Início, Produtos, Usuários, Movimentações, Relatórios, QR Codes e Ver catálogo), na mesma ordem, nas 6 telas do painel. |
| 5.7.16 Ajuda consistente | Requisito | Mecanismo de ajuda repetido fica sempre no mesmo lugar. | Atende | O único mecanismo de ajuda é a lista "Siglas e termos usados no sistema", no rodapé comum (`<details class="glossario">` em `html/base.html`): mesma posição em todas as telas. |

### 5.8 Botões e Controles

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.8.1 Semântica de botão | Requisito | Botões são `<button>`. | Atende | Todos os botões são `<button>` com `type` declarado (conferido por script: nenhum `<button>` sem `type`); os criados pelo JavaScript recebem `type = "button"`. |
| 5.8.2 Uso de botões | Requisito | Botão serve para acionar função, não para navegar. | Atende após correção | Correção C13: "Entrar para finalizar", no modal de compra, era um `<button>` que levava à tela de login; agora é `<a href="/html/login.html">` (`html/catalogo_produtos.html`). Os demais botões executam ações na própria tela. |
| 5.8.3 Propósito do botão | Requisito | O nome do botão diz o que ele faz. | Atende após correção | Botões com texto ("Salvar produto", "Confirmar compra", "Lançar ajuste"). Botões só com símbolo têm `aria-label` ("Fechar", "Diminuir quantidade de <produto>"). Botões que se repetem em lista levam o nome do item: `aria-label="Editar <usuário>"` (`javascript/usuarios_adm.js`). Correção C23: no painel de produtos, "Editar", "Excluir" e "Reativar" eram iguais em todos os cartões; agora `aria-label="Editar: <produto>"` (`criarBotao` em `javascript/catalogo_produtos_adm.js`). Confirmar: T2. |
| 5.8.4 Identificação consistente na página | Recomendação | Mesma função, mesmo nome, na mesma tela. | Atende após correção | Correção C21: no painel de produtos, dois botões abriam o mesmo cadastro com nomes diferentes ("Novo produto" e "Cadastrar produto"); os dois agora se chamam "Cadastrar produto". Depois, o botão do menu lateral foi removido: resta só o do topo da lista. |
| 5.8.5 Identificação consistente em conjunto de páginas | Requisito | Mesma função, mesmo nome, em todas as telas. | Atende | "Recolher menu", "Fechar", "Cancelar", "Salvar alterações", "Limpar filtros", "Imprimir" e "Tentar novamente" têm o mesmo texto em todas as telas em que aparecem; cabeçalho e rodapé são únicos. |
| 5.8.6 Área de acionamento (aprimorada) | Recomendação | Alvos com pelo menos 44 × 44 px. | Atende após correção | `min-height: 44px` em `.botao` (`css/base.css`), filtros, abas, botões de tabela, botões de quantidade (44 × 44) e "×" dos modais (44 × 44). Caixas de seleção e rádios ficam dentro de um `<label>` com 44 px de altura. Correções C02, C06 e C16: o menu do cabeçalho nas telas do painel tinha 40 px, o logotipo cerca de 33 px, o link do rodapé 24 px e `.link-acao` 42,5 px; todos passaram a ter `min-height: 44px`. O seletor de arquivo tem o tamanho definido pelo navegador (exceção do item). |
| 5.8.7 Área de acionamento (mínima) | Requisito | Alvos com pelo menos 24 × 24 px. | Atende | Coberto pelo 5.8.6: o menor alvo tem 44 px de altura. |
| 5.8.8 Mudança de contexto previsível | Recomendação | A tela só muda de contexto quando a pessoa pede. | Atende | Navegação e modais só abrem por clique em link ou botão. Os redirecionamentos de acesso (tela que exige login, sessão encerrada) acontecem ao abrir a tela ou em resposta a uma ação da pessoa; no painel, com a mensagem "Sua sessão terminou. Abrindo a tela de login…". |
| 5.8.9 Mudança de contexto previsível no foco | Requisito | Receber foco não muda o contexto. | Atende | Não há ouvinte de `focus`; nenhum elemento navega, abre modal ou envia formulário ao receber foco. |
| 5.8.10 Mudança de contexto previsível na entrada | Requisito | Digitar ou escolher uma opção não muda o contexto sem aviso. | Atende | Buscas e filtros só atualizam a lista da própria tela, e isso está avisado ao lado do campo ("A lista é atualizada enquanto você digita", "A lista de compras é atualizada ao escolher"). Nenhum campo navega ou envia dados ao ser alterado. |
| 5.8.11 Acionamento por ponteiro único | Requisito | A ação acontece ao soltar o clique, não ao apertar. | Atende | Todas as ações usam o evento `click`; não há `mousedown`, `touchstart` nem `pointerdown`. |
| 5.8.12 Operação por gestos de ponteiro | Requisito | Gesto com vários dedos ou com trajeto tem alternativa simples. | Não se aplica | Não há gestos: tudo é feito com clique ou toque simples. |
| 5.8.13 Operação por movimento de arrastar | Requisito | Arrastar tem alternativa. | Não se aplica | Nada é arrastado. |
| 5.8.14 Operação por movimento | Requisito | Função acionada por balançar ou inclinar o aparelho tem alternativa. | Não se aplica | Nenhuma função usa o movimento do aparelho. |
| 5.8.15 Controles com retorno | Recomendação | O controle acionado dá um retorno que se percebe. | Atende | Botão de envio troca o texto e fica ocupado ("Salvando…", `Cantina.comBotaoOcupado` em `javascript/base.js`); mensagens de resultado em regiões `role="status"`; filtros e abas mudam de estado visual e de `aria-pressed`/`aria-selected`; a sacola atualiza o contador e anuncia o resumo (`anunciarSacola`). Confirmar: T2. |

### 5.9 Formulários e Entrada de Dados

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.9.1 Rótulo de campo | Requisito | Todo campo tem rótulo (ou propósito visível evidente e nome acessível). | Atende após correção | Todos os campos têm `<label>` (conferido por script). Nas duas buscas de produtos o rótulo é texto oculto, e o propósito aparece no ícone e no texto de exemplo. Correção C19: na busca do painel de produtos o `<label>` só tinha o ícone (oculto) e o campo ficava sem nome; agora tem "Buscar por nome, categoria ou código" (`html/catalogo_produtos_adm.html`). Confirmar: T2. |
| 5.9.2 Rótulo de campo previsível | Requisito | O rótulo fica sempre na mesma posição. | Atende | Rótulo acima do campo (`.campo-formulario` com `flex-direction: column`); em caixas de seleção e rádios, o texto fica à direita. |
| 5.9.3 Rótulo de campo associado | Requisito | O rótulo está ligado ao campo no código. | Atende | `<label for="…">` com o `id` do campo, ou `<label>` envolvendo o campo; conferido por script: nenhum `for` sem alvo. |
| 5.9.4 Rótulo de campo descritivo | Requisito | O rótulo diz o que preencher. | Atende | Ex.: "Matrícula, e-mail ou CPF", "Valor depositado", "Preço de venda (R$)", "Confirmar nova senha", "Buscar por nome, matrícula ou e-mail". |
| 5.9.5 Textos de ajuda previsíveis | Requisito | A ajuda fica sempre na mesma posição. | Atende | A dica fica logo abaixo do campo (`<small class="dica-campo">`), ligada por `aria-describedby`; a mensagem de erro vem em seguida (`<small class="erro-campo">`). |
| 5.9.6 Campos relacionados | Requisito | Campos relacionados são agrupados no código. | Atende após correção | "Tipo de ajuste" usa `<fieldset>` com `<legend>` (`html/usuarios_adm.html`); grupos de botões usam `role="group"` com nome (categorias, valores comuns, atalhos de período). Correção C22: as três partes do formulário de produto ("Identificação", "Preços e estoque", "Detalhes") passaram a ser `role="group"` com `aria-labelledby` (`html/catalogo_produtos_adm.html`). |
| 5.9.7 Campos obrigatórios | Requisito | O campo obrigatório é identificado para todas as pessoas. | Atende após correção | Asterisco no rótulo, legenda "Campo obrigatório" ou "Campos com * são obrigatórios" e atributo `required` (lido pelo leitor de tela). Correção C29: nos filtros de data de movimentações e de relatórios havia o asterisco sem a legenda; ela foi incluída. Confirmar: T2. |
| 5.9.8 Tipo de dado determinado | Requisito | O campo declara o tipo de dado da pessoa. | Atende | `autocomplete` nos dados da própria pessoa: `username` e `current-password` (`html/login.html`); `name`, `username`, `email` e `new-password` (`html/cadastro.html`); `current-password` e `new-password` (`html/minha_conta.html`). Tipos: `type="email"`, `type="password"`, `type="date"`, `type="search"`, `inputmode="numeric"`. No painel, onde o administrador digita dados de outra pessoa, `autocomplete="off"`. |
| 5.9.9 Mensagem de erro descritiva | Requisito | O erro é descrito em texto e o campo é identificado. | Atende após correção | `Cantina.exibirErros` (`javascript/base.js`) escreve a mensagem abaixo do campo, marca `aria-invalid="true"`, liga a mensagem por `aria-describedby`, avisa em `<p class="feedback-form" role="alert">` e leva o foco ao primeiro campo com erro. O painel de produtos faz o mesmo em `exibirErrosFormulario`. Correção C25: o erro ao excluir um produto aparecia atrás do modal; agora aparece dentro dele (`#erro-excluir-produto`). Confirmar: T2. |
| 5.9.10 Sugestão de correção | Recomendação | A mensagem diz como corrigir. | Atende | Ex.: "O CPF precisa ter 11 números.", "Informe um e-mail válido, como nome@exemplo.com.", "A senha precisa ter de 8 a 72 caracteres, com pelo menos uma letra e um número.", "O desconto não pode ser maior que o saldo atual (R$ …)". No login, a mensagem é genérica de propósito, por segurança. |
| 5.9.11 Prevenção de erro | Requisito | Todo formulário permite conferir, confirmar ou desfazer. | Atende | Todos os formulários são validados na tela e no servidor, e os erros voltam para correção antes de gravar (conferir). Compra: etapa de conferência com total e saldo antes de "Confirmar compra". Inativar usuário e excluir produto: modal de confirmação, e as duas ações podem ser desfeitas ("Reativar"). Ajuste de saldo: mostra o saldo resultante antes de lançar e pode ser compensado por outro ajuste. Crédito: exige marcar a declaração. Cadastro de produto e de usuário pode ser corrigido depois, pela edição no painel. |
| 5.9.12 Prevenção de erro para formulários críticos | Requisito | Formulário financeiro ou legal permite conferir, confirmar ou desfazer. | Atende | Coberto pelo 5.9.11 (compra, crédito e ajuste de saldo). Além disso, a chave de idempotência impede lançamento em dobro ao reenviar (`garantirChave` em `javascript/catalogo_produtos.js`, `chaveDoCredito` em `javascript/minha_conta.js`). |
| 5.9.13 Ajuda contextual | Recomendação | Há dicas de preenchimento junto aos campos. | Atende | Dicas `.dica-campo` (ex.: "Somente números, de 4 a 20 dígitos."; "Digite os 11 números: os pontos e o traço entram sozinhos."), lista das regras da senha com marca de cumprida ou não, máscaras de CPF e de moeda. |
| 5.9.14 Botão de submissão | Recomendação | Todo formulário tem botão de envio. | Atende após correção | Correção C30: três formulários de consulta atualizavam a lista sozinhos e não tinham botão de envio; ganharam "Buscar" (`html/usuarios_adm.html`, `html/qrcodes_adm.html`) e "Atualizar lista" (aba Compras de `html/relatorios_adm.html`). Os demais 11 formulários já tinham `<button type="submit">`. |
| 5.9.15 Reentrada de dados | Requisito | Não pede de novo o que já foi informado. | Atende | Nenhum processo pede o mesmo dado duas vezes: a compra usa a sacola e a conta já conhecidas, e depois do login a pessoa volta à tela em que estava (`?destino=`). A única repetição é "Confirmar senha", exceção de segurança prevista no item. |
| 5.9.16 Validação sensorial ou por movimento | Requisito | Verificação do tipo CAPTCHA tem alternativa. | Não se aplica | Não há CAPTCHA nem outra verificação sensorial ou por movimento. |
| 5.9.17 Autenticação acessível (aprimorado) | Recomendação | Entrar no sistema não exige teste de memória ou de raciocínio sem ajuda. | Atende | Login com identificador e senha, sem enigma, cálculo ou imagem. Há ajuda para a senha: os campos aceitam colar e gerenciador de senhas (`autocomplete="username"` e `"current-password"`; não há bloqueio de colar) e existe a opção "Mostrar senha". |
| 5.9.18 Autenticação acessível (mínima) | Requisito | Mesmo critério, com exceções. | Atende | Coberto pelo 5.9.17. |

### 5.10 Apresentação

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.10.1 Características sensoriais | Requisito | As instruções não dependem só de cor, forma ou posição. | Atende | As instruções citam o nome do botão ou do campo ("ao clicar em Salvar produto", "Campos com * são obrigatórios"). "Revise os campos destacados" vem junto com a mensagem em texto de cada campo e com o foco no primeiro erro. |
| 5.10.2 Ordem de apresentação | Requisito | A ordem visual não muda o sentido da ordem do código. | Atende | O CSS não reordena o conteúdo; o único `order` (sacola em telas até 1000 px, `css/catalogo_produtos.css`) mantém a ordem do HTML (produtos, depois sacola). |
| 5.10.3 Orientação de exibição | Requisito | Funciona em retrato e em paisagem. | Atende | Não há bloqueio de orientação (nenhuma regra `orientation` no CSS nem no JavaScript). Confirmar: T4. |
| 5.10.4 Design responsivo | Requisito | Com 320 px de largura, não há rolagem horizontal nem perda de conteúdo (tabelas de dados são exceção). | Atende | Larguras fluidas (`min()`, `minmax(0, 1fr)`), menus com quebra de linha e pontos de quebra em 380, 480, 520, 600, 640, 760, 860, 900 e 1000 px. As larguras mínimas fixas são só das tabelas (`.tabela-usuarios`, `.tabela-movimentacoes` etc.), que rolam dentro de `.tabela-rolagem` (`overflow-x: auto`), como a exceção do item permite. Confirmar: T4 e os testes L01 a L05 de `docs/testes-manuais.md`. |
| 5.10.5 Área do indicador de foco visível | Recomendação | O contorno de foco dá a volta no elemento, com 2 px ou mais. | Atende | `outline: 3px solid` com `outline-offset: 2px` (`css/base.css`): contorno inteiro, de 3 px. |

### 5.11 Uso de Cores

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.11.1 Uso de cores | Requisito | A cor não é o único jeito de passar uma informação. | Atende após correção | Valores com sinal além da cor ("+ R$ 5,00", "− R$ 2,00", e "entrada de" ou "saída de" para leitor de tela, em `criarLinhaDoExtrato`); situações em texto ("Ativo", "Inativo", "Sem estoque", "Últimas unidades"); campo com erro tem mensagem em texto; regras da senha com "✓" ou "○"; página atual do menu com barra e negrito; aba aberta com borda. Correções C26 e C02: o filtro selecionado do painel de produtos era só um fundo branco sobre cinza muito claro (1,07:1) e ganhou contorno e "✓"; os links do rodapé não tinham sublinhado. |
| 5.11.2 Contraste para texto (aprimorado) | Recomendação | Texto com 7:1 (4,5:1 se for grande). | **Não atende** | O texto principal passa (#2b2b2b sobre branco: 14,16:1), mas os textos de apoio e as cores da identidade ficam entre 4,5:1 e 7:1: laranja #b8520b (4,94:1), texto suave #5f6b62 (5,58:1), verde de sucesso #2e7d32 (5,13:1), vermelho de erro #b3261e (6,54:1). Ver seção 5.1. |
| 5.11.3 Contraste para texto (mínimo) | Requisito | Texto com 4,5:1 (3:1 se for grande). | Atende após correção | Calculados mais de 110 pares texto/fundo usados nos 7 CSS (os principais estão na seção 4). Menor valor em texto normal: 4,60:1; em texto grande: 4,26:1. Correção C26: o texto de exemplo da busca do painel de produtos usava o cinza padrão do navegador (cerca de 2,3:1) e passou a `var(--cor-texto-suave)` (5,58:1); o preço dos cartões do painel foi de #c9631b (3,97:1, só passava como texto grande) para `var(--cor-primaria)` (4,94:1). |
| 5.11.4 Contraste para componentes | Requisito | Bordas de campos e estados de componentes com 3:1. | Atende após correção | Bordas dos campos: #7f8a82 (3,58:1) e #7d8a80 (3,61:1). Correção C26: no painel de produtos as bordas dos campos (#dfe5de, 1,24:1) e da busca (#e0e6df, 1,27:1) passaram a `var(--cor-contorno)` (#7d8a80). Botões com borda clara ("Sair", "Inativar") são identificados pelo texto, que tem contraste; controles desabilitados ficam de fora do item. |
| 5.11.5 Contraste para objetos gráficos | Requisito | Partes de gráficos com 3:1. | Atende | Barra dos relatórios #3d6545 sobre o trilho #e3e9e2: 5,41:1 (e o valor está em texto). Marcas "✓" e "○" na cor do texto. QR Codes em preto sobre branco (`.qr-imagem` com `background: #ffffff`). |
| 5.11.6 Contraste para indicador de foco visível | Requisito | Contorno de foco com 3:1 em relação ao fundo. | Atende após correção | Laranja #b8520b: 4,94:1 sobre branco, 4,76:1 sobre o creme, 4,64:1 sobre o fundo do painel, 4,32:1 sobre o fundo de erro. Correção C05: sobre o rodapé escuro (#333333) o laranja tinha 2,56:1; ali o contorno agora é branco (12,63:1), em `.footer a:focus-visible`. |

### 5.12 Conteúdo Textual

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.12.1 Espaçamento entre as linhas | Requisito | Entrelinha de 1,5, ou dá para aumentar sem perder conteúdo. | Atende após correção | `body { line-height: 1.5 }` (`css/base.css`). Títulos e rótulos curtos usam entrelinha menor, e nenhum bloco de texto tem altura fixa com corte: o texto pode crescer. Correções C14 e C32: a descrição do produto no catálogo era cortada em 2 linhas (`-webkit-line-clamp`) e tinha entrelinha 1,45; agora aparece inteira, com 1,5; o texto de apoio do formulário de produto foi de 1,4 para 1,5. Confirmar: T5. |
| 5.12.2 Espaçamento entre os parágrafos | Requisito | Dá para aumentar o espaço entre parágrafos sem perder conteúdo. | Atende | Nenhum bloco de texto tem altura fixa com corte: os `overflow: hidden` do CSS estão em contêineres sem altura fixa (topo das telas, cartões), em imagens e na barra decorativa. O item é atendido pela alternativa "mecanismo": o ajuste é feito pelo navegador ou por folha de estilo da pessoa. Confirmar: T5. |
| 5.12.3 Espaçamento entre as letras | Requisito | Dá para aumentar o espaço entre letras sem perder conteúdo. | Atende | Mesma evidência do 5.12.2. Confirmar: T5. |
| 5.12.4 Espaçamento entre as palavras | Requisito | Dá para aumentar o espaço entre palavras sem perder conteúdo. | Atende | Mesma evidência do 5.12.2. Confirmar: T5. |
| 5.12.5 Alinhamento de blocos de texto | Recomendação | Texto alinhado à esquerda. | **Não atende** | O texto corrido é alinhado à esquerda e não há texto justificado, mas alguns blocos curtos são centralizados por desenho: título e subtítulo do login e do cadastro, rodapé, cabeçalho de "Como funciona", mensagens de lista vazia, etapa "Compra registrada!" e cartaz do QR Code. Ver seção 5.1. |
| 5.12.6 Largura de blocos de texto | Requisito | Linhas com até 80 caracteres, ou dá para ajustar a largura. | Atende após correção | Correção C17: em telas largas alguns parágrafos passavam de 120 caracteres por linha; os parágrafos descritivos agora têm `max-width: 70ch` (cerca de 78 caracteres): `.texto-cartao`, `.cabecalho-conta p`, `.mensagem-honestidade p`, `.introducao p`, `.texto-apoio`, `.contador-lista`, `.texto-modal`, `.qr-aviso-local p`, `.estado-lista p`. Caixas de aviso e legendas de tabela acompanham a largura do contêiner: nelas vale a alternativa do item, porque o layout é fluido e a linha encurta ao estreitar a janela ou ampliar o zoom. Confirmar: T4. |
| 5.12.7 Texto redimensionado | Requisito | Com zoom de 200% não há perda de conteúdo nem rolagem horizontal para ler. | Atende após correção | Não há bloqueio de zoom (5.13.5), o layout é responsivo (5.10.4) e nenhum texto fica em caixa de altura fixa. Correção C14: a descrição do produto era cortada em 2 linhas, o que escondia mais texto quanto maior o zoom. Confirmar: T4. |
| 5.12.8 Semântica de texto especial | Requisito | Ênfase, citação e outros textos especiais são marcados no código. | Atende | Ênfase com `<strong>`; datas com `<time datetime>` (`criarData` em `javascript/minha_conta.js`); dicas e erros com `<small>`; pares nome–valor com `<dl>`. Não há citações. Observação: as siglas não usam `<abbr>`; a forma expandida fica no glossário do rodapé (5.12.11), que funciona também pelo teclado. |
| 5.12.9 Uso de texto especial | Requisito | Essas marcações só são usadas para o que significam. | Atende | `<strong>` só em valores e avisos importantes; nenhum `<blockquote>`, `<em>` ou `<h*>` usado só para aparência. |
| 5.12.10 Definições de significado | Recomendação | Há como saber o significado de termos incomuns. | Atende após correção | Correções C03 e C31: glossário "Siglas e termos usados no sistema" no rodapé de todas as telas ("Crédito", "Extrato", "Ticket médio"), e o cartão do relatório passou a dizer "Ticket médio (valor médio por compra)". |
| 5.12.11 Siglas e abreviaturas | Recomendação | Há como ver a forma expandida das siglas. | Atende após correção | Correção C03: o mesmo glossário traz CPF, SENAI, QR Code, URL, Nº, MB e os formatos JPG, PNG e WebP (`<details class="glossario">` em `html/base.html`). |
| 5.12.12 Nível de linguagem | Recomendação | Texto em linguagem simples. | Atende | Frases curtas e diretas ("Pegue o que quiser, registre sua compra e pague com o saldo da sua conta."). Os termos técnicos ficam na tela de QR Codes, usada só pelo administrador. Avaliação feita por leitura dos textos; não foi medida por ferramenta. |
| 5.12.13 Pronúncia identificada | Recomendação | Palavra de sentido ambíguo sem a pronúncia tem a pronúncia indicada. | Não se aplica | Não foi encontrada palavra cujo sentido dependa da pronúncia. |

### 5.13 Codificação e Marcação Semântica

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.13.1 Título da página | Requisito | Cada tela tem `<title>` único. | Atende | 10 títulos diferentes (conferido por script): "Início \| Cantina da Honestidade", "Entrar \| …", "Criar conta \| …", "Produtos \| …", "Minha conta \| …", "Catálogo de Produtos - Administração", "Usuários - Administração", "Movimentações - Administração", "Relatórios - Administração", "QR Codes - Administração". |
| 5.13.2 Idioma da página | Requisito | O idioma está declarado. | Atende | `<html lang="pt-BR">` nas 10 telas e em `html/base.html` (conferido por script). |
| 5.13.3 Idioma das partes da página | Requisito | Trecho em outro idioma é marcado. | Não se aplica | Não há trechos em outro idioma. "QR Code", "e-mail", "ticket" e "WebP" são termos técnicos ou estrangeirismos incorporados, exceções do item. |
| 5.13.4 Título do frame | Requisito | Todo `<iframe>` tem título. | Não se aplica | Não há `<frame>` nem `<iframe>`. |
| 5.13.5 Zoom não bloqueado | Requisito | A tela não impede o zoom. | Atende | `<meta name="viewport" content="width=device-width, initial-scale=1.0">` nas 10 telas, sem `user-scalable=no` nem `maximum-scale`. |
| 5.13.6 Ordem de leitura | Requisito | A ordem do código faz sentido. | Atende | A ordem do HTML é link de pular, cabeçalho, conteúdo, rodapé; dentro do conteúdo, título, filtros, resultado. Os modais ficam depois do `<main>` e recebem o foco ao abrir. Confirmar: T2. |
| 5.13.7 Texto visível no nome acessível | Requisito | O nome lido pelo leitor de tela contém o texto que aparece. | Atende após correção | Todo `aria-label` começa pelo texto visível ("Adicionar à sacola: <produto>", "Editar <usuário>", "Cantina da Honestidade — voltar ao início"). Correção C01: no link "Minha conta" do cabeçalho, o `<span>` do saldo tinha `aria-label="Saldo disponível"`, que substituía o valor; o leitor de tela não lia o saldo que aparece na tela. Agora o link é lido como "Minha conta, saldo disponível: R$ …" (`html/base.html`). Confirmar: T2. |
| 5.13.8 Mensagens de status | Requisito | Mensagens de resultado são anunciadas sem mover o foco. | Atende após correção | Avisos em `role="status"` (`#mensagem-api`, `#status-sacola`, contadores com `aria-live="polite"`, estados "Carregando…") e erros em `role="alert"` (`.feedback-form`, `#erro-compra`). Correções C20 e C25: no painel de produtos a lista inteira tinha `aria-live` (o leitor de tela relia todos os cartões a cada tecla da busca), e o erro da exclusão ficava atrás do modal. Confirmar: T2. |
| 5.13.9 Propósito identificável | Recomendação | Dá para identificar no código a finalidade de regiões e campos. | Atende | Regiões com elemento próprio e nome (5.4), campos com `autocomplete` (5.9.8), componentes com `role` e estado (5.13.12). |
| 5.13.10 Componentes com nome acessível | Requisito | Todo componente tem nome. | Atende após correção | Botões com texto ou `aria-label`; campos com `<label>`; modais com `aria-labelledby`; grupos e regiões com nome. Correções C19 e C01: a busca do painel de produtos não tinha nome, e o saldo do cabeçalho tinha um nome que escondia o valor. Confirmar: T2. |
| 5.13.11 Elementos nativos | Requisito | Todos os componentes usam elementos nativos do HTML. | **Não atende** | Links, botões, campos, listas e tabelas são nativos, e a lista de siglas usa `<details>`. Dois componentes são feitos à mão: as janelas modais (`<div class="modal-conteudo" role="dialog">`, em vez de `<dialog>`) e as abas dos relatórios (`role="tablist"`, sem equivalente nativo). Os dois cumprem 5.13.12 e 5.13.13. Ver seção 5.1. |
| 5.13.12 Semântica de componentes customizados | Requisito | Componente feito à mão expõe função, estado e valor. | Atende | Modais: `role="dialog"`, `aria-modal="true"`, `aria-labelledby` e `aria-describedby`. Abas: `role="tablist"`, `role="tab"` com `aria-selected` e `aria-controls`, `role="tabpanel"` com `aria-labelledby` (`selecionarAba` em `javascript/relatorios_adm.js` atualiza os estados). Botões de alternância com `aria-pressed`; menu recolhível com `aria-expanded` e `aria-controls`; lista em carregamento com `aria-busy`. Confirmar: T2. |
| 5.13.13 Estados, propriedades e valores de componentes customizados | Requisito | O que a pessoa muda no componente também pode ser mudado por tecnologia assistiva. | Atende | Abas, alternâncias e botões dos modais são `<button>` nativos: o acionamento por tecnologia assistiva dispara o mesmo `click`. |

### 5.14 Áudio e Vídeo

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.14.1 Alternativa em texto para áudio | Requisito | Áudio gravado tem transcrição. | Não se aplica | O sistema não tem áudio nem vídeo (nenhum `<audio>`, `<video>` ou som feito por JavaScript). |
| 5.14.2 Legendas descritivas para vídeo | Requisito | Vídeo gravado tem legendas. | Não se aplica | Não há vídeo. |
| 5.14.3 Transcrição para vídeo | Recomendação | Vídeo gravado tem transcrição. | Não se aplica | Não há vídeo. |
| 5.14.4 Audiodescrição para vídeo | Requisito | Vídeo gravado tem audiodescrição. | Não se aplica | Não há vídeo. |
| 5.14.5 Audiodescrição estendida para vídeo | Recomendação | Há audiodescrição estendida quando as pausas não bastam. | Não se aplica | Não há vídeo. |
| 5.14.6 Janela de Libras para conteúdo em áudio | Recomendação | Áudio gravado tem janela de Libras. | Não se aplica | Não há áudio. |
| 5.14.7 Controle de áudio | Requisito | Som que toca sozinho pode ser pausado. | Não se aplica | Nenhum som é reproduzido. |
| 5.14.8 Áudio sem ruído | Recomendação | Fala sem som de fundo que atrapalhe. | Não se aplica | Não há áudio. |
| 5.14.9 Legendas para áudio e vídeo ao vivo | Requisito | Transmissão ao vivo tem legendas. | Não se aplica | Não há transmissão ao vivo. |
| 5.14.10 Transcrição para áudio ao vivo | Recomendação | Áudio ao vivo tem transcrição. | Não se aplica | Não há áudio ao vivo. |

### 5.15 Animação

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.15.1 Controle de animação | Requisito | Animação que começa sozinha e dura mais de 5 s pode ser pausada. | Não se aplica | Não há animação automática: nenhum `@keyframes` nem `animation` nos CSS; nada se move sozinho. |
| 5.15.2 Animações acionadas por interação | Recomendação | Movimento causado pela interação pode ser desligado. | Atende após correção | Os únicos movimentos são transições de até 0,2 s e o pequeno salto do cartão ao passar o mouse. Correção C07: `@media (prefers-reduced-motion: reduce)` existia em 3 dos 7 CSS e não tirava o salto; agora há uma regra global em `css/base.css` que zera as transições e o `transform` do cartão. Confirmar: T6. |
| 5.15.3 Flash intermitente | Recomendação | Nada pisca mais de 3 vezes por segundo. | Atende | Nada pisca. |
| 5.15.4 Flash intermitente limitado | Requisito | Conteúdo que pisca fica abaixo dos limites. | Não se aplica | Não há conteúdo que pisca. |

### 5.16 Tempo

| Item | Tipo | O que foi verificado | Situação | Evidência |
| --- | --- | --- | --- | --- |
| 5.16.1 Limite de tempo | Recomendação | Não há limite de tempo. | **Não atende** | Existe um limite: a sessão de login termina depois de 8 horas sem uso (`PERMANENT_SESSION_LIFETIME=timedelta(hours=8)` em `src/backend/app.py`). É decisão de projeto (seção 6). Fora isso, nenhuma tela tem contagem regressiva nem prazo para preencher. |
| 5.16.2 Limite de tempo ajustável | Requisito | Dá para desligar, ajustar ou estender o limite, ou ele passa de 20 horas. | **Não atende** | O limite de 8 horas é menor que 20 horas, não pode ser desligado nem ajustado, e não há aviso antes do fim com opção de estender. Atenuante: as 8 horas contam a partir do último uso (o Flask renova o cookie a cada resposta), e ao expirar a pessoa entra de novo e volta à mesma tela. Ver seção 5.1. |
| 5.16.3 Controle de atualização | Requisito | Conteúdo que se atualiza sozinho pode ser pausado. | Não se aplica | Nada se atualiza sozinho: não há `setInterval` nem consulta periódica; as listas só mudam por ação da pessoa. |
| 5.16.4 Interrupções | Recomendação | Não há interrupções, ou elas podem ser adiadas. | Atende | Não há pop-up, alerta ou aviso que apareça sem ação da pessoa; não há `alert()` nem `confirm()`. |
| 5.16.5 Reautenticação | Recomendação | Depois de entrar de novo, a pessoa continua sem perder dados. | **Não atende** | Parcial. Preservado: a sacola (fica no dispositivo, `localStorage`), a volta à tela de origem (`?destino=` em `Cantina.irParaLogin`) e a proteção contra compra em dobro. Perdido: o que estava digitado e ainda não gravado em um formulário aberto (cadastro de produto, edição de usuário, valor do crédito). Ver seção 5.1. |
| 5.16.6 Tempo de inatividade | Recomendação | A pessoa é avisada do limite de inatividade antes de perder dados. | Atende após correção | Correção C09: não havia aviso. As telas de login e de cadastro agora informam "o acesso termina depois de 8 horas sem uso" (`<p class="aviso-sessao">` em `html/login.html` e `html/cadastro.html`). |

---

## 3. Correções feitas nesta auditoria

Todas em `src/frontend/`. Nenhuma muda regra de negócio, `id`, `name`, classe usada pelo JavaScript ou campo da API.

| Nº | Arquivos | O que estava em desacordo | O que mudou | Itens |
| --- | --- | --- | --- | --- |
| C01 | `html/base.html` | No link "Minha conta" do cabeçalho, o saldo tinha `aria-label="Saldo disponível"`: o leitor de tela lia o rótulo no lugar do valor. | O `aria-label` saiu; entrou o texto oculto ", saldo disponível:" antes do valor. | 5.13.7, 5.13.10 |
| C02 | `html/base.html`, `css/base.css` | Quatro telas do painel só eram alcançadas pelo menu lateral. O link do rodapé não tinha sublinhado e tinha 24 px de altura. | Rodapé com `<nav aria-label="Mapa do site">` (itens conforme a sessão, com `data-visivel`), links sublinhados e com 44 px. O link "Voltar ao início" virou o item "Início" do mapa. | 5.7.13, 5.11.1, 5.8.6 |
| C03 | `html/base.html`, `css/base.css` | Siglas e termos sem explicação em nenhuma tela. | Lista "Siglas e termos usados no sistema" (`<details class="glossario">`) no rodapé de todas as telas. | 5.12.10, 5.12.11 |
| C04 | `javascript/base.js`, `css/base.css` | O menu do cabeçalho não mostrava a tela atual. | Função `marcarPaginaAtual()` põe `aria-current`; o CSS destaca com barra e negrito. | 5.7.14 |
| C05 | `css/base.css` | Contorno de foco laranja sobre o rodapé escuro: 2,56:1. O foco de `<summary>` e de elementos com `tabindex` dependia do CSS de cada tela. | Contorno branco no rodapé (12,63:1); `summary` e `[tabindex]` entraram na regra geral de foco (antes cada tela repetia a regra). | 5.11.6 |
| C06 | `css/base.css` | Nas telas do painel, itens do menu do cabeçalho com 40 px e logotipo com cerca de 33 px; o menu não quebrava linha em larguras médias. | `min-height: 44px` no logotipo e nos itens; `flex-wrap: wrap` no menu. | 5.8.6, 5.10.4 |
| C07 | `css/base.css` | `prefers-reduced-motion` só em 3 dos 7 CSS, e sem tirar o salto do cartão. | Regra global: sem transições, sem animações e sem o `transform` do cartão. | 5.15.2 |
| C08 | `index.html` | Seção das vantagens sem cabeçalho. | `<h2 id="titulo-vantagens" class="somente-leitor">`. | 5.3.4 |
| C09 | `html/login.html`, `html/cadastro.html`, `css/login_cadastro.css` | Nenhum aviso sobre o tempo de sessão. | Parágrafo `.aviso-sessao` com o limite de 8 horas sem uso. | 5.16.6 |
| C10 | `html/cadastro.html`, `html/minha_conta.html`, `html/catalogo_produtos.html`, as 5 telas do painel, `javascript/minha_conta.js`, `javascript/relatorios_adm.js` | Listas com `list-style: none` sem `role="list"` (alguns leitores de tela deixam de anunciá-las como lista). | `role="list"` nas regras da senha, em "Minhas compras", nos itens de cada compra, nos itens do modal e no menu lateral. | 5.5.1 |
| C11 | `javascript/catalogo_produtos.js`, `javascript/catalogo_produtos_adm.js` | Cartões de produto e itens da sacola eram blocos `<article>` soltos, sem relação de lista. | Contêiner com `role="list"` e cada cartão ou item com `role="listitem"`. | 5.5.1 |
| C12 | `javascript/catalogo_produtos.js` | A lista de itens do modal "Finalizar compra" rola dentro do modal, mas não recebia foco: sem mouse, não dava para conferir uma lista longa. | A lista ganha `tabindex="0"` quando há rolagem. | 5.1.12 |
| C13 | `html/catalogo_produtos.html`, `javascript/catalogo_produtos.js` | "Entrar para finalizar" era um botão que levava a outra tela. | Virou link (`<a href="/html/login.html">`); o JavaScript só acrescenta a volta ao catálogo. | 5.8.2 |
| C14 | `css/catalogo_produtos.css` | Descrição do produto cortada em 2 linhas, sem como ler o resto; entrelinha de 1,45. | Descrição inteira, com entrelinha de 1,5. | 5.12.1, 5.12.7 |
| C15 | `html/catalogo_produtos.html`, `html/catalogo_produtos_adm.html`, `css/catalogo_produtos.css` | Sobretítulos escritos em maiúsculas no HTML. | Texto normal no HTML e `text-transform: uppercase` no CSS (mesma aparência). | boa prática de leitura |
| C16 | `css/catalogo_produtos.css`, `css/minha_conta.css` | `.link-acao` com 42,5 px de altura dentro de avisos. | `min-height: 44px`. | 5.8.6 |
| C17 | `css/base.css`, `css/admin.css`, `css/catalogo_produtos.css`, `css/catalogo_produtos_adm.css`, `css/minha_conta.css` | Parágrafos com mais de 120 caracteres por linha em telas largas. | `max-width: 70ch` nos parágrafos descritivos. | 5.12.6 |
| C18 | `html/catalogo_produtos_adm.html`, `css/catalogo_produtos_adm.css` | Cabeçalhos pulavam de `<h1>` para `<h3>`; resumo e filtros sem título; cartões de resumo em `<article>`. | Três `<h2 class="somente-leitor">` (resumo, filtros, lista); resumo em `<dl>`, com o mesmo desenho. | 5.3.4, 5.3.5 |
| C19 | `html/catalogo_produtos_adm.html` | Campo de busca sem nome: o `<label>` só tinha um ícone oculto. | Texto oculto "Buscar por nome, categoria ou código" no `<label>`. | 5.9.1, 5.13.10 |
| C20 | `html/catalogo_produtos_adm.html` | `aria-live="polite"` na lista inteira de produtos; `role="alert"` junto com `aria-live="polite"`. | `aria-live` saiu da lista (o contador já anuncia o resultado); ficou só `role="alert"`. | 5.13.8 |
| C21 | `html/catalogo_produtos_adm.html` | "Novo produto" e "Cadastrar produto" para a mesma função; "＋" lido pelo leitor de tela. | Os dois botões se chamam "Cadastrar produto"; "＋" com `aria-hidden`. | 5.8.4, 5.2.3 |
| C22 | `html/catalogo_produtos_adm.html` | Partes do formulário de produto sem agrupamento de formulário; números "01–03" lidos sem sentido. | `role="group"` com `aria-labelledby` nas 6 partes (cadastro e edição); números com `aria-hidden`. | 5.9.6, 5.2.3 |
| C23 | `javascript/catalogo_produtos_adm.js` | "Editar", "Excluir" e "Reativar" iguais em todos os cartões. | `aria-label` com o nome do produto. | 5.8.3 |
| C24 | `javascript/catalogo_produtos_adm.js` | Depois de editar ou reativar, a lista era refeita e o foco se perdia. | `focarProduto()` leva o foco ao botão "Editar" do mesmo produto, ou à busca se ele saiu da lista. | 5.1.4 |
| C25 | `html/catalogo_produtos_adm.html`, `javascript/catalogo_produtos_adm.js` | O erro ao excluir aparecia na página, atrás do modal aberto. | `<p id="erro-excluir-produto" role="alert">` dentro do modal. | 5.9.9, 5.13.8 |
| C26 | `css/catalogo_produtos_adm.css`, `css/base.css` | Bordas dos campos e da busca com 1,24:1 a 1,28:1; texto de exemplo da busca na cor padrão do navegador; filtro selecionado só pela cor (1,07:1); preço em #c9631b (3,97:1). | Nova variável `--cor-contorno` (#7d8a80) nas bordas; texto de exemplo em `--cor-texto-suave`; filtro selecionado com contorno e "✓"; preço e contagem "Sem estoque" em `--cor-primaria`. | 5.11.1, 5.11.3, 5.11.4 |
| C27 | `css/base.css`, `css/admin.css`, `css/catalogo_produtos_adm.css` | Marcas "✓ " e setas criadas pelo CSS podiam ser lidas pelo leitor de tela. | `content: "✓ " / ""` (texto alternativo vazio), mantendo a declaração simples como reserva. | 5.2.3 |
| C28 | As 5 telas do painel | Link "Produtos" do menu lateral com o mesmo nome do "Produtos" do cabeçalho, com destinos diferentes. | Nome acessível "Produtos do painel" (texto oculto). | 5.7.5 |
| C29 | `html/movimentacoes_adm.html`, `html/relatorios_adm.html` | Asterisco de obrigatório sem explicação nos filtros de data. | Linha "Campos com * são obrigatórios." | 5.9.7 |
| C30 | `html/usuarios_adm.html`, `html/qrcodes_adm.html`, `html/relatorios_adm.html`, `javascript/relatorios_adm.js` | Três formulários de consulta sem botão de envio. | Botões "Buscar" e "Atualizar lista" (só consultam; nada é gravado). | 5.9.14 |
| C31 | `html/relatorios_adm.html` | "Ticket médio" sem explicação. | "Ticket médio (valor médio por compra)". | 5.12.10 |
| C32 | `css/catalogo_produtos_adm.css` | Texto de apoio do formulário com entrelinha de 1,4; o `<main>` do painel de produtos mostrava contorno ao receber o foco do link de pular (diferente das outras telas do painel). | Entrelinha de 1,5; `.secao-produtos-admin:focus { outline: none }`, igual às outras telas. | 5.12.1 |

**Mudanças que aparecem na tela** (para o grupo conferir no navegador antes da banca): rodapé com o mapa do site e a lista de siglas; aviso de 8 horas no login e no cadastro; descrição do produto inteira no catálogo; botões "Buscar" e "Atualizar lista" em três filtros do painel; botão "Cadastrar produto" no menu lateral (antes "Novo produto"); filtro selecionado do painel de produtos com "✓" e contorno; bordas mais escuras nos campos do painel de produtos; item do menu da tela atual com barra e negrito.

---

## 4. Contrastes medidos

Razão calculada pela fórmula da WCAG: `(L1 + 0,05) / (L2 + 0,05)`, em que L é a luminância relativa de cada cor (L1 é a mais clara). Para conferir um valor, use qualquer verificador de contraste (por exemplo, o WebAIM Contrast Checker) com os dois códigos de cor.

Mínimos: **4,5:1** para texto normal; **3:1** para texto grande (24 px, ou 18,66 px em negrito) e para bordas, estados e contorno de foco.

### Texto normal (mínimo 4,5:1)

| Texto | Fundo | Onde é usado | Razão |
| --- | --- | --- | ---: |
| #2b2b2b | #ffffff | Texto geral (`--cor-texto`) | 14,16 |
| #2b2b2b | #fffaf5 | Texto sobre o fundo creme | 13,65 |
| #333333 | #ffffff | Texto das telas do painel (`body`) | 12,63 |
| #2b2b2b | #fff4e0 | Texto dos avisos (`.mensagem-api`, `.aviso-conferencia`) | 12,99 |
| #2b2b2b | #fdecea | Texto digitado em campo com erro | 12,38 |
| #5f6b62 | #ffffff | Dicas, textos de apoio e texto de exemplo (`--cor-texto-suave`) | 5,58 |
| #5f6b62 | #fffaf5 | Texto de apoio sobre o creme | 5,38 |
| #5f6b62 | #fbfcfa | Texto de apoio nos filtros e listas vazias do painel | 5,42 |
| #5f6b62 | #f7f8f6 | Filtro de situação não selecionado (painel de produtos) | 5,23 |
| #5f6b62 | #ffebd4 | Frase da abertura, no ponto mais escuro do degradê | 4,80 |
| #637067 | #edf3e9 | Parágrafo do topo do catálogo, no ponto mais escuro do degradê | 4,60 |
| #b8520b | #ffffff | Links, botão secundário, preço (`--cor-primaria`) | 4,94 |
| #ffffff | #b8520b | Texto do botão principal | 4,94 |
| #b8520b | #fffaf5 | Laranja sobre o creme | 4,76 |
| #b8520b | #fbfcfa | Contagem "Sem estoque" no painel | 4,80 |
| #ffffff | #96420a | Botão principal com o mouse em cima | 6,82 |
| #96420a | #ffffff | Links de ação (`.link-acao`) | 6,82 |
| #96420a | #fff4e0 | Link e etiqueta dentro de aviso | 6,26 |
| #96420a | #edf7ee | Link dentro de mensagem de sucesso | 6,21 |
| #2e7d32 | #edf7ee | Mensagem de sucesso, etiqueta "Ativo", saldo no cabeçalho | 4,67 |
| #2e7d32 | #ffffff | Valores positivos, regra de senha cumprida | 5,13 |
| #b3261e | #ffffff | Mensagem de erro do campo, asterisco, valores negativos | 6,54 |
| #b3261e | #fdecea | Mensagem de erro em caixa, etiqueta "Inativo" | 5,72 |
| #a13d32 | #fdecea | Mensagem de erro no catálogo | 5,69 |
| #31573a | #fff4e0 | Aviso do catálogo ("adicionado à sua sacola") | 7,54 |
| #ffffff | #333333 | Rodapé | 12,63 |
| #dddddd | #333333 | Direitos autorais e lista de siglas | 9,30 |
| #ffffff | #2b2b2b | Link "Pular para o conteúdo" | 14,16 |
| #526057 | #fffefa | Menu do cabeçalho (telas do cliente) | 6,57 |
| #3d6545 | #f6f8f3 | Item "Administração" do cabeçalho | 6,24 |
| #446e4c | #fff1d9 | Sobretítulos verdes de 11 px, no pior ponto do degradê | 5,26 |
| #ffffff | #446e4c | Filtro de categoria selecionado | 5,87 |
| #5f6c62 | #ffffff | Filtro de categoria não selecionado | 5,51 |
| #59715d | #f3f6f0 | Etiqueta de categoria (11 px) | 4,88 |
| #a45220 | #fff3e7 | "Últimas unidades" (11 px) | 5,05 |
| #3d7449 | #f0f8ef | Selos "Zero lactose" e "Zero açúcar" (11 px) | 5,11 |
| #4d6a52 | #ffffff | "N unidades disponíveis" | 6,00 |
| #75625d | #ffffff | "Indisponível no momento" | 5,74 |
| #8f3f2c | #ffffff | "Remover" e "Limpar sacola" | 7,20 |
| #536157 | #ffffff | Linhas de total e de saldo | 6,53 |
| #55584c | #f7f5ed | Aviso "Ao finalizar, a compra é registrada…" | 6,67 |
| #7a4a00 | #fff4e0 | Etiqueta "Ajuste" | 6,86 |
| #6a756c | #ffffff | Texto de apoio do painel de produtos | 4,80 |
| #6b776e | #ffffff | Texto do modal do painel de produtos | 4,68 |
| #6b756d | #ffffff | Texto de exemplo dos formulários do painel | 4,78 |
| #657168 | #ffffff | Detalhes do cartão de produto (painel) | 5,10 |
| #28743a | #e8f5e9 | Selos no painel | 5,12 |
| #a94b12 | #fff1e3 | "Sem estoque" no cartão do painel (11 px) | 5,12 |
| #8a3b12 | #fff0e4 | "Inativo" no cartão do painel | 6,94 |
| #a94b32 | #ffffff | Botão "Inativar" | 5,62 |
| #555555 | #fff4e0 | Aviso padrão do painel de produtos | 6,84 |
| #666666 | #fbfcfa | Dica de campo no painel de produtos | 5,58 |
| #3a4a3f | #ffffff | Itens do menu lateral | 9,41 |
| #2d5637 | #edf4e9 | Item atual do menu lateral, etiqueta "Administrador" | 7,49 |
| #2d5637 | #ffffff | Filtro ligado na lista de produtos (Ativos, Inativos, Sem estoque) | 8,41 |
| #445248 | #f7f8f6 | Abas dos relatórios | 7,74 |
| #39483d | #fbfcfa | Rótulos dos campos do painel | 9,41 |

### Texto grande (mínimo 3:1)

| Texto | Fundo | Onde é usado | Razão |
| --- | --- | --- | ---: |
| #b8520b | #ffebd4 | "Honestidade" no título do início (38 px ou mais), no pior ponto do degradê | 4,26 |
| #b8520b | #edf3e9 | Segunda linha do título do catálogo (32 px ou mais), no pior ponto | 4,38 |
| #2e7d32 | #f0f7ee | Saldo em destaque em "Minha conta" (32 px ou mais) | 4,70 |
| #293a30 | #ffebd4 | Título do início | 10,38 |

### Bordas, estados e foco (mínimo 3:1)

| Cor | Fundo | Onde é usado | Razão |
| --- | --- | --- | ---: |
| #7f8a82 | #ffffff | Borda dos campos (login, cadastro, minha conta, catálogo) | 3,58 |
| #7d8a80 | #ffffff | Borda dos campos e botões do painel (`--cor-contorno`) | 3,61 |
| #7d8a80 | #fbfcfa | Mesma borda sobre o fundo dos filtros e do formulário de produto | 3,51 |
| #b3261e | #ffffff | Borda do campo com erro | 6,54 |
| #3d6545 | #f7f8f6 | Borda da aba aberta e contorno do filtro selecionado | 6,27 |
| #446e4c | #ffffff | Filtro de categoria selecionado em relação ao não selecionado | 5,87 |
| #3d6545 | #e3e9e2 | Barra do relatório em relação ao trilho | 5,41 |
| #b8520b | #ffffff | Contorno de foco sobre branco | 4,94 |
| #b8520b | #fffaf5 | Contorno de foco sobre o creme | 4,76 |
| #b8520b | #f7f8f6 | Contorno de foco sobre o fundo do painel | 4,64 |
| #b8520b | #fdecea | Contorno de foco sobre campo com erro | 4,32 |
| #ffffff | #333333 | Contorno de foco no rodapé | 12,63 |

### Antes e depois das correções

| Onde | Antes | Depois | Mínimo |
| --- | --- | --- | ---: |
| Texto de exemplo da busca do painel de produtos | cinza padrão do navegador (no Chrome, cerca de #a9a9a9: 2,35) | #5f6b62: 5,58 | 4,5 |
| Preço no cartão do painel de produtos | #c9631b: 3,97 (só passava por ser texto grande) | #b8520b: 4,94 | 3 |
| Contagem "Sem estoque" no resumo do painel | #bf681f sobre #fbfcfa: 3,91 (texto grande) | #b8520b: 4,80 | 3 |
| Borda dos campos do formulário de produto | #dfe5de sobre #fbfcfa: 1,24 | #7d8a80: 3,51 | 3 |
| Borda da busca do painel de produtos | #e0e6df sobre #ffffff: 1,27 | #7d8a80: 3,61 | 3 |
| Filtro de situação selecionado (painel de produtos) | fundo #ffffff sobre #f7f8f6: 1,07, sem outra marca | contorno #3d6545: 6,27, mais a marca "✓" | 3 |
| Contorno de foco no rodapé | #b8520b sobre #333333: 2,56 | #ffffff: 12,63 | 3 |

**Fora da exigência, mas registrado:** a borda do botão "Sair" (#d9ded8, 1,36:1) e a do botão "Inativar" (#e8c8b7, 1,57:1) são claras; esses botões são identificados pelo texto, que tem contraste. Botões desabilitados ficam com 60% de opacidade (o texto branco sobre o laranja cai para cerca de 2,5:1); controles desabilitados ficam de fora dos itens 5.11.3 e 5.11.4.

---

## 5. Pendências e limites

### 5.1 Itens que não atendem

| Item | Tipo | O que falta | Caminho para resolver |
| --- | --- | --- | --- |
| 5.16.2 Limite de tempo ajustável | Requisito | A sessão dura 8 horas sem uso; a norma pede mais de 20 horas, ou um aviso antes do fim com opção de estender. | Opção A (uma linha, no servidor): `PERMANENT_SESSION_LIFETIME=timedelta(hours=24)` em `src/backend/app.py`, e trocar "8 horas" por "24 horas" no aviso de `html/login.html` e `html/cadastro.html`. Opção B: manter 8 horas e criar um aviso alguns minutos antes do fim, com um botão "Continuar conectado". Hoje fica como decisão de projeto (seção 6). |
| 5.13.11 Elementos nativos | Requisito | As janelas modais são `<div role="dialog">` e as abas dos relatórios são `<button role="tab">`. | Trocar os modais por `<dialog>` com `showModal()` (o navegador passa a cuidar do foco e do Esc). Para as abas não existe elemento nativo; elas seguem o padrão da WAI-ARIA e cumprem 5.13.12 e 5.13.13. |
| 5.16.1 Limite de tempo | Recomendação | Existe limite de sessão. | Só deixaria de existir sem expiração de sessão, o que não é recomendável por segurança. |
| 5.16.5 Reautenticação | Recomendação | Ao expirar a sessão com um formulário aberto, o que foi digitado e não gravado se perde. | Guardar o rascunho do formulário (por exemplo, em `sessionStorage`) antes de ir para o login e devolver depois. |
| 5.11.2 Contraste aprimorado (7:1) | Recomendação | O laranja da identidade (4,94:1) e os textos de apoio (5,58:1) não chegam a 7:1. | Escurecer as cores (por exemplo, usar `--cor-primaria-escura`, 6,82:1, ainda abaixo de 7:1) mudaria a identidade visual. O mínimo exigido (5.11.3) é atendido. |
| 5.12.5 Alinhamento de blocos de texto | Recomendação | Títulos e textos curtos centralizados (login, cadastro, rodapé, listas vazias, cartaz). | Alinhar à esquerda esses blocos. Não há texto justificado, e o texto corrido já é alinhado à esquerda. |

### 5.2 O que a leitura do código não garante

- **Leitor de tela.** O código tem os papéis, nomes e regiões de aviso, mas só o teste mostra o que é de fato falado. Atenção especial: avisos que nascem ocultos e aparecem já com texto (`#aviso-pagina`, `.mensagem-api:empty`), que alguns leitores de tela podem não anunciar.
- **Enter em `<select>` dentro dos modais.** O bloqueio de Enter (`Cantina.bloquearEnvioPorEnter`) cancela a tecla em campos e em `<select>`. Confirmar que ainda dá para escolher uma opção com as setas e Enter no campo "Perfil" do modal "Editar usuário".
- **Foco em botão ocupado.** Enquanto envia, o botão fica desabilitado (`Cantina.comBotaoOcupado`). Confirmar que, depois de um erro, o foco continua em um lugar útil.
- **Texto alternativo no CSS.** `content: "✓ " / ""` é ignorado por navegadores antigos, que ficam com a declaração simples (a marca pode ser lida como "marca de seleção").
- **Zoom, 320 px e espaçamento de texto.** O CSS não tem alturas fixas com corte, mas quebra de linha e sobreposição só se veem na tela.
- **Ferramentas automáticas.** Não foram usadas (axe DevTools, WAVE, Lighthouse, validador de HTML do W3C). Vale rodar ao menos uma em cada tela.
- **Impressão.** As regras `@media print` de `css/admin.css` (relatórios, movimentações, cartaz e etiquetas) não foram conferidas no papel.
- **Sessão.** A renovação a cada uso foi lida no código do Flask instalado (versão 3.1.3, `SESSION_REFRESH_EACH_REQUEST` ligado por padrão), não medida.

### 5.3 Roteiro de testes manuais

Complementa os testes L01 a L08 de `docs/testes-manuais.md`. Marcar e anotar navegador, versão e data. Resultado e responsável: **[A PREENCHER pelo grupo]**.

- [ ] **T1 — Só teclado (todas as telas).** Sem mouse: o primeiro Tab mostra "Pular para o conteúdo" e Enter leva ao conteúdo; o Tab segue a ordem da tela; o foco está sempre visível, inclusive no rodapé (contorno branco); nenhum elemento com foco fica escondido. Nos modais (finalizar compra, cadastrar e editar produto, excluir produto, editar usuário, inativar, ajustar saldo, redefinir senha): o foco entra no modal, o Tab não sai dele, Esc fecha e o foco volta ao botão de origem. Nos relatórios: setas, Home e End trocam de aba. Em cada formulário que grava: Enter dentro de um campo **não** grava; Tab até o botão e Enter ou Espaço gravam. No modal "Editar usuário": escolher o perfil com as setas e Enter. No painel de produtos: depois de editar, o foco volta ao "Editar" do mesmo cartão.
- [ ] **T2 — NVDA no computador (Firefox ou Chrome).** Em cada tela: lista de títulos (Insert+F7) sem saltos de nível; regiões (tecla D); todo campo é lido com rótulo, "obrigatório" e dica; ao errar, a mensagem do campo é lida; no cabeçalho, ouve-se "Minha conta, saldo disponível: R$ …". Catálogo: lista de produtos anunciada como lista; "Adicionar à sacola: <produto>"; aviso lido ao adicionar; modal lido com título; aviso de saldo insuficiente; "Compra registrada!". Aviso de boas-vindas depois do cadastro (`#aviso-pagina`) é lido? Tabelas (Ctrl+Alt+setas): cabeçalhos de coluna e de linha lidos. Relatórios: "aba, selecionada, 1 de 5". Painel de produtos: "Editar: <produto>"; a busca não relê todos os cartões.
- [ ] **T3 — TalkBack ou VoiceOver no celular.** Abrir o catálogo pelo QR Code de um produto: o aviso "foi para a sua sacola" é lido e o foco vai para "Minha sacola". Finalizar uma compra só com gestos do leitor de tela.
- [ ] **T4 — Zoom e tela estreita.** Em 1280 px de largura, zoom de 200% e de 400% (equivale a 320 px): sem rolagem horizontal da página (as tabelas rolam dentro da própria área), nenhum texto cortado ou sobreposto, menus e modais utilizáveis. Repetir no celular em retrato e em paisagem. No Firefox, testar também "Ampliar apenas o texto" a 200%.
- [ ] **T5 — Espaçamento de texto.** Com um bookmarklet de espaçamento de texto (entrelinha 1,5; parágrafo 2; letras 0,12; palavras 0,16), percorrer catálogo, minha conta e painel: nenhum texto cortado, sobreposto ou fora da caixa.
- [ ] **T6 — Menos movimento.** Com "reduzir movimento" ligado no sistema operacional: os cartões não se movem ao passar o mouse e não há transições.
- [ ] **T7 — Uso de cor.** Em tons de cinza (DevTools, "Emular deficiência de visão: acromatopsia"): dá para distinguir o filtro selecionado, a aba aberta, a página atual do menu, entradas e saídas do extrato e campos com erro.
- [ ] **T8 — Ferramenta automática.** Rodar axe DevTools ou WAVE nas 10 telas (com modal aberto também) e anotar o que aparecer.
- [ ] **T9 — Impressão.** Imprimir (ou gerar PDF de) um relatório, as movimentações, o cartaz e as etiquetas: texto preto legível, sem menu nem filtros, tabelas inteiras.
- [ ] **T10 — Sessão.** No DevTools, em Application, Cookies, `cantina_sessao`: a data de expiração avança a cada ação (8 horas à frente). Apagar o cookie com itens na sacola e clicar em "Finalizar compra": a tela pede login, a sacola continua, e depois de entrar a pessoa volta ao catálogo.

---

## 6. Decisões de projeto relacionadas

- **Enter não grava.** Nos formulários que gravam dados (cadastro, crédito, troca de senha, produto, edição de usuário, ajuste de saldo, redefinição de senha), a tecla Enter dentro de um campo não envia: só o botão grava (`Cantina.bloquearEnvioPorEnter` em `javascript/base.js`). É regra do sistema (RN15 do Documento do Sistema), pedida pela professora. Não fere a norma: o botão de gravar é um `<button type="submit">` nativo, alcançado pelo Tab e acionado por Enter ou Espaço quando está com o foco, e os modais avisam em texto ("O produto só é gravado ao clicar em Salvar produto"). Nas consultas (login, filtros, buscas), em que nada é gravado, Enter funciona normalmente.
- **Sessão de 8 horas.** O login vale 8 horas contadas do último uso (`PERMANENT_SESSION_LIFETIME` em `src/backend/app.py`; o Flask renova o cookie a cada resposta). O prazo é uma medida de segurança (justificativa a confirmar pelo grupo: **[A PREENCHER pelo grupo]**). Não há contagem regressiva nem conteúdo que se mova sozinho. Ao expirar, a pessoa é levada ao login, volta à tela em que estava, e a sacola continua salva no dispositivo. As telas de login e de cadastro avisam do prazo. Por ser menor que 20 horas e não ter aviso com opção de estender, o item 5.16.2 fica como pendência (seção 5.1).
- **Emojis decorativos.** Os emojis e símbolos (🤝, 🥪, 💰, 🛍️, ♡, ⚠, ←) só ilustram um texto que já está escrito ao lado. Todos têm `aria-hidden="true"`, para o leitor de tela não ler "sanduíche" ou "sacolas de compras" no meio da frase. Nenhuma informação depende deles.
- **Laranja da identidade.** O laranja original (#e87522, 3,0:1 sobre branco) já tinha sido trocado por #b8520b (4,94:1), que cumpre o mínimo. Chegar a 7:1 (5.11.2) exigiria mudar a identidade visual, que foi mantida nesta auditoria.
- **Modais e abas feitos com WAI-ARIA.** Foram construídos com `role="dialog"` e `role="tablist"` antes desta auditoria. Trocar por `<dialog>` é a pendência do item 5.13.11; enquanto isso, eles cumprem os itens de componentes customizados (5.1.15, 5.13.12 e 5.13.13).
- **Listas que se atualizam ao digitar.** As buscas do painel filtram enquanto a pessoa digita. Isso está avisado junto ao campo, só muda o conteúdo da própria tela e, depois desta auditoria, cada busca também tem um botão de envio.
