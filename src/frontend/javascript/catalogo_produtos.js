// Catálogo da cantina: mostra os produtos disponíveis, mantém a sacola neste
// dispositivo e registra a compra, que debita o saldo do usuário logado.
document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    // Com 3 unidades ou menos o catálogo mostra o aviso "Últimas unidades".
    const ULTIMAS_UNIDADES = 3;
    // Limites do contrato da API de compras.
    const MAXIMO_POR_PRODUTO = 99;
    const MAXIMO_DE_PRODUTOS = 50;
    const URL_PRODUTOS = "/api/produtos?status=ATIVO";
    const CHAVE_SACOLA = "cantina-sacola-v1";
    const CHAVE_COMPRA_PENDENTE = "cantina-compra-pendente-v1";
    const elemento = Cantina.criarElemento;
    const formatarPreco = Cantina.formatarPreco;

    // Catálogo e sacola
    const lista = document.getElementById("lista-produtos");
    const busca = document.getElementById("busca-produtos");
    const categorias = document.getElementById("categorias-produtos");
    const contadorProdutos = document.getElementById("contador-produtos");
    const mensagemApi = document.getElementById("mensagem-api");
    const avisoPagina = document.getElementById("aviso-pagina");
    const avisoQr = document.getElementById("aviso-qr");
    const tituloProdutos = document.getElementById("titulo-produtos");
    const carrinho = document.getElementById("carrinho");
    const tituloCarrinho = document.getElementById("titulo-carrinho");
    const itensCarrinho = document.getElementById("itens-carrinho");
    const resumoCarrinho = document.getElementById("resumo-carrinho");
    const totalCarrinho = document.getElementById("total-carrinho");
    const contadorSacola = document.getElementById("contador-sacola");
    const rotuloContadorSacola = document.getElementById("rotulo-contador-sacola");
    const statusSacola = document.getElementById("status-sacola");
    const linhaSaldoSacola = document.getElementById("linha-saldo-sacola");
    const saldoSacola = document.getElementById("saldo-sacola");

    // Modal "Finalizar compra"
    const modal = document.getElementById("modal-compra");
    const dialogo = document.getElementById("dialogo-compra");
    const etapaRevisao = document.getElementById("etapa-revisao");
    const etapaSucesso = document.getElementById("etapa-sucesso");
    const itensCompra = document.getElementById("itens-compra");
    const totalCompra = document.getElementById("total-compra");
    const linhaSaldoDisponivel = document.getElementById("linha-saldo-disponivel");
    const saldoDisponivel = document.getElementById("saldo-disponivel");
    const linhaSaldoApos = document.getElementById("linha-saldo-apos");
    const rotuloSaldoApos = document.getElementById("rotulo-saldo-apos");
    const saldoApos = document.getElementById("saldo-apos");
    const avisoLogin = document.getElementById("aviso-login-compra");
    const avisoSaldo = document.getElementById("aviso-saldo-compra");
    const textoAvisoSaldo = document.getElementById("texto-aviso-saldo");
    const avisoLimite = document.getElementById("aviso-limite-compra");
    const erroCompra = document.getElementById("erro-compra");
    const botaoConfirmar = document.getElementById("confirmar-compra");
    const botaoEntrar = document.getElementById("entrar-para-finalizar");
    const botaoFechar = document.getElementById("fechar-compra");
    const botaoFinalizar = document.getElementById("finalizar-compra");
    const tituloSucesso = document.getElementById("titulo-sucesso");

    let todosProdutos = [];
    let catalogoCarregado = false;
    let categoriaAtual = "TODAS";
    let sacola = lerSacola();
    let usuario = null;             // usuário logado ou null
    let saldoCentavos = null;       // último saldo conhecido (null = não se sabe)
    let consultandoSaldo = false;
    let enviando = false;
    let compraPendente = lerCompraPendente();   // {chave, assinatura} da tentativa de compra em aberto
    // Página aberta pelo QR Code de um produto (?adicionar=<id>): guarda o valor pedido até o
    // catálogo carregar. null = não há pedido (ou ele já foi atendido).
    let pedidoDoQrCode = new URLSearchParams(window.location.search).get("adicionar");

    // ---------- sacola guardada no dispositivo ----------

    function lerSacola() {
        try {
            const valor = JSON.parse(localStorage.getItem(CHAVE_SACOLA) || "{}");
            if (!valor || typeof valor !== "object" || Array.isArray(valor)) return {};
            return Object.fromEntries(Object.entries(valor).filter(([, quantidade]) => Number.isInteger(quantidade) && quantidade > 0));
        } catch {
            return {};
        }
    }

    function salvarSacola() {
        try {
            localStorage.setItem(CHAVE_SACOLA, JSON.stringify(sacola));
        } catch {
            mostrarAviso("Não foi possível salvar a sacola neste navegador.", "erro");
        }
    }

    // ---------- chave de idempotência da compra ----------
    // A mesma chave é reenviada enquanto a sacola (e o usuário) forem os mesmos: se a
    // resposta se perder por falha de rede, tentar de novo não registra a compra em dobro.
    // Uma chave nova só nasce depois de uma compra concluída ou quando a sacola muda.
    // Ela fica no sessionStorage para valer também se a página for recarregada.

    function lerCompraPendente() {
        try {
            const valor = JSON.parse(sessionStorage.getItem(CHAVE_COMPRA_PENDENTE) || "null");
            return valor && typeof valor.chave === "string" && typeof valor.assinatura === "string" ? valor : null;
        } catch {
            return null;
        }
    }

    function assinaturaDaCompra() {
        const itens = Object.keys(sacola)
            .sort((a, b) => Number(a) - Number(b))
            .map((id) => `${id}x${sacola[id]}`)
            .join(",");
        return `${usuario ? usuario.id_usuario : ""}|${itens}`;
    }

    function garantirChave() {
        const assinatura = assinaturaDaCompra();
        if (!compraPendente || compraPendente.assinatura !== assinatura) {
            compraPendente = { chave: Cantina.novaChave(), assinatura };
            try {
                sessionStorage.setItem(CHAVE_COMPRA_PENDENTE, JSON.stringify(compraPendente));
            } catch {
                // Sem armazenamento, a chave vale só enquanto a página estiver aberta.
            }
        }
        return compraPendente.chave;
    }

    function descartarChave() {
        compraPendente = null;
        try {
            sessionStorage.removeItem(CHAVE_COMPRA_PENDENTE);
        } catch {
            // Nada a fazer: a chave já saiu da memória.
        }
    }

    // ---------- apoio ----------

    function mostrarAviso(texto, tipo = "") {
        Cantina.mostrarMensagem(mensagemApi, texto, tipo);
    }

    function normalizar(texto) {
        return String(texto || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLocaleLowerCase("pt-BR");
    }

    function produtosDisponiveis() {
        return todosProdutos.filter((produto) => produto.status === "ATIVO");
    }

    function produtoPorId(id) {
        return todosProdutos.find((produto) => String(produto.id_produto) === String(id));
    }

    // Quanto de um produto cabe na sacola: o estoque, até o máximo aceito por compra.
    function limiteDoProduto(produto) {
        return Math.min(produto.quantidade_estoque, MAXIMO_POR_PRODUTO);
    }

    function itensDaSacola() {
        return Object.entries(sacola)
            .map(([id, quantidade]) => ({ produto: produtoPorId(id), quantidade }))
            .filter((item) => item.produto);
    }

    function totalDaSacola() {
        return itensDaSacola().reduce((soma, { produto, quantidade }) => soma + produto.preco_venda_centavos * quantidade, 0);
    }

    function quantidadeNaSacola() {
        return Object.values(sacola).reduce((soma, quantidade) => soma + quantidade, 0);
    }

    function plural(quantidade, singular, variasUnidades) {
        return `${quantidade} ${quantidade === 1 ? singular : variasUnidades}`;
    }

    // A API devolve "assets/produtos/arquivo.png"; o servidor entrega em "/assets/produtos/...".
    function caminhoFoto(caminho) {
        return caminho ? "/" + String(caminho).replace(/^\/+/, "") : null;
    }

    // ---------- produtos ----------

    function criarImagem(produto) {
        const wrapper = elemento("div", "imagem-produto");
        const emojiPorCategoria = { bebidas: "🥤", lanches: "🥪", salgados: "🥟", doces: "🍪", frutas: "🍎" };
        const fallback = elemento("span", "imagem-fallback", emojiPorCategoria[normalizar(produto.categoria)] || "🥡");
        fallback.setAttribute("aria-hidden", "true");
        wrapper.append(fallback);
        const src = caminhoFoto(produto.foto_caminho);
        if (src) {
            const imagem = elemento("img");
            imagem.src = src;
            imagem.alt = `Foto de ${produto.nome}`;
            imagem.loading = "lazy";
            imagem.addEventListener("load", () => wrapper.classList.add("com-foto"), { once: true });
            imagem.addEventListener("error", () => imagem.remove(), { once: true });
            wrapper.prepend(imagem);
        }
        return wrapper;
    }

    function configurarBotaoAdicionar(botao, produto) {
        const esgotado = produto.quantidade_estoque <= 0;
        const noLimite = !esgotado && (sacola[produto.id_produto] || 0) >= limiteDoProduto(produto);
        const texto = esgotado ? "Esgotado" : "Adicionar à sacola";
        botao.textContent = texto;
        botao.setAttribute("aria-label", `${texto}: ${produto.nome}`);
        botao.disabled = esgotado;
        // No limite o botão continua focável (aria-disabled): o foco do teclado não se perde
        // e o clique explica por que não dá para adicionar mais.
        if (noLimite) botao.setAttribute("aria-disabled", "true");
        else botao.removeAttribute("aria-disabled");
    }

    function criarCard(produto) {
        // Cada cartão é um item da lista de produtos (o contêiner recebe role="list").
        const card = elemento("div", "card-produto");
        card.setAttribute("role", "listitem");
        card.dataset.produtoId = produto.id_produto;
        card.append(criarImagem(produto));
        const conteudo = elemento("div", "conteudo-produto");
        const topo = elemento("div", "topo-card-produto");
        topo.append(elemento("span", "categoria-produto", produto.categoria));
        if (produto.quantidade_estoque > 0 && produto.quantidade_estoque <= ULTIMAS_UNIDADES) {
            topo.append(elemento("span", "estoque-produto poucas-unidades", "Últimas unidades"));
        }
        conteudo.append(topo);
        conteudo.append(elemento("h3", "nome-produto", produto.nome));
        conteudo.append(elemento("p", "preco-produto", formatarPreco(produto.preco_venda_centavos)));
        if (produto.descricao) conteudo.append(elemento("p", "descricao-produto", produto.descricao));
        const selos = elemento("div", "selos-produto");
       // if (produto.zero_lactose) selos.append(elemento("span", "selo", "Zero lactose"));
        //if (produto.zero_acucar) selos.append(elemento("span", "selo", "Zero açúcar"));
        if (selos.childElementCount) conteudo.append(selos);

        const rodape = elemento("div", "rodape-card-produto");
        const estoque = produto.quantidade_estoque > 0
            ? (produto.quantidade_estoque === 1 ? "1 unidade disponível" : `${produto.quantidade_estoque} unidades disponíveis`)
            : "Indisponível no momento";
        rodape.append(elemento("span", produto.quantidade_estoque > 0 ? "disponibilidade" : "disponibilidade esgotado", estoque));
        const botao = elemento("button", "botao botao-principal botao-adicionar");
        botao.type = "button";
        botao.dataset.acao = "adicionar";
        configurarBotaoAdicionar(botao, produto);
        rodape.append(botao);
        conteudo.append(rodape);
        card.append(conteudo);
        return card;
    }

    // Atualiza só os botões "Adicionar" (sem redesenhar a lista, para manter o foco do teclado).
    function atualizarBotoesAdicionar() {
        lista.querySelectorAll("[data-produto-id]").forEach((card) => {
            const produto = produtoPorId(card.dataset.produtoId);
            const botao = card.querySelector("button[data-acao='adicionar']");
            if (produto && botao) configurarBotaoAdicionar(botao, produto);
        });
    }

    function renderizarCategorias() {
        categorias.replaceChildren();
        const botaoTodas = elemento("button", "filtro-categoria selecionado", "Todas");
        botaoTodas.type = "button";
        botaoTodas.dataset.categoria = "TODAS";
        botaoTodas.setAttribute("aria-pressed", "true");
        categorias.append(botaoTodas);
        const valores = [...new Set(produtosDisponiveis().map((p) => p.categoria).filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt-BR"));
        valores.forEach((categoria) => {
            const botao = elemento("button", "filtro-categoria", categoria);
            botao.type = "button";
            botao.dataset.categoria = categoria;
            botao.setAttribute("aria-pressed", "false");
            categorias.append(botao);
        });
        const aindaExiste = categoriaAtual === "TODAS" || valores.includes(categoriaAtual);
        if (!aindaExiste) categoriaAtual = "TODAS";
        atualizarEstadoCategorias();
    }

    function atualizarEstadoCategorias() {
        categorias.querySelectorAll("[data-categoria]").forEach((botao) => {
            const selecionado = botao.dataset.categoria === categoriaAtual;
            botao.classList.toggle("selecionado", selecionado);
            botao.setAttribute("aria-pressed", String(selecionado));
        });
    }

    function renderizarProdutos() {
        const termo = normalizar(busca.value.trim());
        const produtos = produtosDisponiveis().filter((produto) => {
            const correspondeCategoria = categoriaAtual === "TODAS" || produto.categoria === categoriaAtual;
            const correspondeBusca = !termo || normalizar(`${produto.nome} ${produto.categoria}`).includes(termo);
            return correspondeCategoria && correspondeBusca;
        });
        lista.replaceChildren();
        contadorProdutos.textContent = plural(produtos.length, "produto", "produtos");
        lista.setAttribute("aria-busy", "false");
        // Com produtos na tela, o contêiner é anunciado como lista ("lista com N itens").
        if (produtos.length) lista.setAttribute("role", "list");
        else lista.removeAttribute("role");
        if (!produtos.length) {
            const vazio = elemento("div", "estado-vazio-catalogo");
            const icone = elemento("span", "icone-vazio", termo ? "⌕" : "🍊");
            icone.setAttribute("aria-hidden", "true");
            vazio.append(icone);
            vazio.append(elemento("strong", "", todosProdutos.length ? "Não encontramos esse produto" : "Nenhum produto disponível agora"));
            vazio.append(elemento("p", "", termo ? "Tente buscar por outro nome ou categoria." : "Volte em breve para conferir as novidades da cantina."));
            lista.append(vazio);
            return;
        }
        produtos.forEach((produto) => lista.append(criarCard(produto)));
    }

    // ---------- sacola ----------

    // Tira da sacola o que saiu do catálogo ou esgotou e limita as quantidades ao estoque.
    // Devolve true se algo precisou ser ajustado.
    function ajustarSacolaAoEstoque() {
        if (!catalogoCarregado) return false;
        let mudou = false;
        Object.keys(sacola).forEach((id) => {
            const produto = produtoPorId(id);
            const limite = produto && produto.status === "ATIVO" ? limiteDoProduto(produto) : 0;
            if (limite <= 0) {
                delete sacola[id];
                mudou = true;
            } else if (sacola[id] > limite) {
                sacola[id] = limite;
                mudou = true;
            }
        });
        return mudou;
    }

    function criarBotaoDaSacola(classe, texto, acao, produto, rotulo) {
        const botao = elemento("button", classe, texto);
        botao.type = "button";
        botao.dataset.acao = acao;
        botao.dataset.id = produto.id_produto;
        botao.setAttribute("aria-label", rotulo);
        return botao;
    }

    function criarLinhaDaSacola(produto, quantidade) {
        // Cada produto é um item da lista da sacola (o contêiner recebe role="list").
        const linha = elemento("div", "item-carrinho");
        linha.setAttribute("role", "listitem");
        const info = elemento("div", "informacoes-item");
        info.append(elemento("h3", "", produto.nome));
        info.append(elemento("p", "", `${formatarPreco(produto.preco_venda_centavos)} cada`));
        const subtotal = elemento("strong", "subtotal-item", formatarPreco(produto.preco_venda_centavos * quantidade));

        const controles = elemento("div", "controles-quantidade");
        const menos = criarBotaoDaSacola("botao-quantidade", "−", "diminuir", produto, `Diminuir quantidade de ${produto.nome}`);
        menos.disabled = quantidade <= 1;
        const valor = elemento("span", "quantidade-item");
        valor.append(elemento("span", "somente-leitor", "Quantidade: "), String(quantidade));
        const mais = criarBotaoDaSacola("botao-quantidade", "+", "aumentar", produto, `Aumentar quantidade de ${produto.nome}`);
        mais.disabled = quantidade >= limiteDoProduto(produto);
        const remover = criarBotaoDaSacola("remover-item", "Remover", "remover", produto, `Remover ${produto.nome} da sacola`);
        controles.append(menos, valor, mais, remover);

        linha.append(info, subtotal, controles);
        return linha;
    }

    function mostrarSaldoNaSacola() {
        const conhecido = Boolean(usuario) && Number.isInteger(saldoCentavos);
        linhaSaldoSacola.hidden = !conhecido;
        saldoSacola.textContent = conhecido ? formatarPreco(saldoCentavos) : "";
    }

    // Redesenha a sacola. Devolve true se ela precisou ser ajustada ao estoque.
    function renderizarSacola() {
        const mudou = ajustarSacolaAoEstoque();
        itensCarrinho.replaceChildren();
        itensDaSacola().forEach(({ produto, quantidade }) => itensCarrinho.append(criarLinhaDaSacola(produto, quantidade)));

        // Com itens, a sacola é anunciada como lista; vazia, mostra só o aviso.
        if (itensCarrinho.childElementCount) {
            itensCarrinho.setAttribute("role", "list");
            itensCarrinho.setAttribute("aria-label", "Produtos na sacola");
        } else {
            itensCarrinho.removeAttribute("role");
            itensCarrinho.removeAttribute("aria-label");
        }

        const quantidadeTotal = quantidadeNaSacola();
        contadorSacola.textContent = quantidadeTotal;
        rotuloContadorSacola.textContent = quantidadeTotal === 1 ? "item na sacola" : "itens na sacola";
        totalCarrinho.textContent = formatarPreco(totalDaSacola());
        resumoCarrinho.hidden = quantidadeTotal === 0;
        if (quantidadeTotal === 0) {
            // Sacola vazia (compra concluída ou itens retirados): o aviso do QR Code
            // "foi para a sua sacola" deixa de valer.
            avisoQr.replaceChildren();
            const vazio = elemento("div", "sacola-vazia");
            const icone = elemento("span", "", "🛍️");
            icone.setAttribute("aria-hidden", "true");
            vazio.append(icone);
            vazio.append(elemento("strong", "", "Sua sacola está vazia"));
            vazio.append(elemento("p", "", "Adicione algo gostoso para começar."));
            const link = elemento("a", "", "Explorar produtos");
            link.href = "#produtos";
            vazio.append(link);
            itensCarrinho.append(vazio);
        }
        if (catalogoCarregado) salvarSacola();
        return mudou;
    }

    // Depois de redesenhar a sacola, devolve o foco a um controle do mesmo item
    // (ou ao que sobrou), para quem navega pelo teclado não se perder.
    function focarNaSacola(acao, id) {
        const doItem = [acao, "aumentar", "diminuir", "remover"]
            .map((nome) => itensCarrinho.querySelector(`button[data-acao="${nome}"][data-id="${CSS.escape(String(id))}"]`))
            .find((botao) => botao && !botao.disabled);
        const destino = doItem || itensCarrinho.querySelector("button:not([disabled]), a[href]") || tituloCarrinho;
        destino.focus();
    }

    // Resumo falado para leitores de tela (a região #status-sacola é aria-live).
    function anunciarSacola(prefixo = "") {
        const quantidade = quantidadeNaSacola();
        const resumo = quantidade
            ? `Sacola com ${plural(quantidade, "item", "itens")}, total de ${formatarPreco(totalDaSacola())}.`
            : "Sua sacola está vazia.";
        statusSacola.textContent = `${prefixo} ${resumo}`.trim();
    }

    // Explica por que não cabe mais uma unidade do produto na sacola ("" quando ainda cabe).
    function motivoDoLimite(produto) {
        const naSacola = sacola[produto.id_produto] || 0;
        if (naSacola < limiteDoProduto(produto)) return "";
        return naSacola >= MAXIMO_POR_PRODUTO
            ? `Cada compra aceita até ${MAXIMO_POR_PRODUTO} unidades de ${produto.nome}.`
            : `Você já colocou na sacola todas as unidades disponíveis de ${produto.nome}.`;
    }

    // Coloca 1 unidade na sacola. Quem chama confere antes o estoque e o limite (motivoDoLimite).
    // A chave de idempotência não precisa de cuidado aqui: como a sacola mudou, a assinatura
    // muda e garantirChave() cria outra chave na próxima tentativa de compra.
    function adicionarUnidade(produto) {
        sacola[produto.id_produto] = (sacola[produto.id_produto] || 0) + 1;
        renderizarSacola();
        atualizarBotoesAdicionar();
    }

    // ---------- modal "Finalizar compra" ----------

    function definirSaldo(centavos) {
        saldoCentavos = centavos;
        if (usuario) usuario.saldo_centavos = centavos;
        Cantina.atualizarSaldoCabecalho(centavos);
        mostrarSaldoNaSacola();
    }

    function mostrarEtapa(etapa) {
        const sucesso = etapa === "sucesso";
        etapaRevisao.hidden = sucesso;
        etapaSucesso.hidden = !sucesso;
        dialogo.setAttribute("aria-labelledby", sucesso ? "titulo-sucesso" : "titulo-compra");
    }

    // Monta a conferência: itens, total, saldo e o que o usuário pode fazer agora.
    function renderizarRevisao() {
        const itens = itensDaSacola();
        const total = totalDaSacola();
        const vazia = itens.length === 0;
        const logado = Boolean(usuario);
        const saldoConhecido = logado && Number.isInteger(saldoCentavos);
        const insuficiente = saldoConhecido && !consultandoSaldo && saldoCentavos < total;
        const muitosProdutos = itens.length > MAXIMO_DE_PRODUTOS;

        itensCompra.replaceChildren();
        if (vazia) itensCompra.append(elemento("li", "linha-revisao", "Sua sacola está vazia."));
        itens.forEach(({ produto, quantidade }) => {
            const linha = elemento("li", "linha-revisao");
            linha.append(elemento("span", "", `${quantidade} × ${produto.nome}`));
            linha.append(elemento("strong", "", formatarPreco(produto.preco_venda_centavos * quantidade)));
            itensCompra.append(linha);
        });
        totalCompra.textContent = formatarPreco(total);

        linhaSaldoDisponivel.hidden = !logado || vazia;
        if (consultandoSaldo) saldoDisponivel.textContent = "Consultando...";
        else saldoDisponivel.textContent = saldoConhecido ? formatarPreco(saldoCentavos) : "Não foi possível consultar";

        linhaSaldoApos.hidden = !saldoConhecido || consultandoSaldo || vazia;
        rotuloSaldoApos.textContent = insuficiente ? "Falta para esta compra" : "Saldo após a compra";
        saldoApos.textContent = formatarPreco(Math.abs((saldoCentavos || 0) - total));

        avisoLogin.hidden = logado || consultandoSaldo || vazia;
        avisoSaldo.hidden = !insuficiente || vazia;
        textoAvisoSaldo.textContent = insuficiente
            ? `Faltam ${formatarPreco(total - saldoCentavos)} para esta compra. Adicione crédito e volte para finalizar: sua sacola continua salva.`
            : "";
        avisoLimite.hidden = !muitosProdutos;

        botaoEntrar.hidden = logado || consultandoSaldo || vazia;
        botaoConfirmar.hidden = !logado || vazia;
        botaoConfirmar.disabled = consultandoSaldo || insuficiente || muitosProdutos;
        if (insuficiente) botaoConfirmar.setAttribute("aria-describedby", "aviso-saldo-compra");
        else botaoConfirmar.removeAttribute("aria-describedby");

        // Lista longa rola dentro do modal: só então ela entra na ordem do Tab, para
        // quem usa o teclado conseguir rolar e conferir todos os itens.
        if (itensCompra.scrollHeight > itensCompra.clientHeight + 1) itensCompra.tabIndex = 0;
        else itensCompra.removeAttribute("tabindex");
    }

    // Busca o saldo atual no servidor (ele pode ter mudado em outra aba ou aparelho).
    async function consultarSaldo() {
        consultandoSaldo = true;
        renderizarRevisao();
        try {
            usuario = await Cantina.sessao();
            if (usuario) {
                const resultado = await Cantina.requisitar("/api/carteira");
                if (resultado.carteira && Number.isInteger(resultado.carteira.saldo_centavos)) {
                    definirSaldo(resultado.carteira.saldo_centavos);
                }
            }
        } catch (erro) {
            if (erro.status === 401) {
                // A sessão acabou: a tela volta ao estado "sem login".
                usuario = null;
                saldoCentavos = null;
                mostrarSaldoNaSacola();
                Cantina.atualizarSessao();
            }
            // Outras falhas: segue com o último saldo conhecido; o servidor confere de novo na compra.
        } finally {
            consultandoSaldo = false;
            if (usuario) garantirChave();
            renderizarRevisao();
        }
    }

    function abrirCompra() {
        if (!quantidadeNaSacola()) return;
        mostrarEtapa("revisao");
        Cantina.mostrarMensagem(erroCompra, "", "erro");
        modal.classList.add("aberto");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-aberto");
        botaoFechar.focus();
        // Desenha a conferência e atualiza o saldo; a chave de idempotência nasce aqui.
        consultarSaldo();
    }

    function fecharCompra() {
        // Enquanto a compra está sendo enviada o modal não fecha (evita mexer na sacola no meio do envio).
        if (enviando) return;
        modal.classList.remove("aberto");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-aberto");
        // Devolve o foco ao botão que abriu o modal; se ele sumiu (sacola vazia), vai para o título dos produtos.
        const botaoVisivel = botaoFinalizar.getClientRects().length > 0;
        (botaoVisivel ? botaoFinalizar : tituloProdutos).focus();
    }

    function itensParaApi() {
        return itensDaSacola().map(({ produto, quantidade }) => ({ id_produto: produto.id_produto, quantidade }));
    }

    async function confirmarCompra() {
        if (enviando || botaoConfirmar.disabled) return;
        enviando = true;
        Cantina.mostrarMensagem(erroCompra, "", "erro");
        let resultado = null;
        let falha = null;
        try {
            resultado = await Cantina.comBotaoOcupado(botaoConfirmar, "Registrando compra...", () =>
                Cantina.requisitar("/api/compras", {
                    method: "POST",
                    json: { itens: itensParaApi(), chave_idempotencia: garantirChave() },
                }));
        } catch (erro) {
            falha = erro;
        }
        // "enviando" só termina depois de tratar a resposta: até lá, novos cliques são ignorados.
        try {
            if (falha) await tratarErroDaCompra(falha);
            else concluirCompra(resultado);
        } finally {
            enviando = false;
        }
    }

    function concluirCompra(resultado) {
        const compra = resultado.compra || {};
        const carteira = resultado.carteira || {};

        // Compra registrada: a sacola esvazia e a próxima compra usa outra chave.
        sacola = {};
        descartarChave();
        if (Number.isInteger(carteira.saldo_centavos)) definirSaldo(carteira.saldo_centavos);

        document.getElementById("numero-compra").textContent = compra.id_compra ? `nº ${compra.id_compra}` : "—";
        document.getElementById("total-pago").textContent = formatarPreco(compra.valor_total_centavos);
        document.getElementById("novo-saldo").textContent = Number.isInteger(saldoCentavos) ? formatarPreco(saldoCentavos) : "—";
        mostrarEtapa("sucesso");
        tituloSucesso.focus();

        renderizarSacola();
        mostrarAviso("");
        // O estoque mudou: busca os produtos de novo.
        carregarCatalogo({ silencioso: true });
    }

    function nomeDoProduto(item) {
        return item.nome || produtoPorId(item.id_produto)?.nome || `produto nº ${item.id_produto}`;
    }

    function descreverFaltaDeEstoque(item) {
        const nome = nomeDoProduto(item);
        const disponivel = Math.max(0, Number(item.disponivel) || 0);
        if (disponivel === 0) return `${nome} (esgotado)`;
        const unidades = disponivel === 1 ? "só 1 unidade disponível" : `só ${disponivel} unidades disponíveis`;
        return item.solicitado ? `${nome} (${unidades}; você pediu ${item.solicitado})` : `${nome} (${unidades})`;
    }

    // Leva ao login e, na volta, o catálogo lembra que a sacola está esperando
    // (ela continua salva neste dispositivo).
    function entrarParaFinalizar() {
        window.history.replaceState(null, "", window.location.pathname + "?aviso=continuar-compra");
        Cantina.irParaLogin();
    }

    async function tratarErroDaCompra(erro) {
        // Sessão expirada: vai para o login.
        if (erro.status === 401) {
            entrarParaFinalizar();
            return;
        }

        const detalhes = erro.detalhes || {};
        const produtos = Array.isArray(detalhes.produtos) ? detalhes.produtos : [];
        let mensagem = erro.message;

        if (erro.codigo === "SALDO_INSUFICIENTE") {
            if (Number.isInteger(detalhes.saldo_centavos)) definirSaldo(detalhes.saldo_centavos);
            const total = Number.isInteger(detalhes.total_centavos) ? detalhes.total_centavos : totalDaSacola();
            mensagem = Number.isInteger(saldoCentavos)
                ? `A compra não foi registrada: seu saldo é de ${formatarPreco(saldoCentavos)} e o total é de ${formatarPreco(total)}.`
                : "A compra não foi registrada: o saldo não é suficiente.";
        } else if (erro.codigo === "ESTOQUE_INSUFICIENTE") {
            const faltas = produtos.map(descreverFaltaDeEstoque);
            // Aplica o estoque informado pelo servidor e busca o catálogo de novo.
            produtos.forEach((item) => {
                const local = produtoPorId(item.id_produto);
                if (local) local.quantidade_estoque = Math.max(0, Number(item.disponivel) || 0);
            });
            renderizarSacola();
            renderizarProdutos();
            await carregarCatalogo({ silencioso: true });
            mensagem = faltas.length
                ? `A compra não foi registrada porque faltou estoque: ${faltas.join("; ")}.`
                : "A compra não foi registrada porque faltou estoque de algum produto.";
            mensagem += quantidadeNaSacola()
                ? " Ajustamos sua sacola ao que está disponível: confira e confirme de novo."
                : " Sua sacola ficou vazia.";
        } else if (erro.codigo === "PRODUTO_INDISPONIVEL") {
            const nomes = produtos.map((item) => item.nome || produtoPorId(item.id_produto)?.nome).filter(Boolean);
            produtos.forEach((item) => { delete sacola[item.id_produto]; });
            renderizarSacola();
            await carregarCatalogo({ silencioso: true });
            mensagem = nomes.length
                ? `A compra não foi registrada: ${nomes.join(", ")} não ${nomes.length === 1 ? "está mais disponível e saiu" : "estão mais disponíveis e saíram"} da sua sacola.`
                : "A compra não foi registrada: um produto da sacola não está mais disponível e foi retirado.";
            mensagem += quantidadeNaSacola() ? " Confira e confirme de novo." : " Sua sacola ficou vazia.";
        } else if (erro.status === 422) {
            mensagem = [erro.message, ...Object.values(erro.campos || {})].join(" ");
        } else if (erro.status === 0) {
            mensagem = `${erro.message} Sua sacola continua salva. Pode confirmar de novo: a compra não será registrada em dobro.`;
        }

        renderizarRevisao();
        Cantina.mostrarMensagem(erroCompra, mensagem, "erro");
        erroCompra.focus();
    }

    // ---------- avisos vindos de outras telas ----------

    // Tira um parâmetro do endereço sem recarregar a página; os outros parâmetros e a âncora ficam.
    function removerParametroDoEndereco(nome) {
        const parametros = new URLSearchParams(window.location.search);
        if (!parametros.has(nome)) return;
        parametros.delete(nome);
        const consulta = parametros.toString();
        window.history.replaceState(null, "", window.location.pathname + (consulta ? `?${consulta}` : "") + window.location.hash);
    }

    async function mostrarAvisoDaUrl() {
        const aviso = new URLSearchParams(window.location.search).get("aviso");
        if (!aviso) return;

        // Tira o aviso do endereço: ele não reaparece ao atualizar a página.
        removerParametroDoEndereco("aviso");

        const avisos = {
            "bem-vindo": {
                texto: "Cadastro concluído! Adicione créditos em Minha conta para começar a comprar.",
                tipo: "sucesso",
                link: { texto: "Adicionar crédito", href: "/html/minha_conta.html#creditos" },
            },
            "sem-permissao": {
                texto: "Aquela área é exclusiva da administração.",
                tipo: "erro",
            },
            // Volta do login pedido no modal "Finalizar compra".
            "continuar-compra": {
                texto: "Você entrou na sua conta. Sua sacola continua aqui: é só finalizar a compra.",
                tipo: "sucesso",
                link: { texto: "Ir para a sacola", href: "#carrinho" },
                somenteLogado: true,
            },
        };
        if (!Object.prototype.hasOwnProperty.call(avisos, aviso)) return;
        const escolhido = avisos[aviso];
        if (escolhido.somenteLogado && !(await Cantina.sessao())) return;

        Cantina.mostrarMensagem(avisoPagina, escolhido.texto, escolhido.tipo);
        if (escolhido.link) {
            const link = elemento("a", "link-acao", escolhido.link.texto);
            link.href = escolhido.link.href;
            avisoPagina.append(" ", link);
        }
        avisoPagina.hidden = false;
    }

    // ---------- QR Code do produto (?adicionar=<id>) ----------
    // O QR Code de um produto abre o catálogo com "?adicionar=<id>". Depois que os produtos
    // carregam, a tela coloca 1 unidade na sacola, avisa e tira o parâmetro do endereço:
    // recarregar a página não adiciona de novo.

    // O aviso entra em #aviso-qr, que é uma região role="status" (lida pelos leitores de tela).
    function mostrarAvisoDoQrCode(texto, tipo, comLinkParaSacola) {
        const caixa = elemento("p", "mensagem-api aviso-pagina");
        Cantina.mostrarMensagem(caixa, texto, tipo);
        if (comLinkParaSacola) {
            const link = elemento("a", "link-acao", "Ir para a sacola");
            link.href = "#carrinho";
            caixa.append(" ", link);
        }
        avisoQr.replaceChildren(caixa);
    }

    // Leva a tela até a sacola e põe o foco do teclado no título dela.
    // No computador o aviso e a sacola cabem juntos na tela: a rolagem para no aviso e os dois
    // aparecem. No celular a sacola fica depois da lista de produtos: a rolagem vai direto a ela.
    function rolarAteASacola() {
        const altura = carrinho.getBoundingClientRect().bottom - avisoQr.getBoundingClientRect().top;
        const cabemJuntos = altura <= document.documentElement.clientHeight - 32;
        (cabemJuntos ? avisoQr : carrinho).scrollIntoView();
        tituloCarrinho.focus({ preventScroll: true });
    }

    // Chamada a cada carga do catálogo; só age uma vez, na primeira carga que der certo.
    async function atenderPedidoDoQrCode() {
        if (pedidoDoQrCode === null) return;
        const pedido = pedidoDoQrCode;
        pedidoDoQrCode = null;
        removerParametroDoEndereco("adicionar");

        // Só vale código formado por dígitos; o produto precisa estar ativo e ter estoque.
        const produto = /^\d+$/.test(pedido) ? produtoPorId(Number(pedido)) : null;
        const disponivel = Boolean(produto) && produto.status === "ATIVO" && produto.quantidade_estoque > 0;

        // Respeita o estoque e o máximo por compra, como o botão "Adicionar à sacola".
        const limite = disponivel ? motivoDoLimite(produto) : "";
        if (disponivel && !limite) adicionarUnidade(produto);

        // O cabeçalho entra na página depois e muda a altura dela: espera por ele antes de
        // avisar e rolar a tela.
        await Cantina.pronta();

        if (!disponivel) {
            mostrarAvisoDoQrCode("Este produto não está disponível agora.", "erro", false);
            avisoQr.scrollIntoView({ block: "center" });
            return;
        }
        if (limite) mostrarAvisoDoQrCode(limite, "", true);
        else mostrarAvisoDoQrCode(`${produto.nome} foi para a sua sacola. Confira e finalize a compra.`, "sucesso", true);
        rolarAteASacola();
    }

    // ---------- eventos ----------

    lista.addEventListener("click", (evento) => {
        const botao = evento.target.closest("button[data-acao='adicionar']");
        if (!botao) return;
        const produto = produtoPorId(botao.closest("[data-produto-id]").dataset.produtoId);
        if (!produto || produto.quantidade_estoque <= 0) return;
        const limite = motivoDoLimite(produto);
        if (limite) {
            mostrarAviso(limite);
            return;
        }
        adicionarUnidade(produto);
        mostrarAviso(`${produto.nome} adicionado à sua sacola (${plural(sacola[produto.id_produto], "unidade", "unidades")}).`);
    });

    categorias.addEventListener("click", (evento) => {
        const botao = evento.target.closest("[data-categoria]");
        if (!botao) return;
        categoriaAtual = botao.dataset.categoria;
        atualizarEstadoCategorias();
        renderizarProdutos();
    });

    busca.addEventListener("input", renderizarProdutos);

    itensCarrinho.addEventListener("click", (evento) => {
        const botao = evento.target.closest("button[data-acao]");
        if (!botao) return;
        const { acao, id } = botao.dataset;
        const produto = produtoPorId(id);
        if (acao === "remover") delete sacola[id];
        if (acao === "diminuir" && sacola[id] > 1) sacola[id] -= 1;
        if (acao === "aumentar" && produto && sacola[id] < limiteDoProduto(produto)) sacola[id] += 1;
        renderizarSacola();
        atualizarBotoesAdicionar();
        focarNaSacola(acao, id);
        anunciarSacola(acao === "remover" && produto ? `${produto.nome} saiu da sacola.` : "");
    });

    document.getElementById("limpar-sacola").addEventListener("click", () => {
        sacola = {};
        renderizarSacola();
        atualizarBotoesAdicionar();
        tituloCarrinho.focus();
        anunciarSacola();
    });

    botaoFinalizar.addEventListener("click", abrirCompra);
    botaoFechar.addEventListener("click", fecharCompra);
    document.getElementById("voltar-catalogo").addEventListener("click", fecharCompra);
    document.getElementById("continuar-catalogo").addEventListener("click", fecharCompra);
    botaoConfirmar.addEventListener("click", confirmarCompra);
    // "Entrar para finalizar" é um link para o login; o clique só acrescenta a volta para o catálogo.
    botaoEntrar.addEventListener("click", (evento) => {
        evento.preventDefault();
        entrarParaFinalizar();
    });
    modal.addEventListener("click", (evento) => { if (evento.target === modal) fecharCompra(); });

    // Modal: Esc fecha e o Tab fica preso dentro dele.
    document.addEventListener("keydown", (evento) => {
        if (!modal.classList.contains("aberto")) return;
        if (evento.key === "Escape") {
            evento.preventDefault();
            fecharCompra();
            return;
        }
        if (evento.key !== "Tab") return;

        const focaveis = [...modal.querySelectorAll(
            "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])",
        )].filter((item) => item.getClientRects().length > 0);
        if (!focaveis.length) {
            evento.preventDefault();
            dialogo.focus();
            return;
        }

        const primeiro = focaveis[0];
        const ultimo = focaveis[focaveis.length - 1];
        const foraDoModal = !modal.contains(document.activeElement);
        if (evento.shiftKey && (document.activeElement === primeiro || foraDoModal)) {
            evento.preventDefault();
            ultimo.focus();
        } else if (!evento.shiftKey && (document.activeElement === ultimo || foraDoModal)) {
            evento.preventDefault();
            primeiro.focus();
        }
    });

    // ---------- carga inicial ----------

    async function carregarCatalogo({ silencioso = false } = {}) {
        lista.setAttribute("aria-busy", "true");
        try {
            const resultado = await Cantina.requisitar(URL_PRODUTOS);
            todosProdutos = Array.isArray(resultado) ? resultado : (resultado.produtos || []);
            catalogoCarregado = true;
            renderizarCategorias();
            renderizarProdutos();
            const sacolaMudou = renderizarSacola();
            if (!silencioso) {
                mostrarAviso(sacolaMudou ? "Atualizamos sua sacola: alguns produtos esgotaram ou saíram do catálogo." : "");
            }
            // Com os produtos na tela, atende o QR Code do produto (se a página foi aberta por ele).
            atenderPedidoDoQrCode();
        } catch (erro) {
            lista.setAttribute("aria-busy", "false");
            // Numa recarga silenciosa, a lista que já está na tela continua valendo.
            if (silencioso && catalogoCarregado) return;
            lista.replaceChildren();
            lista.removeAttribute("role");
            const erroBox = elemento("div", "estado-vazio-catalogo erro-catalogo");
            erroBox.append(elemento("strong", "", "Não foi possível abrir o catálogo"));
            erroBox.append(elemento("p", "", erro.message || "Tente novamente em instantes."));
            const tentar = elemento("button", "botao botao-secundario", "Tentar novamente");
            tentar.type = "button";
            tentar.addEventListener("click", () => {
                // O botão some ao recarregar: o foco vai para o título da seção.
                tituloProdutos.focus();
                carregarCatalogo();
            });
            erroBox.append(tentar);
            lista.append(erroBox);
            contadorProdutos.textContent = "";
            mostrarAviso("O catálogo não conseguiu falar com o servidor. Tente novamente em instantes.", "erro");
        }
    }

    // Sessão: guarda o usuário e o saldo para a sacola e para o modal.
    Cantina.pronta().then((logado) => {
        usuario = logado;
        saldoCentavos = logado && Number.isInteger(logado.saldo_centavos) ? logado.saldo_centavos : null;
        mostrarSaldoNaSacola();
    });

    mostrarAvisoDaUrl();
    carregarCatalogo();
});
