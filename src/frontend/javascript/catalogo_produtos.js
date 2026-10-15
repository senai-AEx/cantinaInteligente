// Catálogo público: consulta o estoque disponível e mantém a sacola neste dispositivo.
document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:5000/api/produtos?status=ATIVO";
    const STORAGE_KEY = "cantina-sacola-v1";
    const lista = document.getElementById("lista-produtos");
    const busca = document.getElementById("busca-produtos");
    const categorias = document.getElementById("categorias-produtos");
    const contadorProdutos = document.getElementById("contador-produtos");
    const mensagemApi = document.getElementById("mensagem-api");
    const itensCarrinho = document.getElementById("itens-carrinho");
    const resumoCarrinho = document.getElementById("resumo-carrinho");
    const totalCarrinho = document.getElementById("total-carrinho");
    const contadorSacola = document.getElementById("contador-sacola");
    const modalRevisao = document.getElementById("modal-revisao");
    const resumoRevisao = document.getElementById("resumo-revisao");
    const totalRevisao = document.getElementById("total-revisao");
    let todosProdutos = [];
    let categoriaAtual = "TODAS";
    let sacola = lerSacola();
    let focoAnterior = null;

    function lerSacola() {
        try {
            const valor = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
            if (!valor || typeof valor !== "object" || Array.isArray(valor)) return {};
            return Object.fromEntries(Object.entries(valor).filter(([, quantidade]) => Number.isInteger(quantidade) && quantidade > 0));
        } catch {
            return {};
        }
    }

    function salvarSacola() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(sacola));
        } catch {
            mensagemApi.textContent = "Não foi possível salvar a sacola neste navegador.";
            mensagemApi.classList.add("mensagem-erro");
        }
    }

    async function requisitar() {
        const resposta = await fetch(API_URL, { headers: { Accept: "application/json" } });
        const resultado = await resposta.json().catch(() => ({}));
        if (!resposta.ok) throw new Error(resultado.erro || "Não foi possível carregar o catálogo.");
        return resultado;
    }

    function elemento(tag, classe, texto) {
        const node = document.createElement(tag);
        if (classe) node.className = classe;
        if (texto !== undefined) node.textContent = texto;
        return node;
    }

    function formatarPreco(centavos) {
        return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    }

    function normalizar(texto) {
        return String(texto || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
    }

    function hojeISO() {
        const hoje = new Date();
        return `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, "0")}-${String(hoje.getDate()).padStart(2, "0")}`;
    }

    function formatarData(data) {
        if (!data) return "";
        const [ano, mes, dia] = data.split("-");
        return `${dia}/${mes}/${ano}`;
    }

    function produtosDisponiveis() {
        return todosProdutos.filter((produto) => produto.status === "ATIVO" && (!produto.validade || produto.validade >= hojeISO()));
    }

    function produtoPorId(id) {
        return todosProdutos.find((produto) => String(produto.id_produto) === String(id));
    }

    function caminhoFoto(caminho) {
        if (!caminho) return null;
        try {
            const url = new URL("../" + caminho.replace(/^\/+/, ""), document.baseURI);
            return url.origin === window.location.origin ? url.href : null;
        } catch {
            return null;
        }
    }

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
            imagem.alt = produto.nome;
            imagem.loading = "lazy";
            imagem.addEventListener("load", () => wrapper.classList.add("com-foto"), { once: true });
            imagem.addEventListener("error", () => imagem.remove(), { once: true });
            wrapper.prepend(imagem);
        }
        return wrapper;
    }

    function criarCard(produto) {
        const card = elemento("article", "card-produto");
        card.dataset.produtoId = produto.id_produto;
        card.append(criarImagem(produto));
        const conteudo = elemento("div", "conteudo-produto");
        const topo = elemento("div", "topo-card-produto");
        topo.append(elemento("span", "categoria-produto", produto.categoria));
        if (produto.quantidade_estoque > 0 && produto.quantidade_estoque <= produto.estoque_minimo) {
            topo.append(elemento("span", "estoque-produto poucas-unidades", "Últimas unidades"));
        }
        conteudo.append(topo);
        conteudo.append(elemento("h3", "nome-produto", produto.nome));
        conteudo.append(elemento("p", "preco-produto", formatarPreco(produto.preco_centavos)));
        if (produto.descricao) conteudo.append(elemento("p", "descricao-produto", produto.descricao));
        if (produto.validade) conteudo.append(elemento("p", "validade-produto", `Validade ${formatarData(produto.validade)}`));
        const selos = elemento("div", "selos-produto");
        if (produto.zero_lactose) selos.append(elemento("span", "selo", "Zero lactose"));
        if (produto.zero_acucar) selos.append(elemento("span", "selo", "Zero açúcar"));
        if (selos.childElementCount) conteudo.append(selos);

        const rodape = elemento("div", "rodape-card-produto");
        const estoque = produto.quantidade_estoque > 0
            ? (produto.quantidade_estoque === 1 ? "1 unidade disponível" : `${produto.quantidade_estoque} unidades disponíveis`)
            : "Indisponível no momento";
        rodape.append(elemento("span", produto.quantidade_estoque > 0 ? "disponibilidade" : "disponibilidade esgotado", estoque));
        const botao = elemento("button", "botao botao-principal botao-adicionar", produto.quantidade_estoque > 0 ? "Adicionar à sacola" : "Esgotado");
        botao.type = "button";
        botao.dataset.acao = "adicionar";
        botao.setAttribute("aria-label", `${produto.quantidade_estoque > 0 ? "Adicionar" : "Indisponível"}: ${produto.nome}`);
        botao.disabled = produto.quantidade_estoque <= 0 || (sacola[produto.id_produto] || 0) >= produto.quantidade_estoque;
        rodape.append(botao);
        conteudo.append(rodape);
        card.append(conteudo);
        return card;
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
            const correspondeBusca = !termo || normalizar(`${produto.nome} ${produto.categoria} ${produto.codigo_produto}`).includes(termo);
            return correspondeCategoria && correspondeBusca;
        });
        lista.replaceChildren();
        contadorProdutos.textContent = `${produtos.length} ${produtos.length === 1 ? "produto" : "produtos"}`;
        lista.setAttribute("aria-busy", "false");
        if (!produtos.length) {
            const vazio = elemento("div", "estado-vazio-catalogo");
            vazio.append(elemento("span", "icone-vazio", termo ? "⌕" : "🍊"));
            vazio.append(elemento("strong", "", todosProdutos.length ? "Não encontramos esse produto" : "Nenhum produto disponível agora"));
            vazio.append(elemento("p", "", termo ? "Tente buscar por outro nome ou categoria." : "Volte em breve para conferir as novidades da cantina."));
            lista.append(vazio);
            return;
        }
        produtos.forEach((produto) => lista.append(criarCard(produto)));
    }

    function atualizarBadge() {
        const quantidade = Object.values(sacola).reduce((soma, item) => soma + item, 0);
        const badge = document.getElementById("cart-count");
        if (badge) {
            badge.textContent = quantidade;
            badge.hidden = quantidade === 0;
            badge.setAttribute("aria-label", `${quantidade} ${quantidade === 1 ? "item" : "itens"}`);
        }
    }

    function renderizarSacola() {
        itensCarrinho.replaceChildren();
        const linhas = Object.entries(sacola)
            .map(([id, quantidade]) => ({ produto: produtoPorId(id), quantidade }))
            .filter((item) => item.produto && item.produto.status === "ATIVO" && item.produto.quantidade_estoque > 0 && (!item.produto.validade || item.produto.validade >= hojeISO()));
        const idsValidos = new Set(linhas.map(({ produto }) => String(produto.id_produto)));
        const sacolaLimpa = Object.fromEntries(Object.entries(sacola).filter(([id]) => idsValidos.has(String(id))));
        if (Object.keys(sacolaLimpa).length !== Object.keys(sacola).length) sacola = sacolaLimpa;
        linhas.forEach(({ produto, quantidade }) => {
            const qtd = Math.min(quantidade, produto.quantidade_estoque);
            sacola[produto.id_produto] = qtd;
            const linha = elemento("article", "item-carrinho");
            const info = elemento("div", "informacoes-item");
            info.append(elemento("h3", "", produto.nome));
            info.append(elemento("p", "", `${formatarPreco(produto.preco_centavos)} cada`));
            const subtotal = elemento("strong", "subtotal-item", formatarPreco(produto.preco_centavos * qtd));
            const controles = elemento("div", "controles-quantidade");
            const menos = elemento("button", "botao-quantidade", "−");
            menos.type = "button"; menos.dataset.acao = "diminuir"; menos.dataset.id = produto.id_produto;
            menos.disabled = qtd <= 1; menos.setAttribute("aria-label", `Diminuir ${produto.nome}`);
            const valor = elemento("span", "quantidade-item", String(qtd));
            const mais = elemento("button", "botao-quantidade", "+");
            mais.type = "button"; mais.dataset.acao = "aumentar"; mais.dataset.id = produto.id_produto;
            mais.disabled = qtd >= produto.quantidade_estoque; mais.setAttribute("aria-label", `Aumentar ${produto.nome}`);
            const remover = elemento("button", "remover-item", "Remover");
            remover.type = "button"; remover.dataset.acao = "remover"; remover.dataset.id = produto.id_produto;
            controles.append(menos, valor, mais, remover);
            linha.append(info, subtotal, controles);
            itensCarrinho.append(linha);
        });
        const quantidadeTotal = Object.values(sacola).reduce((soma, item) => soma + item, 0);
        const totalCentavos = linhas.reduce((soma, { produto, quantidade }) => soma + produto.preco_centavos * Math.min(quantidade, produto.quantidade_estoque), 0);
        contadorSacola.textContent = quantidadeTotal;
        contadorSacola.setAttribute("aria-label", `${quantidadeTotal} ${quantidadeTotal === 1 ? "item" : "itens"}`);
        totalCarrinho.textContent = formatarPreco(totalCentavos);
        resumoCarrinho.hidden = quantidadeTotal === 0;
        if (quantidadeTotal === 0) {
            const vazio = elemento("div", "sacola-vazia");
            vazio.append(elemento("span", "", "🛍️"));
            vazio.append(elemento("strong", "", "Sua sacola está vazia"));
            vazio.append(elemento("p", "", "Adicione algo gostoso para começar."));
            const link = elemento("a", "", "Explorar produtos"); link.href = "#produtos"; vazio.append(link);
            itensCarrinho.append(vazio);
        }
        salvarSacola();
        atualizarBadge();
    }

    function abrirRevisao() {
        if (!Object.keys(sacola).length) return;
        resumoRevisao.replaceChildren();
        Object.entries(sacola).forEach(([id, quantidade]) => {
            const produto = produtoPorId(id);
            if (!produto) return;
            const linha = elemento("div", "linha-revisao");
            linha.append(elemento("span", "", `${quantidade} × ${produto.nome}`));
            linha.append(elemento("strong", "", formatarPreco(produto.preco_centavos * quantidade)));
            resumoRevisao.append(linha);
        });
        totalRevisao.textContent = totalCarrinho.textContent;
        focoAnterior = document.activeElement;
        modalRevisao.classList.add("aberto");
        modalRevisao.setAttribute("aria-hidden", "false");
        document.getElementById("fechar-revisao").focus();
    }

    function fecharRevisao() {
        modalRevisao.classList.remove("aberto");
        modalRevisao.setAttribute("aria-hidden", "true");
        if (focoAnterior && focoAnterior.isConnected) focoAnterior.focus();
    }

    lista.addEventListener("click", (evento) => {
        const botao = evento.target.closest("button[data-acao='adicionar']");
        if (!botao) return;
        const id = botao.closest("[data-produto-id]").dataset.produtoId;
        const produto = produtoPorId(id);
        if (!produto || produto.quantidade_estoque <= 0) return;
        sacola[id] = Math.min((sacola[id] || 0) + 1, produto.quantidade_estoque);
        renderizarSacola();
        renderizarProdutos();
        mensagemApi.textContent = `${produto.nome} adicionado à sua sacola.`;
        mensagemApi.classList.remove("mensagem-erro");
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
        const id = botao.dataset.id;
        const produto = produtoPorId(id);
        if (botao.dataset.acao === "remover") delete sacola[id];
        if (botao.dataset.acao === "diminuir" && sacola[id] > 1) sacola[id] -= 1;
        if (botao.dataset.acao === "aumentar" && produto && sacola[id] < produto.quantidade_estoque) sacola[id] += 1;
        renderizarSacola();
        renderizarProdutos();
    });
    document.getElementById("limpar-sacola").addEventListener("click", () => {
        sacola = {};
        renderizarSacola();
        renderizarProdutos();
    });
    document.getElementById("revisar-sacola").addEventListener("click", abrirRevisao);
    document.getElementById("fechar-revisao").addEventListener("click", fecharRevisao);
    document.getElementById("voltar-catalogo").addEventListener("click", fecharRevisao);
    modalRevisao.addEventListener("click", (evento) => { if (evento.target === modalRevisao) fecharRevisao(); });
    document.addEventListener("keydown", (evento) => {
        if (!modalRevisao.classList.contains("aberto")) return;
        if (evento.key === "Escape") {
            evento.preventDefault();
            fecharRevisao();
            return;
        }
        if (evento.key !== "Tab") return;

        const focaveis = [...modalRevisao.querySelectorAll(
            "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])",
        )].filter((elemento) => elemento.getClientRects().length > 0);
        if (!focaveis.length) {
            evento.preventDefault();
            modalRevisao.focus();
            return;
        }

        const primeiro = focaveis[0];
        const ultimo = focaveis[focaveis.length - 1];
        if (evento.shiftKey && (document.activeElement === primeiro || !modalRevisao.contains(document.activeElement))) {
            evento.preventDefault();
            ultimo.focus();
        } else if (!evento.shiftKey && (document.activeElement === ultimo || !modalRevisao.contains(document.activeElement))) {
            evento.preventDefault();
            primeiro.focus();
        }
    });
    document.addEventListener("layoutbase:carregada", atualizarBadge);

    async function carregarCatalogo() {
        lista.setAttribute("aria-busy", "true");
        try {
            todosProdutos = await requisitar();
            renderizarCategorias();
            renderizarProdutos();
            renderizarSacola();
        } catch (erro) {
            lista.setAttribute("aria-busy", "false");
            lista.replaceChildren();
            const erroBox = elemento("div", "estado-vazio-catalogo erro-catalogo");
            erroBox.append(elemento("strong", "", "Não foi possível abrir o catálogo"));
            erroBox.append(elemento("p", "", "Confira se o backend e o MySQL estão ligados e tente novamente."));
            const tentar = elemento("button", "botao botao-secundario", "Tentar novamente");
            tentar.type = "button"; tentar.addEventListener("click", carregarCatalogo); erroBox.append(tentar);
            lista.append(erroBox);
            mensagemApi.textContent = "O catálogo não conseguiu se conectar ao servidor. Tente novamente em instantes.";
            mensagemApi.classList.add("mensagem-erro");
        }
    }

    carregarCatalogo();
});
