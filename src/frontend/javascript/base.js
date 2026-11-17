// Funções compartilhadas por todas as telas: chamadas à API, sessão de login,
// cabeçalho/rodapé, máscaras, validações e mensagens de erro dos formulários.
// Tudo fica no objeto global `Cantina`. Carregue este arquivo antes do script da tela.
(function () {
    "use strict";

    const Cantina = {};
    let promessaSessao = null;
    let promessaLayout = null;

    // ---------- API ----------

    // Uso: await Cantina.requisitar("/api/compras", { method: "POST", json: {...} })
    // Em erro, lança Error com: status, campos ({campo: mensagem}), codigo e detalhes.
    Cantina.requisitar = async function (url, opcoes = {}) {
        const { json, headers, ...resto } = opcoes;
        const cabecalhos = { Accept: "application/json", ...(headers || {}) };
        if (json !== undefined) {
            cabecalhos["Content-Type"] = "application/json";
            resto.body = JSON.stringify(json);
        }

        let resposta;
        try {
            resposta = await fetch(url, { credentials: "same-origin", ...resto, headers: cabecalhos });
        } catch {
            const erro = new Error("Não foi possível falar com o servidor. Confira se o sistema está ligado.");
            erro.status = 0;
            erro.campos = {};
            throw erro;
        }

        let resultado = {};
        try {
            resultado = await resposta.json();
        } catch {
            resultado = {};
        }

        if (!resposta.ok) {
            const erro = new Error(resultado.erro || "Não foi possível concluir a operação.");
            erro.status = resposta.status;
            erro.campos = resultado.campos || {};
            erro.codigo = resultado.codigo || null;
            erro.detalhes = resultado.detalhes || null;
            throw erro;
        }
        return resultado;
    };

    // ---------- sessão ----------

    // Promise com o usuário logado ({id_usuario, nome, perfil, saldo_centavos, ...}) ou null.
    Cantina.sessao = function () {
        if (!promessaSessao) {
            promessaSessao = Cantina.requisitar("/api/auth/eu")
                .then((resultado) => resultado.usuario || null)
                .catch(() => null);
        }
        return promessaSessao;
    };

    // Relê o usuário no servidor e redesenha o cabeçalho (use após login, crédito ou compra).
    Cantina.atualizarSessao = async function () {
        promessaSessao = null;
        const usuario = await Cantina.sessao();
        renderizarCabecalho(usuario);
        return usuario;
    };

    // Aceita apenas caminhos internos ("/html/..."), para não redirecionar a outros sites.
    Cantina.destinoSeguro = function (destino, padrao) {
        if (typeof destino === "string" && destino.startsWith("/") && !destino.startsWith("//") && !destino.includes("\\")) {
            return destino;
        }
        return padrao;
    };

    Cantina.irParaLogin = function () {
        const destino = window.location.pathname + window.location.search;
        window.location.href = "/html/login.html?destino=" + encodeURIComponent(destino);
    };

    // Use no início das telas que exigem login. Quem não está logado vai para o login.
    Cantina.exigirLogin = async function () {
        const usuario = await Cantina.sessao();
        if (!usuario) {
            Cantina.irParaLogin();
            return new Promise(() => {});
        }
        return usuario;
    };

    // Use no início das telas administrativas.
    Cantina.exigirAdministrador = async function () {
        const usuario = await Cantina.exigirLogin();
        if (usuario.perfil !== "ADMINISTRADOR") {
            window.location.href = "/html/catalogo_produtos.html?aviso=sem-permissao";
            return new Promise(() => {});
        }
        return usuario;
    };

    Cantina.sair = async function () {
        try {
            await Cantina.requisitar("/api/auth/logout", { method: "POST" });
        } finally {
            // Em computador compartilhado, a sacola de quem saiu não fica para o próximo.
            try {
                window.localStorage.removeItem("cantina-sacola-v1");
                window.sessionStorage.removeItem("cantina-compra-pendente-v1");
            } catch { /* armazenamento indisponível: nada a limpar */ }
            window.location.href = "/";
        }
    };

    // ---------- formatação ----------

    Cantina.formatarPreco = function (centavos) {
        return (Number(centavos || 0) / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    };

    Cantina.centavosParaTexto = function (centavos) {
        return (Number(centavos || 0) / 100).toLocaleString("pt-BR", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    };

    Cantina.textoParaCentavos = function (texto) {
        const digitos = String(texto ?? "").replace(/\D/g, "");
        return digitos ? Number(digitos) : 0;
    };

    // A API envia datas em UTC ("2026-11-17T22:48:21Z"); a tela mostra no horário local.
    Cantina.formatarDataHora = function (iso) {
        if (!iso) return "";
        const data = new Date(iso);
        if (Number.isNaN(data.getTime())) return "";
        return data.toLocaleString("pt-BR", { dateStyle: "short", timeStyle: "short" });
    };

    Cantina.formatarData = function (iso) {
        if (!iso) return "";
        const data = new Date(iso);
        if (Number.isNaN(data.getTime())) return "";
        return data.toLocaleDateString("pt-BR");
    };

    // Identificador único de uma operação (compra, crédito): reenviar não duplica.
    Cantina.novaChave = function () {
        if (window.crypto?.randomUUID) return window.crypto.randomUUID();
        return "xxxxxxxx-xxxx-4xxx-8xxx-xxxxxxxxxxxx".replace(/x/g, () => Math.floor(Math.random() * 16).toString(16));
    };

    // ---------- máscaras e validações ----------

    Cantina.somenteDigitos = function (texto) {
        return String(texto ?? "").replace(/\D/g, "");
    };

    // Moeda: o usuário digita só números e o campo mostra "1.234,56".
    Cantina.aplicarMascaraMoeda = function (campo) {
        const digitos = Cantina.somenteDigitos(campo.value).replace(/^0+/, "").slice(0, 9);
        campo.value = digitos ? Cantina.centavosParaTexto(Number(digitos)) : "";
    };

    Cantina.ligarMascaraMoeda = function (campo) {
        campo.addEventListener("input", () => Cantina.aplicarMascaraMoeda(campo));
    };

    Cantina.mascaraCpf = function (texto) {
        const d = Cantina.somenteDigitos(texto).slice(0, 11);
        if (d.length <= 3) return d;
        if (d.length <= 6) return `${d.slice(0, 3)}.${d.slice(3)}`;
        if (d.length <= 9) return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6)}`;
        return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6, 9)}-${d.slice(9)}`;
    };

    Cantina.ligarMascaraCpf = function (campo) {
        campo.addEventListener("input", () => { campo.value = Cantina.mascaraCpf(campo.value); });
    };

    // Deixa o campo aceitar apenas números (matrícula, quantidade).
    Cantina.ligarSomenteDigitos = function (campo, maximo = 20) {
        campo.addEventListener("input", () => { campo.value = Cantina.somenteDigitos(campo.value).slice(0, maximo); });
    };

    Cantina.validarCpf = function (texto) {
        const cpf = Cantina.somenteDigitos(texto);
        if (cpf.length !== 11 || /^(\d)\1{10}$/.test(cpf)) return false;
        const digito = (tamanho) => {
            let soma = 0;
            for (let i = 0; i < tamanho; i += 1) soma += Number(cpf[i]) * (tamanho + 1 - i);
            const resto = (soma * 10) % 11;
            return resto === 10 ? 0 : resto;
        };
        return digito(9) === Number(cpf[9]) && digito(10) === Number(cpf[10]);
    };

    Cantina.validarEmail = function (texto) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(texto ?? "").trim());
    };

    // Regra de senha do sistema: 8 a 72 caracteres, com letra e número.
    Cantina.validarSenha = function (texto) {
        const senha = String(texto ?? "");
        return senha.length >= 8 && senha.length <= 72 && /[A-Za-zÀ-ÿ]/.test(senha) && /\d/.test(senha);
    };

    // ---------- elementos e mensagens ----------

    Cantina.criarElemento = function (tag, classe, texto) {
        const elemento = document.createElement(tag);
        if (classe) elemento.className = classe;
        if (texto !== undefined && texto !== null) elemento.textContent = texto;
        return elemento;
    };

    // Mostra texto em um elemento de aviso. tipo: "erro", "sucesso" ou "" (neutro).
    Cantina.mostrarMensagem = function (elemento, mensagem, tipo = "") {
        if (!elemento) return;
        elemento.textContent = mensagem || "";
        elemento.classList.toggle("mensagem-erro", tipo === "erro");
        elemento.classList.toggle("mensagem-sucesso", tipo === "sucesso");
    };

    // Formulários: cada campo tem <small class="erro-campo" data-error-for="nome_do_campo">
    // e o formulário tem <p class="feedback-form" role="alert"> para erros gerais.
    function mensagemDoCampo(formulario, nome) {
        return [...formulario.querySelectorAll("[data-error-for]")]
            .find((elemento) => elemento.dataset.errorFor === nome);
    }

    Cantina.limparErroCampo = function (formulario, nome) {
        const campo = formulario.elements.namedItem(nome);
        const mensagem = mensagemDoCampo(formulario, nome);
        if (campo && campo.removeAttribute) {
            campo.removeAttribute("aria-invalid");
            const descricoes = (campo.getAttribute("aria-describedby") || "")
                .split(/\s+/)
                .filter((id) => id && id !== mensagem?.id);
            if (descricoes.length) campo.setAttribute("aria-describedby", descricoes.join(" "));
            else campo.removeAttribute("aria-describedby");
        }
        if (mensagem) mensagem.textContent = "";
    };

    Cantina.limparErros = function (formulario) {
        formulario.querySelectorAll("[data-error-for]").forEach((mensagem) => {
            Cantina.limparErroCampo(formulario, mensagem.dataset.errorFor);
        });
        const feedback = formulario.querySelector(".feedback-form");
        if (feedback) feedback.textContent = "";
    };

    // erros: {campo: mensagem}. Campos sem lugar próprio vão para o .feedback-form.
    // Foca o primeiro campo com erro. Devolve true se havia algum erro.
    Cantina.exibirErros = function (formulario, erros) {
        const entradas = Object.entries(erros || {});
        const feedback = formulario.querySelector(".feedback-form");
        const gerais = [];
        entradas.forEach(([nome, texto]) => {
            const campo = formulario.elements.namedItem(nome);
            const mensagem = mensagemDoCampo(formulario, nome);
            if (campo && campo.setAttribute && campo.type !== "hidden" && mensagem) {
                if (!mensagem.id) mensagem.id = `${formulario.id || "form"}-erro-${nome}`;
                campo.setAttribute("aria-invalid", "true");
                const descricoes = new Set((campo.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean));
                descricoes.add(mensagem.id);
                campo.setAttribute("aria-describedby", [...descricoes].join(" "));
                mensagem.textContent = texto;
            } else {
                gerais.push(texto);
            }
        });
        if (feedback && entradas.length) {
            feedback.textContent = ["Revise os campos destacados.", ...gerais].join(" ");
        }
        formulario.querySelector("[aria-invalid='true']")?.focus();
        return entradas.length > 0;
    };

    // Limpa o erro de cada campo assim que o usuário volta a digitar nele.
    Cantina.ligarLimpezaDeErros = function (formulario) {
        formulario.querySelectorAll("[data-error-for]").forEach((mensagem) => {
            const campo = formulario.elements.namedItem(mensagem.dataset.errorFor);
            if (!campo || !campo.addEventListener) return;
            const limpar = () => Cantina.limparErroCampo(formulario, mensagem.dataset.errorFor);
            campo.addEventListener("input", limpar);
            campo.addEventListener("change", limpar);
        });
    };

    // Regra do sistema: o formulário só grava pelo clique no botão; Enter em um campo não envia.
    // Botões, links e caixas de seleção continuam funcionando com Enter pelo teclado.
    Cantina.bloquearEnvioPorEnter = function (formulario) {
        const tiposLivres = ["submit", "button", "reset", "file", "checkbox", "radio"];
        formulario.addEventListener("keydown", (evento) => {
            if (evento.key !== "Enter") return;
            const alvo = evento.target;
            const campoDeTexto = alvo.tagName === "INPUT" && !tiposLivres.includes(alvo.type);
            if (campoDeTexto || alvo.tagName === "SELECT") evento.preventDefault();
        });
    };

    // Desabilita o botão e troca o texto enquanto a função assíncrona roda.
    Cantina.comBotaoOcupado = async function (botao, textoOcupado, funcao) {
        const textoOriginal = botao.textContent;
        botao.disabled = true;
        botao.textContent = textoOcupado;
        try {
            return await funcao();
        } finally {
            botao.disabled = false;
            botao.textContent = textoOriginal;
        }
    };

    // ---------- cabeçalho e rodapé ----------

    // No base.html, cada item do menu tem data-visivel = "sempre", "anonimo", "logado" ou "admin".
    function renderizarCabecalho(usuario) {
        const admin = Boolean(usuario) && usuario.perfil === "ADMINISTRADOR";
        document.querySelectorAll("[data-visivel]").forEach((item) => {
            const regra = item.dataset.visivel;
            const mostrar = regra === "sempre"
                || (regra === "anonimo" && !usuario)
                || (regra === "logado" && Boolean(usuario))
                || (regra === "admin" && admin);
            item.hidden = !mostrar;
        });
        document.querySelectorAll("[data-usuario-nome]").forEach((item) => {
            item.textContent = usuario ? usuario.nome.trim().split(/\s+/)[0] : "";
        });
        Cantina.atualizarSaldoCabecalho(usuario ? usuario.saldo_centavos : null);
    }

    // Atualiza o saldo mostrado no cabeçalho sem nova consulta ao servidor.
    Cantina.atualizarSaldoCabecalho = function (saldoCentavos) {
        document.querySelectorAll("[data-usuario-saldo]").forEach((item) => {
            item.textContent = saldoCentavos === null || saldoCentavos === undefined
                ? ""
                : Cantina.formatarPreco(saldoCentavos);
        });
    };

    async function carregarLayout() {
        const localHeader = document.getElementById("header-container");
        const localFooter = document.getElementById("footer-container");
        if (localHeader || localFooter) {
            try {
                const resposta = await fetch("/html/base.html");
                if (!resposta.ok) throw new Error("Não foi possível carregar o base.html");
                const documento = new DOMParser().parseFromString(await resposta.text(), "text/html");
                const pular = documento.querySelector(".pular-conteudo");
                const header = documento.querySelector("header");
                const footer = documento.querySelector("footer");
                if (header && localHeader) {
                    localHeader.replaceWith(header);
                    if (pular && document.querySelector("main")) {
                        const principal = document.querySelector("main");
                        if (!principal.id) principal.id = "conteudo-principal";
                        pular.setAttribute("href", "#" + principal.id);
                        document.body.prepend(pular);
                    }
                }
                if (footer && localFooter) localFooter.replaceWith(footer);
            } catch (erro) {
                console.error("Erro ao carregar cabeçalho e rodapé:", erro);
            }
        }

        document.addEventListener("click", (evento) => {
            if (evento.target.closest("[data-acao='sair']")) {
                evento.preventDefault();
                Cantina.sair();
            }
        });

        const usuario = await Cantina.sessao();
        renderizarCabecalho(usuario);
        // Evento antigo, mantido para as telas que já o escutam.
        document.dispatchEvent(new Event("layoutbase:carregada"));
        document.dispatchEvent(new CustomEvent("cantina:pronta", { detail: { usuario } }));
        return usuario;
    }

    // Promise resolvida quando cabeçalho e sessão estão prontos; devolve o usuário ou null.
    Cantina.pronta = function () {
        if (!promessaLayout) promessaLayout = carregarLayout();
        return promessaLayout;
    };

    window.Cantina = Cantina;

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", () => Cantina.pronta());
    } else {
        Cantina.pronta();
    }
})();
