// Tela administrativa de QR Codes: cartaz da cantina e etiquetas dos produtos ativos,
// com busca por nome e impressão de cada parte em separado.
// Usa as funções compartilhadas do objeto Cantina (base.js).
document.addEventListener("DOMContentLoaded", async () => {
    "use strict";

    // Só administradores passam daqui: quem não está logado vai para o login e
    // quem não é administrador volta ao catálogo.
    await Cantina.exigirAdministrador();

    const API_QR = "/api/qrcode";
    const API_PRODUTOS = "/api/produtos?status=ATIVO";
    const ESPERA_IMAGENS_MS = 8000;
    // Classes postas no <body> só durante a impressão (ver @media print em admin.css).
    const CLASSE_CARTAZ = "imprimindo-cartaz";
    const CLASSE_ETIQUETAS = "imprimindo-etiquetas";
    const el = Cantina.criarElemento;

    const mensagemApi = document.getElementById("mensagem-api");
    const avisoLocal = document.getElementById("aviso-somente-local");
    const enderecoQr = document.getElementById("endereco-qr");
    const cartaz = document.getElementById("cartaz-cantina");
    const urlCantina = document.getElementById("url-cantina");
    const botaoImprimirCartaz = document.getElementById("imprimir-cartaz");
    const botaoImprimirEtiquetas = document.getElementById("imprimir-etiquetas");
    const formularioBusca = document.getElementById("form-busca-etiquetas");
    const campoBusca = document.getElementById("busca-etiquetas");
    const contador = document.getElementById("contador-etiquetas");
    const estadoLista = document.getElementById("estado-etiquetas");
    const listaEtiquetas = document.getElementById("lista-etiquetas");

    // Uma entrada por produto ativo: { item: <li>, nomeBusca: nome sem acentos e em minúsculas }.
    let etiquetas = [];
    let produtosCarregados = false;

    // ---------- utilitários ----------

    const plural = Cantina.plural;

    // Busca sem diferença entre maiúsculas, minúsculas e acentos ("pao" encontra "Pão").
    function normalizar(texto) {
        return String(texto ?? "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLocaleLowerCase("pt-BR");
    }

    // Traduz o erro da API em um texto claro. Sessão encerrada leva ao login.
    function tratarErro(erro) {
        if (erro.status === 401) {
            Cantina.irParaLogin();
            return "Sua sessão terminou. Abrindo a tela de login…";
        }
        if (erro.status === 403) {
            return "Sua conta não tem permissão de administrador para ver os QR Codes.";
        }
        return erro.message;
    }

    // Botão "Tentar novamente". Como ele some quando a região é redesenhada, o foco
    // segue para o elemento indicado em focoDepois, em vez de se perder na página.
    function botaoTentar(aoTentar, focoDepois) {
        const botao = el("button", "botao botao-secundario", "Tentar novamente");
        botao.type = "button";
        botao.addEventListener("click", async () => {
            await aoTentar();
            focoDepois()?.focus({ preventScroll: true });
        });
        return botao;
    }

    // ---------- menu lateral ----------

    document.getElementById("alternar-menu").addEventListener("click", (evento) => {
        const recolhido = document.getElementById("menu-admin").classList.toggle("recolhido");
        document.querySelector(".layout-admin").classList.toggle("menu-recolhido", recolhido);
        evento.currentTarget.setAttribute("aria-expanded", String(!recolhido));
        evento.currentTarget.textContent = recolhido ? "Expandir menu" : "Recolher menu";
    });

    // ---------- imagens dos QR Codes ----------

    // Se a imagem não carregar (servidor fora, produto que deixou de existir),
    // entra um texto no lugar dela.
    function vigiarImagem(imagem) {
        imagem.addEventListener("error", () => {
            imagem.replaceWith(el("p", "qr-indisponivel", "QR Code indisponível"));
        }, { once: true });
    }

    // Promise resolvida quando todas as imagens terminaram de carregar (ou falharam),
    // com um tempo máximo para a tela não ficar esperando para sempre.
    function esperarImagens(imagens) {
        const pendentes = imagens.filter((imagem) => !imagem.complete);
        if (!pendentes.length) return Promise.resolve();
        const carregadas = Promise.all(pendentes.map((imagem) => new Promise((resolver) => {
            imagem.addEventListener("load", resolver, { once: true });
            imagem.addEventListener("error", resolver, { once: true });
        })));
        const tempoMaximo = new Promise((resolver) => { window.setTimeout(resolver, ESPERA_IMAGENS_MS); });
        return Promise.race([carregadas, tempoMaximo]);
    }

    // ---------- endereço gravado nos QR Codes ----------

    async function carregarEndereco() {
        enderecoQr.classList.remove("estado-erro");
        enderecoQr.replaceChildren(el("p", "", "Consultando o endereço dos QR Codes…"));
        try {
            const dados = await Cantina.requisitar(API_QR);
            const linha = el("p", "", "Endereço em uso nos QR Codes: ");
            linha.append(el("strong", "qr-url", dados.url_base || "não informado pelo servidor"));
            enderecoQr.replaceChildren(linha);
            // Endereço local (127.0.0.1 ou localhost): o QR só abre neste computador.
            avisoLocal.hidden = dados.somente_local !== true;
            urlCantina.textContent = dados.url_cantina || "";
        } catch (erro) {
            avisoLocal.hidden = true;
            urlCantina.textContent = "";
            enderecoQr.classList.add("estado-erro");
            enderecoQr.replaceChildren(
                el("p", "", `Não foi possível consultar o endereço dos QR Codes. ${tratarErro(erro)}`),
                botaoTentar(carregarEndereco, () => enderecoQr.querySelector("button") || enderecoQr),
            );
        }
    }

    // ---------- etiquetas dos produtos ----------

    // Estado da lista: carregando, vazio ou erro (com um botão ou link de apoio).
    function mostrarEstado(texto, { erro = false, acao = null } = {}) {
        estadoLista.replaceChildren(el("p", "", texto));
        estadoLista.classList.toggle("estado-erro", erro);
        if (acao) estadoLista.append(acao);
        estadoLista.hidden = false;
        listaEtiquetas.hidden = true;
    }

    function mostrarLista() {
        estadoLista.hidden = true;
        estadoLista.replaceChildren();
        listaEtiquetas.hidden = false;
    }

    function criarEtiqueta(produto) {
        const item = el("li", "qr-etiqueta");

        const imagem = el("img", "qr-imagem");
        // loading="lazy" vem antes do src: só as etiquetas perto da área visível são buscadas.
        imagem.loading = "lazy";
        imagem.decoding = "async";
        imagem.width = 160;
        imagem.height = 160;
        imagem.alt = `QR Code do produto ${produto.nome}`;
        vigiarImagem(imagem);
        imagem.src = `${API_QR}/produtos/${encodeURIComponent(produto.id_produto)}.svg`;

        item.append(
            imagem,
            el("h3", "qr-etiqueta-nome", produto.nome),
            el("p", "qr-etiqueta-preco", Cantina.formatarPreco(produto.preco_venda_centavos)),
            el("p", "qr-etiqueta-codigo", `Código ${produto.id_produto}`),
        );
        return { item, nomeBusca: normalizar(produto.nome) };
    }

    // Mostra só as etiquetas cujo nome contém o texto buscado. As escondidas ficam
    // com o atributo hidden e, por isso, também não saem na impressão.
    function aplicarBusca() {
        if (!produtosCarregados) return;
        const termo = normalizar(campoBusca.value.trim());
        let visiveis = 0;
        etiquetas.forEach((etiqueta) => {
            const mostrar = !termo || etiqueta.nomeBusca.includes(termo);
            etiqueta.item.hidden = !mostrar;
            if (mostrar) visiveis += 1;
        });

        if (!etiquetas.length) {
            const link = el("a", "botao botao-secundario", "Ir para Produtos");
            link.href = "/html/catalogo_produtos_adm.html";
            contador.textContent = "Nenhuma etiqueta para mostrar.";
            mostrarEstado("Ainda não há produtos ativos. Cadastre ou reative um produto para gerar as etiquetas.", { acao: link });
            return;
        }
        if (!visiveis) {
            contador.textContent = "Nenhuma etiqueta encontrada.";
            mostrarEstado("Nenhum produto ativo corresponde a essa busca.");
            return;
        }
        contador.textContent = termo
            ? `${visiveis} de ${plural(etiquetas.length, "etiqueta", "etiquetas")} ${visiveis === 1 ? "aparece" : "aparecem"} na busca. A impressão segue a busca.`
            : `${plural(visiveis, "etiqueta", "etiquetas")}, uma para cada produto ativo.`;
        mostrarLista();
    }

    async function carregarProdutos() {
        produtosCarregados = false;
        etiquetas = [];
        listaEtiquetas.replaceChildren();
        contador.textContent = "";
        mostrarEstado("Carregando produtos…");
        try {
            const resultado = await Cantina.requisitar(API_PRODUTOS);
            // A API de produtos devolve a lista direto no corpo da resposta.
            const lista = Array.isArray(resultado) ? resultado : (resultado.produtos || []);
            const ativos = lista
                .filter((produto) => !produto.status || produto.status === "ATIVO")
                .sort((a, b) => String(a.nome).localeCompare(String(b.nome), "pt-BR", { sensitivity: "base" }));
            etiquetas = ativos.map(criarEtiqueta);
            listaEtiquetas.replaceChildren(...etiquetas.map((etiqueta) => etiqueta.item));
            produtosCarregados = true;
            aplicarBusca();
        } catch (erro) {
            mostrarEstado(tratarErro(erro), {
                erro: true,
                acao: botaoTentar(carregarProdutos, () => estadoLista.querySelector("button") || campoBusca),
            });
        }
    }

    campoBusca.addEventListener("input", aplicarBusca);

    // Enter no campo de busca só filtra a lista (é uma consulta, nada é gravado).
    formularioBusca.addEventListener("submit", (evento) => {
        evento.preventDefault();
        aplicarBusca();
    });

    document.getElementById("limpar-busca").addEventListener("click", () => {
        formularioBusca.reset();
        aplicarBusca();
        campoBusca.focus();
    });

    // ---------- impressão ----------

    // Cada botão imprime só a sua parte: a classe no <body> esconde a outra seção
    // no papel e é retirada quando a impressão termina (evento afterprint).
    function limparModoDeImpressao() {
        document.body.classList.remove(CLASSE_CARTAZ, CLASSE_ETIQUETAS);
    }

    function imprimir(classe) {
        limparModoDeImpressao();
        document.body.classList.add(classe);
        window.print();
    }

    window.addEventListener("afterprint", limparModoDeImpressao);

    // Impressão pelo navegador (Ctrl+P), sem os botões: sai o cartaz e depois as
    // etiquetas. As imagens ainda não buscadas (loading="lazy") passam a carregar.
    window.addEventListener("beforeprint", () => {
        listaEtiquetas.querySelectorAll("img").forEach((imagem) => { imagem.loading = "eager"; });
    });

    // Enquanto as imagens terminam de carregar, o botão fica ocupado; depois o foco volta a ele.
    async function prepararImagens(botao, textoOcupado, imagens) {
        if (imagens.every((imagem) => imagem.complete)) return;
        await Cantina.comBotaoOcupado(botao, textoOcupado, () => esperarImagens(imagens));
        botao.focus({ preventScroll: true });
    }

    botaoImprimirCartaz.addEventListener("click", async () => {
        Cantina.mostrarMensagem(mensagemApi, "");
        const imagem = cartaz.querySelector("img");
        if (imagem) await prepararImagens(botaoImprimirCartaz, "Preparando cartaz…", [imagem]);
        if (!cartaz.querySelector("img")) {
            Cantina.mostrarMensagem(mensagemApi, "O QR Code do cartaz não está disponível, por isso o cartaz não foi impresso. Recarregue a página e tente de novo.", "erro");
            return;
        }
        imprimir(CLASSE_CARTAZ);
    });

    botaoImprimirEtiquetas.addEventListener("click", async () => {
        Cantina.mostrarMensagem(mensagemApi, "");
        // A busca ativa define o que é impresso: só as etiquetas que estão na lista.
        const visiveis = etiquetas.filter((etiqueta) => !etiqueta.item.hidden);
        if (!visiveis.length) {
            Cantina.mostrarMensagem(mensagemApi, etiquetas.length
                ? "Nenhuma etiqueta aparece na lista com essa busca. Limpe a busca para imprimir."
                : "Ainda não há etiquetas na lista para imprimir.", "erro");
            return;
        }

        // As etiquetas fora da área visível ainda não tiveram a imagem buscada
        // (loading="lazy"): todas são carregadas antes de abrir a impressão.
        const imagens = visiveis.map((etiqueta) => etiqueta.item.querySelector("img")).filter(Boolean);
        imagens.forEach((imagem) => { imagem.loading = "eager"; });
        await prepararImagens(botaoImprimirEtiquetas, "Preparando etiquetas…", imagens);

        const semQr = visiveis.filter((etiqueta) => !etiqueta.item.querySelector("img")).length;
        if (semQr === visiveis.length) {
            Cantina.mostrarMensagem(mensagemApi, "Os QR Codes das etiquetas não estão disponíveis, por isso nada foi impresso. Recarregue a página e tente de novo.", "erro");
            return;
        }
        if (semQr) {
            Cantina.mostrarMensagem(mensagemApi, `${plural(semQr, "etiqueta está", "etiquetas estão")} sem QR Code e ${semQr === 1 ? "sai" : "saem"} com o texto "QR Code indisponível". Recarregue a página para tentar de novo.`, "erro");
        }
        imprimir(CLASSE_ETIQUETAS);
    });

    // ---------- início ----------

    // A imagem do cartaz está no HTML e pode ter falhado antes deste script rodar
    // (o evento "error" já passou). Pedir a imagem de novo faz o navegador avisar
    // outra vez se ela carregou ou falhou.
    const imagemCartaz = document.getElementById("imagem-cartaz");
    vigiarImagem(imagemCartaz);
    if (imagemCartaz.complete && imagemCartaz.naturalWidth === 0) {
        imagemCartaz.src = imagemCartaz.getAttribute("src");
    }

    carregarEndereco();
    carregarProdutos();
});
