// Integração da tela administrativa com a API de produtos.
document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:5000/api/produtos";
    const lista = document.getElementById("lista-produtos");
    const mensagemApi = document.getElementById("mensagem-api");
    const modalCadastro = document.getElementById("modal-cadastro-produto");
    const modalEdicao = document.getElementById("modal-editar-produto");
    const modalExclusao = document.getElementById("modal-excluir-produto");
    const formularioCadastro = document.getElementById("form-cadastro-produto");
    const formularioEdicao = document.getElementById("form-editar-produto");
    const textoConfirmacao = document.getElementById("texto-confirmacao-exclusao");
    const tituloConfirmacao = document.getElementById("titulo-confirmacao-produto");
    const botaoConfirmarExclusao = document.getElementById("botao-confirmar-exclusao");
    const buscaProdutos = document.getElementById("busca-produtos");
    const contadorProdutos = document.getElementById("contador-produtos");
    const filtrosStatus = [...document.querySelectorAll("[data-filtro-status]")];
    const produtosPorId = new Map();
    let todosProdutos = [];
    let filtroAtual = "TODOS";
    let estoqueBaixoAtivo = false;
    let produtoSelecionado = null;
    let acaoConfirmacao = null;
    const focosAnteriores = new WeakMap();

    function mostrarMensagem(elemento, mensagem, tipo = "") {
        elemento.textContent = mensagem;
        elemento.classList.toggle("mensagem-erro", tipo === "erro");
        elemento.classList.toggle("mensagem-sucesso", tipo === "sucesso");
    }

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

    async function requisitar(url, opcoes = {}) {
        const resposta = await fetch(url, {
            ...opcoes,
            headers: {
                Accept: "application/json",
                "X-Actor": "administrador-local",
                ...(opcoes.headers || {}),
            },
        });

        let resultado = {};
        try {
            resultado = await resposta.json();
        } catch {
            resultado = {};
        }

        if (!resposta.ok) {
            const erro = new Error(resultado.erro || "Não foi possível concluir a operação.");
            erro.campos = resultado.campos || {};
            throw erro;
        }

        return resultado;
    }

    function criarElemento(tag, classe, texto) {
        const elemento = document.createElement(tag);
        if (classe) elemento.className = classe;
        if (texto !== undefined) elemento.textContent = texto;
        return elemento;
    }

    function formatarPreco(centavos) {
        return (centavos / 100).toLocaleString("pt-BR", {
            style: "currency",
            currency: "BRL",
        });
    }

    function formatarValidade(validade) {
        if (!validade) return "Validade não informada";
        const [ano, mes, dia] = validade.split("-");
        return "Validade: " + dia + "/" + mes + "/" + ano;
    }

    function criarBotao(texto, acao, classe) {
        const botao = criarElemento("button", classe, texto);
        botao.type = "button";
        botao.dataset.acao = acao;
        return botao;
    }

    function criarCard(produto) {
        const card = criarElemento("article", "card-produto");
        card.dataset.produtoId = produto.id_produto;
        if (produto.status === "ATIVO" && produto.quantidade_estoque <= produto.estoque_minimo) {
            card.classList.add("estoque-alerta");
        }

        const imagem = criarElemento("img", "imagem-produto");
        imagem.alt = produto.nome;
        if (produto.foto_caminho) {
            imagem.src = new URL("../../../" + produto.foto_caminho, document.baseURI).href;
            imagem.addEventListener("error", () => imagem.remove(), { once: true });
        } else {
            imagem.hidden = true;
        }
        card.append(imagem);

        const conteudo = criarElemento("div", "conteudo-produto");
        conteudo.append(criarElemento("h3", "", produto.nome));
        conteudo.append(criarElemento("p", "preco-produto", formatarPreco(produto.preco_centavos)));
        conteudo.append(criarElemento("p", "detalhe-produto", "Código: " + produto.codigo_produto));
        conteudo.append(criarElemento("p", "detalhe-produto", "Categoria: " + produto.categoria));
        conteudo.append(criarElemento(
            "p",
            "detalhe-produto",
            "Estoque: " + produto.quantidade_estoque
                + " (mín. " + produto.estoque_minimo + " / máx. " + produto.estoque_maximo + ")",
        ));
        conteudo.append(criarElemento("p", "validade", formatarValidade(produto.validade)));

        const selos = criarElemento("div", "selos-produto");
        if (produto.zero_lactose) selos.append(criarElemento("span", "selo", "Zero lactose"));
        if (produto.zero_acucar) selos.append(criarElemento("span", "selo", "Zero açúcar"));
        if (selos.childElementCount) conteudo.append(selos);

        if (produto.descricao) {
            conteudo.append(criarElemento("p", "detalhe-produto", produto.descricao));
        }

        if (produto.status === "INATIVO") {
            conteudo.append(criarElemento("span", "status-produto inativo", "Inativo"));
        }

        const hoje = new Date();
        const hojeIso = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, "0")}-${String(hoje.getDate()).padStart(2, "0")}`;
        if (produto.validade && produto.validade < hojeIso) {
            card.classList.add("validade-alerta");
            conteudo.append(criarElemento("span", "aviso-validade", "Validade vencida"));
        }

        const acoes = criarElemento("div", "acoes-produto");
        acoes.append(criarBotao("Editar", "editar", "botao botao-principal"));
        if (produto.status === "ATIVO") {
            acoes.append(criarBotao("Inativar", "inativar", "botao botao-excluir"));
        } else {
            acoes.append(criarBotao("Reativar", "reativar", "botao botao-principal"));
        }
        acoes.append(criarBotao(
            "Excluir definitivamente",
            "excluir",
            "botao botao-exclusao-definitiva",
        ));
        conteudo.append(acoes);
        card.append(conteudo);
        return card;
    }

    function atualizarResumo() {
        const ativos = todosProdutos.filter((produto) => produto.status === "ATIVO");
        const inativos = todosProdutos.filter((produto) => produto.status === "INATIVO");
        const estoqueBaixo = ativos.filter((produto) => produto.quantidade_estoque <= produto.estoque_minimo);
        document.getElementById("total-ativos").textContent = ativos.length;
        document.getElementById("total-inativos").textContent = inativos.length;
        document.getElementById("total-estoque-baixo").textContent = estoqueBaixo.length;
    }

    function normalizarBusca(texto) {
        return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
    }

    function renderizarProdutos() {
        produtosPorId.clear();
        lista.replaceChildren();
        atualizarResumo();

        const termo = normalizarBusca(buscaProdutos.value.trim());
        const produtos = todosProdutos.filter((produto) => {
            const statusCorresponde = filtroAtual === "TODOS" || produto.status === filtroAtual;
            const buscaCorresponde = !termo || normalizarBusca(
                [produto.nome, produto.codigo_produto, produto.categoria].join(" "),
            ).includes(termo);
            const estoqueCorresponde = !estoqueBaixoAtivo
                || (produto.status === "ATIVO" && produto.quantidade_estoque <= produto.estoque_minimo);
            return statusCorresponde && buscaCorresponde && estoqueCorresponde;
        });

        contadorProdutos.textContent = `${produtos.length} ${produtos.length === 1 ? "produto encontrado" : "produtos encontrados"}`;
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

    async function carregarProdutos() {
        lista.replaceChildren(criarElemento("p", "estado-lista", "Carregando produtos..."));
        try {
            todosProdutos = await requisitar(API_URL + "?status=TODOS");
            renderizarProdutos();
        } catch (erro) {
            lista.replaceChildren(criarElemento("p", "estado-lista", "Não foi possível carregar os produtos."));
            mostrarMensagem(mensagemApi, erro.message + " Confira se o MySQL e o backend estão ligados.", "erro");
        }
    }

    function limparErrosFormulario(formulario) {
        formulario.querySelectorAll("[aria-invalid='true']").forEach((campo) => {
            campo.removeAttribute("aria-invalid");
        });
        formulario.querySelectorAll("[data-error-for]").forEach((mensagem) => {
            mensagem.textContent = "";
        });
        formulario.querySelector(".feedback-form").textContent = "";
    }

    function exibirErrosFormulario(formulario, erros) {
        const feedback = formulario.querySelector(".feedback-form");
        Object.entries(erros).forEach(([campo, mensagem]) => {
            // A interface recebe reais, mas o contrato da API reporta erros em centavos.
            const campoVisual = campo === "preco_centavos" ? "preco" : campo;
            const controle = formulario.elements.namedItem(campoVisual);
            const mensagemCampo = [...formulario.querySelectorAll("[data-error-for]")]
                .find((elemento) => elemento.dataset.errorFor === campoVisual);
            if (controle && mensagemCampo) {
                controle.setAttribute("aria-invalid", "true");
                mensagemCampo.textContent = mensagem;
            } else {
                feedback.textContent = mensagem;
            }
        });
    }

    function obterCampo(formulario, nome) {
        return formulario.elements.namedItem(nome);
    }

    function montarPayload(formulario) {
        const numero = (nome) => Number(obterCampo(formulario, nome).value || 0);
        const validade = obterCampo(formulario, "validade").value;
        const foto = obterCampo(formulario, "foto_caminho").value.trim();

        return {
            codigo_produto: obterCampo(formulario, "codigo_produto").value.trim(),
            nome: obterCampo(formulario, "nome").value.trim(),
            categoria: obterCampo(formulario, "categoria").value.trim(),
            descricao: obterCampo(formulario, "descricao").value.trim(),
            preco_centavos: Math.round(numero("preco") * 100),
            quantidade_estoque: numero("quantidade_estoque"),
            estoque_minimo: numero("estoque_minimo"),
            estoque_maximo: numero("estoque_maximo"),
            validade: validade || null,
            foto_caminho: foto || null,
            zero_lactose: obterCampo(formulario, "zero_lactose").checked,
            zero_acucar: obterCampo(formulario, "zero_acucar").checked,
        };
    }

    function preencherFormulario(formulario, produto) {
        formulario.reset();
        obterCampo(formulario, "codigo_produto").value = produto.codigo_produto;
        obterCampo(formulario, "nome").value = produto.nome;
        obterCampo(formulario, "categoria").value = produto.categoria;
        obterCampo(formulario, "descricao").value = produto.descricao || "";
        obterCampo(formulario, "preco").value = (produto.preco_centavos / 100).toFixed(2);
        obterCampo(formulario, "quantidade_estoque").value = produto.quantidade_estoque;
        obterCampo(formulario, "estoque_minimo").value = produto.estoque_minimo;
        obterCampo(formulario, "estoque_maximo").value = produto.estoque_maximo;
        obterCampo(formulario, "validade").value = produto.validade || "";
        obterCampo(formulario, "foto_caminho").value = produto.foto_caminho || "";
        obterCampo(formulario, "zero_lactose").checked = produto.zero_lactose;
        obterCampo(formulario, "zero_acucar").checked = produto.zero_acucar;
    }

    async function enviarFormulario(evento, formulario, metodo, idProduto = null) {
        evento.preventDefault();
        limparErrosFormulario(formulario);
        mostrarMensagem(mensagemApi, "");

        if (!formulario.reportValidity()) return;

        const botaoEnviar = formulario.querySelector("button[type='submit']");
        botaoEnviar.disabled = true;
        try {
            await requisitar(idProduto ? API_URL + "/" + idProduto : API_URL, {
                method: metodo,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(montarPayload(formulario)),
            });
            fecharModal(idProduto ? modalEdicao : modalCadastro);
            formulario.reset();
            await carregarProdutos();
            mostrarMensagem(
                mensagemApi,
                metodo === "POST" ? "Produto cadastrado." : "Produto atualizado.",
                "sucesso",
            );
        } catch (erro) {
            if (Object.keys(erro.campos || {}).length) {
                exibirErrosFormulario(formulario, erro.campos);
            } else {
                formulario.querySelector(".feedback-form").textContent = erro.message;
            }
        } finally {
            botaoEnviar.disabled = false;
        }
    }

    function abrirCadastro() {
        formularioCadastro.reset();
        limparErrosFormulario(formularioCadastro);
        abrirModal(modalCadastro, obterCampo(formularioCadastro, "codigo_produto"));
    }

    document.getElementById("abrir-cadastro-produto").addEventListener("click", abrirCadastro);
    document.getElementById("abrir-cadastro-produto-topo").addEventListener("click", abrirCadastro);

    filtrosStatus.forEach((botao) => {
        botao.addEventListener("click", () => {
            filtroAtual = botao.dataset.filtroStatus;
            estoqueBaixoAtivo = false;
            const filtroEstoque = document.getElementById("filtrar-estoque-baixo");
            filtroEstoque.setAttribute("aria-pressed", "false");
            filtroEstoque.classList.remove("ativo");
            filtrosStatus.forEach((item) => {
                const selecionado = item === botao;
                item.classList.toggle("selecionado", selecionado);
                item.setAttribute("aria-pressed", String(selecionado));
            });
            renderizarProdutos();
        });
    });

    buscaProdutos.addEventListener("input", renderizarProdutos);

    document.getElementById("filtrar-estoque-baixo").addEventListener("click", (evento) => {
        estoqueBaixoAtivo = !estoqueBaixoAtivo;
        evento.currentTarget.setAttribute("aria-pressed", String(estoqueBaixoAtivo));
        evento.currentTarget.classList.toggle("ativo", estoqueBaixoAtivo);
        if (estoqueBaixoAtivo) {
            filtroAtual = "ATIVO";
            filtrosStatus.forEach((botao) => {
                const selecionado = botao.dataset.filtroStatus === "ATIVO";
                botao.classList.toggle("selecionado", selecionado);
                botao.setAttribute("aria-pressed", String(selecionado));
            });
        }
        renderizarProdutos();
    });

    document.getElementById("alternar-menu").addEventListener("click", (evento) => {
        const recolhido = document.getElementById("menu-admin").classList.toggle("recolhido");
        document.querySelector(".layout-admin").classList.toggle("menu-recolhido", recolhido);
        evento.currentTarget.setAttribute("aria-expanded", String(!recolhido));
        evento.currentTarget.textContent = recolhido ? "Expandir" : "Recolher";
    });
    document.getElementById("fechar-cadastro-produto").addEventListener("click", () => fecharModal(modalCadastro));
    document.getElementById("fechar-editar-produto").addEventListener("click", () => fecharModal(modalEdicao));
    document.getElementById("fechar-excluir-produto").addEventListener("click", () => fecharModal(modalExclusao));

    formularioCadastro.addEventListener("submit", (evento) => {
        enviarFormulario(evento, formularioCadastro, "POST");
    });

    formularioEdicao.addEventListener("submit", (evento) => {
        if (produtoSelecionado) {
            enviarFormulario(evento, formularioEdicao, "PUT", produtoSelecionado.id_produto);
        } else {
            evento.preventDefault();
        }
    });

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

        if (botao.dataset.acao === "inativar" || botao.dataset.acao === "excluir") {
            produtoSelecionado = produto;
            acaoConfirmacao = botao.dataset.acao === "excluir" ? "EXCLUIR" : "INATIVAR";
            const excluirDefinitivamente = acaoConfirmacao === "EXCLUIR";
            tituloConfirmacao.textContent = excluirDefinitivamente
                ? "Excluir produto definitivamente"
                : "Inativar produto";
            textoConfirmacao.textContent = excluirDefinitivamente
                ? `Deseja excluir "${produto.nome}"? O produto sairá do banco; o histórico de auditoria será mantido e não será possível reativá-lo.`
                : `Deseja inativar "${produto.nome}"? Ele sairá do catálogo, mas continuará salvo e poderá ser reativado.`;
            botaoConfirmarExclusao.textContent = excluirDefinitivamente
                ? "Excluir definitivamente"
                : "Inativar produto";
            botaoConfirmarExclusao.classList.toggle(
                "botao-exclusao-definitiva",
                excluirDefinitivamente,
            );
            abrirModal(modalExclusao);
            return;
        }

        if (botao.dataset.acao === "reativar") {
            botao.disabled = true;
            try {
                await requisitar(API_URL + "/" + produto.id_produto + "/reativar", { method: "PATCH" });
                await carregarProdutos();
                mostrarMensagem(mensagemApi, "Produto reativado.", "sucesso");
            } catch (erro) {
                mostrarMensagem(mensagemApi, erro.message, "erro");
            } finally {
                botao.disabled = false;
            }
        }
    });

    botaoConfirmarExclusao.addEventListener("click", async () => {
        if (!produtoSelecionado) return;
        botaoConfirmarExclusao.disabled = true;
        try {
            const excluindoDefinitivamente = acaoConfirmacao === "EXCLUIR";
            const url = API_URL + "/" + produtoSelecionado.id_produto
                + (excluindoDefinitivamente ? "" : "/inativar");
            await requisitar(url, { method: excluindoDefinitivamente ? "DELETE" : "PATCH" });
            fecharModal(modalExclusao);
            produtoSelecionado = null;
            acaoConfirmacao = null;
            await carregarProdutos();
            buscaProdutos.focus({ preventScroll: true });
            mostrarMensagem(
                mensagemApi,
                excluindoDefinitivamente
                    ? "Produto excluído. O histórico de auditoria foi preservado."
                    : "Produto inativado.",
                "sucesso",
            );
        } catch (erro) {
            mostrarMensagem(mensagemApi, erro.message, "erro");
        } finally {
            botaoConfirmarExclusao.disabled = false;
        }
    });

    [modalCadastro, modalEdicao, modalExclusao].forEach((modal) => {
        modal.addEventListener("click", (evento) => {
            if (evento.target === modal) fecharModal(modal);
        });
    });

    document.addEventListener("keydown", (evento) => {
        const modalAberto = [modalCadastro, modalEdicao, modalExclusao]
            .find((modal) => modal.classList.contains("aberto"));
        if (!modalAberto) return;

        if (evento.key === "Escape") {
            evento.preventDefault();
            fecharModal(modalAberto);
            return;
        }

        if (evento.key !== "Tab") return;
        const focaveis = [...modalAberto.querySelectorAll(
            "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])",
        )].filter((elemento) => elemento.getClientRects().length > 0);
        if (!focaveis.length) {
            evento.preventDefault();
            modalAberto.focus();
            return;
        }

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

    carregarProdutos();
});
