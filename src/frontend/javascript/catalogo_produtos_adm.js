// Integração da tela administrativa com a API de produtos.
// Telas e API saem do mesmo servidor: as URLs são relativas e o login vai no cookie de sessão.
document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "/api/produtos";
    const UPLOAD_URL = "/api/uploads/produtos";
    const lista = document.getElementById("lista-produtos");
    const mensagemApi = document.getElementById("mensagem-api");
    const modalCadastro = document.getElementById("modal-cadastro-produto");
    const modalEdicao = document.getElementById("modal-editar-produto");
    const modalExclusao = document.getElementById("modal-excluir-produto");
    const formularioCadastro = document.getElementById("form-cadastro-produto");
    const formularioEdicao = document.getElementById("form-editar-produto");
    const textoConfirmacao = document.getElementById("texto-confirmacao-exclusao");
    const botaoConfirmarExclusao = document.getElementById("botao-confirmar-exclusao");
    const erroExclusao = document.getElementById("erro-excluir-produto");
    const buscaProdutos = document.getElementById("busca-produtos");
    const contadorProdutos = document.getElementById("contador-produtos");
    const filtroSemEstoque = document.getElementById("filtrar-sem-estoque");
    const filtrosStatus = [...document.querySelectorAll("[data-filtro-status]")];
    const modais = [modalCadastro, modalEdicao, modalExclusao];
    const produtosPorId = new Map();
    let todosProdutos = [];
    let filtroAtual = "TODOS";
    let semEstoqueAtivo = false;
    let produtoSelecionado = null;
    const focosAnteriores = new WeakMap();

    // ---------- utilitários ----------

    function mostrarMensagem(elemento, mensagem, tipo = "") {
        elemento.textContent = mensagem;
        elemento.classList.toggle("mensagem-erro", tipo === "erro");
        elemento.classList.toggle("mensagem-sucesso", tipo === "sucesso");
    }

    function criarElemento(tag, classe, texto) {
        const elemento = document.createElement(tag);
        if (classe) elemento.className = classe;
        if (texto !== undefined) elemento.textContent = texto;
        return elemento;
    }

    function formatarPreco(centavos) {
        return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    }

    // Máscara de moeda: o usuário digita só números e o campo mostra "1.234,56".
    function centavosParaTexto(centavos) {
        return (centavos / 100).toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    }

    function textoParaCentavos(texto) {
        const digitos = String(texto).replace(/\D/g, "");
        return digitos ? Number(digitos) : 0;
    }

    function aplicarMascaraMoeda(campo) {
        const digitos = campo.value.replace(/\D/g, "").replace(/^0+/, "").slice(0, 9);
        campo.value = digitos ? centavosParaTexto(Number(digitos)) : "";
    }

    function normalizarBusca(texto) {
        return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLocaleLowerCase("pt-BR");
    }

    function semEstoque(produto) {
        return produto.status === "ATIVO" && produto.quantidade_estoque === 0;
    }

    // A API devolve "assets/produtos/arquivo.png"; o servidor entrega em "/assets/produtos/...".
    function caminhoFoto(caminho) {
        return "/" + String(caminho).replace(/^\/+/, "");
    }

    // Chamada à API pelo Cantina.requisitar (base.js). O servidor identifica o
    // administrador pela sessão; aqui só tratamos sessão encerrada e falta de permissão.
    async function requisitar(url, opcoes = {}) {
        try {
            return await Cantina.requisitar(url, opcoes);
        } catch (erro) {
            if (erro.status === 401) {
                erro.message = "Sua sessão terminou. Abrindo a tela de login…";
                Cantina.irParaLogin();
            } else if (erro.status === 403) {
                erro.message = "Sua conta não tem permissão de administrador para esta operação.";
            }
            throw erro;
        }
    }

    // ---------- modais ----------

    function abrirModal(modal, focoInicial = null) {
        focosAnteriores.set(modal, document.activeElement);
        modal.classList.add("aberto");
        modal.setAttribute("aria-hidden", "false");
        const conteudo = modal.querySelector(".modal-conteudo");
        if (conteudo) conteudo.scrollTop = 0;
        const primeiroCampo = focoInicial || modal.querySelector(
            "input:not([type='hidden']), select, textarea, button:not([disabled])",
        );
        primeiroCampo?.focus({ preventScroll: true });
    }

    function fecharModal(modal) {
        if (!modal.classList.contains("aberto")) return;
        modal.classList.remove("aberto");
        modal.setAttribute("aria-hidden", "true");
        const focoAnterior = focosAnteriores.get(modal);
        if (focoAnterior?.isConnected) focoAnterior.focus();
    }

    // ---------- listagem ----------

    // O nome do produto entra no rótulo acessível, pois os botões se repetem em cada cartão
    // ("Editar: Suco de uva"). O texto visível continua no começo do rótulo.
    function criarBotao(texto, acao, classe, produto) {
        const botao = criarElemento("button", classe, texto);
        botao.type = "button";
        botao.dataset.acao = acao;
        botao.setAttribute("aria-label", `${texto}: ${produto.nome}`);
        return botao;
    }

    function criarCard(produto) {
        // Cada cartão é um item da lista de produtos (o contêiner recebe role="list").
        const card = criarElemento("div", "card-produto");
        card.setAttribute("role", "listitem");
        card.dataset.produtoId = produto.id_produto;
        if (semEstoque(produto)) card.classList.add("sem-estoque");

        const imagem = criarElemento("img", "imagem-produto");
        imagem.alt = produto.nome;
        if (produto.foto_caminho) {
            imagem.src = caminhoFoto(produto.foto_caminho);
            imagem.addEventListener("error", () => imagem.remove(), { once: true });
        } else {
            imagem.hidden = true;
        }
        card.append(imagem);

        const conteudo = criarElemento("div", "conteudo-produto");
        conteudo.append(criarElemento("h3", "", produto.nome));
        conteudo.append(criarElemento("p", "preco-produto", formatarPreco(produto.preco_venda_centavos)));
        conteudo.append(criarElemento(
            "p",
            "precos-produto",
            "Compra: " + formatarPreco(produto.preco_compra_centavos),
        ));
        conteudo.append(criarElemento("p", "detalhe-produto", "Código: " + produto.id_produto));
        conteudo.append(criarElemento("p", "detalhe-produto", "Categoria: " + produto.categoria));
        conteudo.append(criarElemento("p", "detalhe-produto", "Estoque: " + produto.quantidade_estoque));

        const selos = criarElemento("div", "selos-produto");
        if (produto.zero_lactose) selos.append(criarElemento("span", "selo", "Zero lactose"));
        if (produto.zero_acucar) selos.append(criarElemento("span", "selo", "Zero açúcar"));
        if (selos.childElementCount) conteudo.append(selos);

        if (produto.descricao) {
            conteudo.append(criarElemento("p", "detalhe-produto", produto.descricao));
        }
        if (semEstoque(produto)) {
            conteudo.append(criarElemento("span", "aviso-estoque", "Sem estoque"));
        }
        if (produto.status === "INATIVO") {
            conteudo.append(criarElemento("span", "status-produto inativo", "Inativo"));
        }

        const acoes = criarElemento("div", "acoes-produto");
        acoes.append(criarBotao("Editar", "editar", "botao botao-principal", produto));
        if (produto.status === "ATIVO") {
            acoes.append(criarBotao("Excluir", "excluir", "botao botao-excluir", produto));
        } else {
            acoes.append(criarBotao("Reativar", "reativar", "botao botao-principal", produto));
        }
        conteudo.append(acoes);
        card.append(conteudo);
        return card;
    }

    function atualizarResumo() {
        document.getElementById("total-ativos").textContent =
            todosProdutos.filter((produto) => produto.status === "ATIVO").length;
        document.getElementById("total-inativos").textContent =
            todosProdutos.filter((produto) => produto.status === "INATIVO").length;
        document.getElementById("total-sem-estoque").textContent =
            todosProdutos.filter(semEstoque).length;
    }

    function renderizarProdutos() {
        produtosPorId.clear();
        lista.replaceChildren();
        atualizarResumo();

        const termo = normalizarBusca(buscaProdutos.value.trim());
        const produtos = todosProdutos.filter((produto) => {
            const statusCorresponde = filtroAtual === "TODOS" || produto.status === filtroAtual;
            const buscaCorresponde = !termo || normalizarBusca(
                [produto.nome, produto.categoria, String(produto.id_produto)].join(" "),
            ).includes(termo);
            return statusCorresponde && buscaCorresponde && (!semEstoqueAtivo || semEstoque(produto));
        });

        contadorProdutos.textContent = `${produtos.length} ${produtos.length === 1 ? "produto encontrado" : "produtos encontrados"}`;
        // Com produtos na tela, o contêiner é anunciado como lista ("lista com N itens").
        if (produtos.length) lista.setAttribute("role", "list");
        else lista.removeAttribute("role");
        if (produtos.length === 0) {
            const mensagem = todosProdutos.length === 0
                ? "Seu catálogo ainda está vazio. Cadastre o primeiro produto para começar."
                : "Nenhum produto corresponde a esses filtros.";
            lista.append(criarElemento("p", "estado-lista", mensagem));
            return;
        }

        produtos.forEach((produto) => {
            produtosPorId.set(String(produto.id_produto), produto);
            lista.append(criarCard(produto));
        });
    }

    // Depois de gravar, a lista é refeita e o botão que tinha o foco deixa de existir:
    // o foco vai para o botão "Editar" do mesmo produto (ou para o campo de busca, se o
    // produto saiu da lista filtrada), em vez de se perder no começo da página.
    function focarProduto(idProduto) {
        const card = [...lista.querySelectorAll("[data-produto-id]")]
            .find((item) => item.dataset.produtoId === String(idProduto));
        const destino = card?.querySelector("button[data-acao='editar']") || buscaProdutos;
        destino.focus();
    }

    async function carregarProdutos() {
        lista.removeAttribute("role");
        lista.replaceChildren(criarElemento("p", "estado-lista", "Carregando produtos..."));
        try {
            todosProdutos = await requisitar(API_URL + "?status=TODOS");
            renderizarProdutos();
        } catch (erro) {
            lista.replaceChildren(criarElemento("p", "estado-lista", "Não foi possível carregar os produtos."));
            mostrarMensagem(mensagemApi, erro.message, "erro");
        }
    }

    // ---------- formulários ----------

    // A API devolve erros com o nome da coluna; a tela usa nomes mais curtos.
    const CAMPO_VISUAL = {
        preco_compra_centavos: "preco_compra",
        preco_venda_centavos: "preco_venda",
    };

    function obterCampo(formulario, nome) {
        return formulario.elements.namedItem(nome);
    }

    function mensagemDoCampo(formulario, nomeCampo) {
        return [...formulario.querySelectorAll("[data-error-for]")]
            .find((elemento) => elemento.dataset.errorFor === nomeCampo);
    }

    function limparErroCampo(formulario, nomeCampo) {
        const campo = obterCampo(formulario, nomeCampo);
        const mensagem = mensagemDoCampo(formulario, nomeCampo);
        if (campo) {
            campo.removeAttribute("aria-invalid");
            const descricoes = (campo.getAttribute("aria-describedby") || "")
                .split(/\s+/)
                .filter((id) => id && id !== mensagem?.id);
            if (descricoes.length) campo.setAttribute("aria-describedby", descricoes.join(" "));
            else campo.removeAttribute("aria-describedby");
        }
        if (mensagem) mensagem.textContent = "";
        if (!formulario.querySelector("[aria-invalid='true']")) {
            formulario.querySelector(".feedback-form").textContent = "";
        }
    }

    function limparErrosFormulario(formulario) {
        formulario.querySelectorAll("[data-error-for]").forEach((mensagem) => {
            limparErroCampo(formulario, mensagem.dataset.errorFor);
        });
        formulario.querySelector(".feedback-form").textContent = "";
    }

    function exibirErrosFormulario(formulario, erros) {
        const feedback = formulario.querySelector(".feedback-form");
        feedback.textContent = "";
        Object.entries(erros).forEach(([campo, mensagem]) => {
            const campoVisual = CAMPO_VISUAL[campo] || campo;
            const controle = obterCampo(formulario, campoVisual);
            const mensagemCampo = mensagemDoCampo(formulario, campoVisual);
            if (controle && controle.type !== "hidden" && mensagemCampo) {
                if (!mensagemCampo.id) mensagemCampo.id = `${formulario.id}-erro-${campoVisual}`;
                controle.setAttribute("aria-invalid", "true");
                const descricoes = new Set((controle.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean));
                descricoes.add(mensagemCampo.id);
                controle.setAttribute("aria-describedby", [...descricoes].join(" "));
                mensagemCampo.textContent = mensagem;
            } else {
                feedback.textContent += `${feedback.textContent ? " " : ""}${mensagem}`;
            }
        });
        if (Object.keys(erros).length) {
            feedback.textContent = `Revise os campos destacados. ${feedback.textContent}`.trim();
            formulario.querySelector("[aria-invalid='true']")?.focus();
        }
    }

    // Validação na tela (o servidor valida de novo; esta só evita idas desnecessárias).
    function validarFormulario(formulario) {
        const erros = {};
        const nome = obterCampo(formulario, "nome").value.trim();
        const categoria = obterCampo(formulario, "categoria").value.trim();
        const compra = textoParaCentavos(obterCampo(formulario, "preco_compra").value);
        const venda = textoParaCentavos(obterCampo(formulario, "preco_venda").value);
        const quantidadeTexto = obterCampo(formulario, "quantidade_estoque").value.trim();

        if (nome.length < 2) erros.nome = "Informe o nome do produto (mínimo 2 caracteres).";
        if (categoria.length < 2) erros.categoria = "Informe a categoria (mínimo 2 caracteres).";
        if (compra <= 0) erros.preco_compra = "Informe o preço de compra.";
        if (venda <= 0) erros.preco_venda = "Informe o preço de venda.";
        else if (compra > 0 && venda < compra) {
            erros.preco_venda = "O preço de venda não pode ser menor que o preço de compra.";
        }
        if (quantidadeTexto !== "" && !/^\d+$/.test(quantidadeTexto)) {
            erros.quantidade_estoque = "Informe uma quantidade inteira, sem sinal negativo.";
        }
        return erros;
    }

    function atualizarPreview(formulario, caminho = null, arquivo = null) {
        const preview = formulario.querySelector(".preview-imagem");
        if (!preview) return;
        if (preview.dataset.urlTemporaria) URL.revokeObjectURL(preview.dataset.urlTemporaria);
        delete preview.dataset.urlTemporaria;
        if (arquivo) {
            const url = URL.createObjectURL(arquivo);
            preview.src = url;
            preview.dataset.urlTemporaria = url;
            preview.hidden = false;
        } else if (caminho) {
            preview.src = caminhoFoto(caminho);
            preview.hidden = false;
        } else {
            preview.removeAttribute("src");
            preview.hidden = true;
        }
    }

    function montarPayload(formulario, fotoCaminho = null) {
        const foto = obterCampo(formulario, "foto_caminho").value.trim();
        return {
            nome: obterCampo(formulario, "nome").value.trim(),
            categoria: obterCampo(formulario, "categoria").value.trim(),
            descricao: obterCampo(formulario, "descricao").value.trim(),
            preco_compra_centavos: textoParaCentavos(obterCampo(formulario, "preco_compra").value),
            preco_venda_centavos: textoParaCentavos(obterCampo(formulario, "preco_venda").value),
            quantidade_estoque: Number(obterCampo(formulario, "quantidade_estoque").value || 0),
            foto_caminho: fotoCaminho === null ? (foto || null) : fotoCaminho,
        };
    }

    function preencherFormulario(formulario, produto) {
        formulario.reset();
        obterCampo(formulario, "nome").value = produto.nome;
        obterCampo(formulario, "categoria").value = produto.categoria;
        obterCampo(formulario, "descricao").value = produto.descricao || "";
        obterCampo(formulario, "preco_compra").value = centavosParaTexto(produto.preco_compra_centavos);
        obterCampo(formulario, "preco_venda").value = centavosParaTexto(produto.preco_venda_centavos);
        obterCampo(formulario, "quantidade_estoque").value = produto.quantidade_estoque;
        obterCampo(formulario, "foto_caminho").value = produto.foto_caminho || "";
        atualizarPreview(formulario, produto.foto_caminho);
    }

    async function salvarFormulario(formulario, metodo, idProduto = null) {
        limparErrosFormulario(formulario);
        mostrarMensagem(mensagemApi, "");

        const errosTela = validarFormulario(formulario);
        if (Object.keys(errosTela).length) {
            exibirErrosFormulario(formulario, errosTela);
            return;
        }

        const botaoSalvar = formulario.querySelector("button[type='submit']");
        const textoOriginal = botaoSalvar.textContent;
        botaoSalvar.disabled = true;
        botaoSalvar.textContent = "Salvando…";
        try {
            let fotoCaminho = null;
            const imagem = obterCampo(formulario, "imagem").files[0];
            if (imagem) {
                const dadosImagem = new FormData();
                dadosImagem.append("imagem", imagem);
                const resultadoUpload = await requisitar(UPLOAD_URL, { method: "POST", body: dadosImagem });
                fotoCaminho = resultadoUpload.foto_caminho;
            }
            await requisitar(idProduto ? API_URL + "/" + idProduto : API_URL, {
                method: metodo,
                json: montarPayload(formulario, fotoCaminho),
            });
            fecharModal(idProduto ? modalEdicao : modalCadastro);
            formulario.reset();
            atualizarPreview(formulario);
            await carregarProdutos();
            // Na edição, o foco tinha voltado para o botão "Editar" do cartão, que foi refeito.
            if (idProduto) focarProduto(idProduto);
            mostrarMensagem(mensagemApi, metodo === "POST" ? "Produto cadastrado." : "Produto atualizado.", "sucesso");
        } catch (erro) {
            if (Object.keys(erro.campos || {}).length) {
                exibirErrosFormulario(formulario, erro.campos);
            } else {
                formulario.querySelector(".feedback-form").textContent = erro.message;
            }
        } finally {
            botaoSalvar.disabled = false;
            botaoSalvar.textContent = textoOriginal;
        }
    }

    function abrirCadastro() {
        formularioCadastro.reset();
        atualizarPreview(formularioCadastro);
        limparErrosFormulario(formularioCadastro);
        abrirModal(modalCadastro, obterCampo(formularioCadastro, "nome"));
    }

    [formularioCadastro, formularioEdicao].forEach((formulario) => {
        // Enter dentro de um campo NÃO grava: o produto só é salvo pelo clique no botão.
        Cantina.bloquearEnvioPorEnter(formulario);

        formulario.querySelectorAll(".campo-moeda").forEach((campo) => {
            campo.addEventListener("input", () => aplicarMascaraMoeda(campo));
        });

        formulario.querySelectorAll("[data-error-for]").forEach((mensagem) => {
            const campo = obterCampo(formulario, mensagem.dataset.errorFor);
            if (!campo) return;
            const limparErro = () => limparErroCampo(formulario, mensagem.dataset.errorFor);
            campo.addEventListener("input", limparErro);
            campo.addEventListener("change", limparErro);
        });

        const seletorImagem = obterCampo(formulario, "imagem");
        seletorImagem.addEventListener("change", () => {
            const arquivo = seletorImagem.files[0];
            limparErroCampo(formulario, "imagem");
            if (!arquivo) {
                atualizarPreview(formulario, obterCampo(formulario, "foto_caminho").value);
                return;
            }
            const permitido = ["image/jpeg", "image/png", "image/webp"].includes(arquivo.type);
            if (!permitido || arquivo.size > 5 * 1024 * 1024) {
                exibirErrosFormulario(formulario, {
                    imagem: !permitido ? "Use uma imagem JPG, PNG ou WebP." : "Escolha uma imagem de até 5 MB.",
                });
                seletorImagem.value = "";
                atualizarPreview(formulario, obterCampo(formulario, "foto_caminho").value);
                return;
            }
            obterCampo(formulario, "foto_caminho").value = "";
            atualizarPreview(formulario, null, arquivo);
        });
    });

    // Só grava quando o envio vem do clique no botão de salvar.
    formularioCadastro.addEventListener("submit", (evento) => {
        evento.preventDefault();
        if (evento.submitter?.type !== "submit") return;
        salvarFormulario(formularioCadastro, "POST");
    });

    formularioEdicao.addEventListener("submit", (evento) => {
        evento.preventDefault();
        if (evento.submitter?.type !== "submit" || !produtoSelecionado) return;
        salvarFormulario(formularioEdicao, "PUT", produtoSelecionado.id_produto);
    });

    // ---------- filtros e menu ----------

    document.getElementById("abrir-cadastro-produto").addEventListener("click", abrirCadastro);
    document.getElementById("abrir-cadastro-produto-topo").addEventListener("click", abrirCadastro);

    function selecionarFiltroStatus(status) {
        filtroAtual = status;
        filtrosStatus.forEach((botao) => {
            const selecionado = botao.dataset.filtroStatus === status;
            botao.classList.toggle("selecionado", selecionado);
            botao.setAttribute("aria-pressed", String(selecionado));
        });
    }

    filtrosStatus.forEach((botao) => {
        botao.addEventListener("click", () => {
            semEstoqueAtivo = false;
            filtroSemEstoque.setAttribute("aria-pressed", "false");
            filtroSemEstoque.classList.remove("ativo");
            selecionarFiltroStatus(botao.dataset.filtroStatus);
            renderizarProdutos();
        });
    });

    buscaProdutos.addEventListener("input", renderizarProdutos);

    filtroSemEstoque.addEventListener("click", () => {
        semEstoqueAtivo = !semEstoqueAtivo;
        filtroSemEstoque.setAttribute("aria-pressed", String(semEstoqueAtivo));
        filtroSemEstoque.classList.toggle("ativo", semEstoqueAtivo);
        if (semEstoqueAtivo) selecionarFiltroStatus("ATIVO");
        renderizarProdutos();
    });

    document.getElementById("alternar-menu").addEventListener("click", (evento) => {
        const recolhido = document.getElementById("menu-admin").classList.toggle("recolhido");
        document.querySelector(".layout-admin").classList.toggle("menu-recolhido", recolhido);
        evento.currentTarget.setAttribute("aria-expanded", String(!recolhido));
        evento.currentTarget.textContent = recolhido ? "Expandir menu" : "Recolher menu";
    });

    document.getElementById("fechar-cadastro-produto").addEventListener("click", () => fecharModal(modalCadastro));
    document.getElementById("fechar-editar-produto").addEventListener("click", () => fecharModal(modalEdicao));
    document.getElementById("fechar-excluir-produto").addEventListener("click", () => fecharModal(modalExclusao));
    document.getElementById("botao-cancelar-exclusao").addEventListener("click", () => fecharModal(modalExclusao));

    modais.forEach((modal) => {
        modal.addEventListener("click", (evento) => {
            if (evento.target === modal) fecharModal(modal);
        });
    });

    // Esc fecha o modal aberto e Tab circula apenas dentro dele.
    document.addEventListener("keydown", (evento) => {
        const modalAberto = modais.find((modal) => modal.classList.contains("aberto"));
        if (!modalAberto) return;
        if (evento.key === "Escape") {
            evento.preventDefault();
            fecharModal(modalAberto);
            return;
        }
        if (evento.key !== "Tab") return;
        const focaveis = [...modalAberto.querySelectorAll(
            "a[href], button:not([disabled]), input:not([disabled]):not([type='hidden']), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])",
        )].filter((elemento) => elemento.getClientRects().length > 0);
        if (!focaveis.length) return;
        const primeiro = focaveis[0];
        const ultimo = focaveis[focaveis.length - 1];
        if (evento.shiftKey && (document.activeElement === primeiro || !modalAberto.contains(document.activeElement))) {
            evento.preventDefault();
            ultimo.focus();
        } else if (!evento.shiftKey && (document.activeElement === ultimo || !modalAberto.contains(document.activeElement))) {
            evento.preventDefault();
            primeiro.focus();
        }
    });

    // ---------- ações dos cards ----------

    lista.addEventListener("click", async (evento) => {
        const botao = evento.target.closest("button[data-acao]");
        if (!botao) return;
        const card = botao.closest("[data-produto-id]");
        const produto = produtosPorId.get(card?.dataset.produtoId);
        if (!produto) return;

        if (botao.dataset.acao === "editar") {
            produtoSelecionado = produto;
            preencherFormulario(formularioEdicao, produto);
            limparErrosFormulario(formularioEdicao);
            abrirModal(modalEdicao);
            return;
        }

        if (botao.dataset.acao === "excluir") {
            produtoSelecionado = produto;
            textoConfirmacao.textContent = `Deseja excluir "${produto.nome}"? Ele sairá do catálogo, mas continuará salvo no banco como inativo e poderá ser reativado.`;
            erroExclusao.textContent = "";
            abrirModal(modalExclusao, document.getElementById("botao-cancelar-exclusao"));
            return;
        }

        if (botao.dataset.acao === "reativar") {
            botao.disabled = true;
            try {
                await requisitar(API_URL + "/" + produto.id_produto + "/reativar", { method: "PATCH" });
                await carregarProdutos();
                focarProduto(produto.id_produto);
                mostrarMensagem(mensagemApi, "Produto reativado.", "sucesso");
            } catch (erro) {
                mostrarMensagem(mensagemApi, erro.message, "erro");
            } finally {
                botao.disabled = false;
            }
        }
    });

    // "Excluir" é uma exclusão lógica: o produto fica INATIVO e continua no banco.
    botaoConfirmarExclusao.addEventListener("click", async () => {
        if (!produtoSelecionado) return;
        botaoConfirmarExclusao.disabled = true;
        erroExclusao.textContent = "";
        try {
            await requisitar(API_URL + "/" + produtoSelecionado.id_produto + "/inativar", { method: "PATCH" });
            fecharModal(modalExclusao);
            produtoSelecionado = null;
            await carregarProdutos();
            buscaProdutos.focus({ preventScroll: true });
            mostrarMensagem(mensagemApi, "Produto excluído (inativado). Ele continua salvo e pode ser reativado.", "sucesso");
        } catch (erro) {
            // O modal continua aberto: a mensagem aparece dentro dele (e é anunciada por role="alert").
            erroExclusao.textContent = erro.message;
        } finally {
            botaoConfirmarExclusao.disabled = false;
        }
    });

    // Só administradores usam esta tela: quem não está logado vai para o login e
    // quem não é administrador volta ao catálogo (Cantina.exigirAdministrador).
    Cantina.exigirAdministrador().then(carregarProdutos);
});
