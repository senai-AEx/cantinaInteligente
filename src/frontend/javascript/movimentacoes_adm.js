// Tela administrativa de movimentações financeiras: créditos declarados, débitos de
// compras e ajustes, com filtros por período, tipo e usuário, totais e impressão.
// Usa as funções compartilhadas do objeto Cantina (base.js).
document.addEventListener("DOMContentLoaded", async () => {
    "use strict";

    // Só administradores passam daqui: quem não está logado vai para o login e
    // quem não é administrador volta ao catálogo.
    const administrador = await Cantina.exigirAdministrador();

    const API = "/api/admin/movimentacoes";
    const LIMITE = 200;
    const DIAS_PADRAO = 30;
    const TIPOS = {
        CREDITO: { rotulo: "Crédito", classe: "etiqueta etiqueta-sucesso" },
        DEBITO: { rotulo: "Débito", classe: "etiqueta etiqueta-erro" },
        AJUSTE: { rotulo: "Ajuste", classe: "etiqueta" },
    };
    const NOMES_FILTRO_TIPO = { TODOS: "Todos", CREDITO: "Créditos", DEBITO: "Compras/Débitos", AJUSTE: "Ajustes" };
    const el = Cantina.criarElemento;

    const formulario = document.getElementById("form-filtros");
    const campoDe = document.getElementById("filtro-de");
    const campoAte = document.getElementById("filtro-ate");
    const campoTipo = document.getElementById("filtro-tipo");
    const campoUsuario = document.getElementById("filtro-usuario");
    const textoFiltros = document.getElementById("texto-filtros-aplicados");
    const contador = document.getElementById("contador-movimentacoes");
    const estadoLista = document.getElementById("estado-movimentacoes");
    const areaTabela = document.getElementById("area-tabela-movimentacoes");
    const corpoTabela = document.getElementById("corpo-tabela-movimentacoes");
    const totalCreditos = document.getElementById("total-creditos");
    const totalDebitos = document.getElementById("total-debitos");
    const totalAjustes = document.getElementById("total-ajustes");

    let filtrosAplicados = null;
    let ultimoPedido = 0;

    // ---------- datas (o período da API usa datas de Brasília, AAAA-MM-DD) ----------

    function hojeEmBrasilia() {
        const partes = new Intl.DateTimeFormat("en-CA", {
            timeZone: "America/Sao_Paulo",
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
        }).formatToParts(new Date());
        const parte = (tipo) => partes.find((item) => item.type === tipo).value;
        return `${parte("year")}-${parte("month")}-${parte("day")}`;
    }

    function somarDias(dataIso, dias) {
        const [ano, mes, dia] = dataIso.split("-").map(Number);
        return new Date(Date.UTC(ano, mes - 1, dia + dias)).toISOString().slice(0, 10);
    }

    function dataValida(texto) {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(texto || "")) return false;
        const [ano, mes, dia] = texto.split("-").map(Number);
        const data = new Date(Date.UTC(ano, mes - 1, dia));
        return data.getUTCFullYear() === ano && data.getUTCMonth() === mes - 1 && data.getUTCDate() === dia;
    }

    // "2026-11-17" -> "17/11/2026" (sem converter fuso: é só uma data).
    function formatarDia(dataIso) {
        if (!dataValida(dataIso)) return dataIso || "";
        const [ano, mes, dia] = dataIso.split("-");
        return `${dia}/${mes}/${ano}`;
    }

    // ---------- utilitários ----------

    function valorComSinal(centavos) {
        const texto = Cantina.formatarPreco(Math.abs(centavos));
        if (centavos > 0) return "+ " + texto;
        if (centavos < 0) return "− " + texto;
        return texto;
    }

    // Valor com sinal e cor; o sinal garante a leitura mesmo sem distinguir as cores.
    function definirTotal(elemento, centavos) {
        const valor = Number(centavos || 0);
        elemento.textContent = valorComSinal(valor);
        elemento.classList.toggle("valor-positivo", valor > 0);
        elemento.classList.toggle("valor-negativo", valor < 0);
    }

    function limparTotais() {
        [totalCreditos, totalDebitos, totalAjustes].forEach((elemento) => {
            elemento.textContent = "—";
            elemento.classList.remove("valor-positivo", "valor-negativo");
        });
    }

    function tratarErro(erro) {
        if (erro.status === 401) {
            Cantina.irParaLogin();
            return "Sua sessão terminou. Abrindo a tela de login…";
        }
        if (erro.status === 403) {
            return "Sua conta não tem permissão de administrador para ver as movimentações.";
        }
        return erro.message;
    }

    function celula(conteudo, classe = "") {
        const elemento = document.createElement("td");
        if (classe) elemento.className = classe;
        if (conteudo instanceof Node) elemento.append(conteudo);
        else elemento.textContent = conteudo ?? "";
        return elemento;
    }

    // ---------- menu lateral ----------

    document.getElementById("alternar-menu").addEventListener("click", (evento) => {
        const recolhido = document.getElementById("menu-admin").classList.toggle("recolhido");
        document.querySelector(".layout-admin").classList.toggle("menu-recolhido", recolhido);
        evento.currentTarget.setAttribute("aria-expanded", String(!recolhido));
        evento.currentTarget.textContent = recolhido ? "Expandir menu" : "Recolher menu";
    });

    // ---------- filtros ----------

    function filtrosPadrao() {
        const hoje = hojeEmBrasilia();
        return { de: somarDias(hoje, -(DIAS_PADRAO - 1)), ate: hoje, tipo: "TODOS", id_usuario: "" };
    }

    // O link da tela de Usuários chega com ?id_usuario=; os demais filtros também valem na URL.
    function filtrosDaUrl() {
        const parametros = new URLSearchParams(window.location.search);
        const filtros = filtrosPadrao();
        if (dataValida(parametros.get("de"))) filtros.de = parametros.get("de");
        if (dataValida(parametros.get("ate"))) filtros.ate = parametros.get("ate");
        const tipo = (parametros.get("tipo") || "").toUpperCase();
        if (tipo in NOMES_FILTRO_TIPO) filtros.tipo = tipo;
        const idUsuario = parametros.get("id_usuario") || "";
        if (/^[1-9]\d{0,9}$/.test(idUsuario)) filtros.id_usuario = idUsuario;
        return filtros;
    }

    function garantirOpcaoDeUsuario(idUsuario) {
        const existe = [...campoUsuario.options].some((opcao) => opcao.value === String(idUsuario));
        if (!existe) campoUsuario.add(new Option(`Usuário nº ${idUsuario}`, String(idUsuario)));
    }

    function preencherCampos(filtros) {
        campoDe.value = filtros.de;
        campoAte.value = filtros.ate;
        campoTipo.value = filtros.tipo;
        if (filtros.id_usuario) garantirOpcaoDeUsuario(filtros.id_usuario);
        campoUsuario.value = filtros.id_usuario;
    }

    function validarFiltros(filtros) {
        const erros = {};
        if (!dataValida(filtros.de)) erros.de = "Informe a data inicial.";
        if (!dataValida(filtros.ate)) erros.ate = "Informe a data final.";
        if (!erros.de && !erros.ate && filtros.de > filtros.ate) {
            erros.de = "A data inicial não pode ser depois da data final.";
        }
        return erros;
    }

    function rotuloDoUsuarioFiltrado(idUsuario) {
        if (!idUsuario) return "Todos os usuários";
        const opcao = [...campoUsuario.options].find((item) => item.value === String(idUsuario));
        return opcao ? opcao.textContent : `Usuário nº ${idUsuario}`;
    }

    // Texto que acompanha os totais na tela e no papel.
    function descreverFiltros(periodo) {
        if (!filtrosAplicados) return;
        const de = periodo?.de || filtrosAplicados.de;
        const ate = periodo?.ate || filtrosAplicados.ate;
        textoFiltros.textContent = `Período: ${formatarDia(de)} a ${formatarDia(ate)} · `
            + `Tipo: ${NOMES_FILTRO_TIPO[filtrosAplicados.tipo]} · `
            + `Usuário: ${rotuloDoUsuarioFiltrado(filtrosAplicados.id_usuario)}`;
    }

    // Mantém na URL os filtros diferentes do padrão: recarregar a página (ou voltar do
    // login) preserva a consulta, e a visão padrão continua sendo "últimos 30 dias".
    function atualizarUrl() {
        const padrao = filtrosPadrao();
        const parametros = new URLSearchParams();
        if (filtrosAplicados.de !== padrao.de || filtrosAplicados.ate !== padrao.ate) {
            parametros.set("de", filtrosAplicados.de);
            parametros.set("ate", filtrosAplicados.ate);
        }
        if (filtrosAplicados.tipo !== padrao.tipo) parametros.set("tipo", filtrosAplicados.tipo);
        if (filtrosAplicados.id_usuario) parametros.set("id_usuario", filtrosAplicados.id_usuario);
        const consulta = parametros.toString();
        window.history.replaceState(null, "", window.location.pathname + (consulta ? `?${consulta}` : ""));
    }

    function aplicarFiltros() {
        Cantina.limparErros(formulario);
        const filtros = {
            de: campoDe.value,
            ate: campoAte.value,
            tipo: campoTipo.value,
            id_usuario: campoUsuario.value,
        };
        if (Cantina.exibirErros(formulario, validarFiltros(filtros))) return;
        filtrosAplicados = filtros;
        atualizarUrl();
        carregar();
    }

    // Lista de usuários para o filtro. Se falhar, o filtro pelo link continua funcionando.
    async function carregarOpcoesDeUsuario() {
        try {
            const resultado = await Cantina.requisitar("/api/admin/usuarios?status=TODOS&perfil=TODOS");
            const selecionado = campoUsuario.value;
            const opcoes = (resultado.usuarios || []).map((usuario) => {
                const inativo = usuario.status === "INATIVO" ? " (inativo)" : "";
                return new Option(`${usuario.nome} — matrícula ${usuario.matricula}${inativo}`, String(usuario.id_usuario));
            });
            campoUsuario.replaceChildren(new Option("Todos os usuários", ""), ...opcoes);
            if (selecionado) garantirOpcaoDeUsuario(selecionado);
            campoUsuario.value = selecionado;
            descreverFiltros();
        } catch {
            // Sem a lista, o campo fica só com "Todos os usuários" e o usuário vindo do link.
        }
    }

    // ---------- listagem ----------

    // Estado da lista: carregando, vazio ou erro (com botão para tentar de novo).
    function mostrarEstado(texto, { erro = false, aoTentar = null } = {}) {
        estadoLista.replaceChildren(el("p", "", texto));
        estadoLista.classList.toggle("estado-erro", erro);
        if (aoTentar) {
            const botao = el("button", "botao botao-secundario nao-imprimir", "Tentar novamente");
            botao.type = "button";
            botao.addEventListener("click", aoTentar);
            estadoLista.append(botao);
        }
        estadoLista.hidden = false;
        areaTabela.hidden = true;
    }

    function mostrarTabela() {
        estadoLista.hidden = true;
        estadoLista.replaceChildren();
        areaTabela.hidden = false;
    }

    function criarLinha(movimentacao) {
        const linha = document.createElement("tr");
        const tipo = TIPOS[movimentacao.tipo] || { rotulo: movimentacao.tipo || "—", classe: "etiqueta" };
        const usuario = movimentacao.usuario || {};
        const valor = Number(movimentacao.valor_centavos || 0);

        const celulaUsuario = celula("");
        celulaUsuario.append(el("span", "nome-usuario", usuario.nome || "Usuário não identificado"));
        if (usuario.matricula) {
            celulaUsuario.append(el("span", "texto-secundario", `Matrícula ${usuario.matricula}`));
        }

        let classeValor = "numero";
        if (valor > 0) classeValor += " valor-positivo";
        else if (valor < 0) classeValor += " valor-negativo";

        linha.append(
            celula(Cantina.formatarDataHora(movimentacao.data_hora), "celula-data"),
            celulaUsuario,
            celula(el("span", tipo.classe, tipo.rotulo)),
            celula(movimentacao.descricao || "—", "texto-quebravel"),
            celula(valorComSinal(valor), classeValor),
            celula(Cantina.formatarPreco(movimentacao.saldo_apos_centavos), "numero"),
        );
        return linha;
    }

    function renderizar(resultado) {
        const movimentacoes = resultado.movimentacoes || [];
        const totais = resultado.totais || {};
        definirTotal(totalCreditos, totais.creditos_centavos);
        definirTotal(totalDebitos, totais.debitos_centavos);
        definirTotal(totalAjustes, totais.ajustes_centavos);
        descreverFiltros(resultado.periodo);

        if (!movimentacoes.length) {
            corpoTabela.replaceChildren();
            contador.textContent = "Nenhuma movimentação encontrada.";
            mostrarEstado("Não há movimentações neste período com esses filtros.");
            return;
        }

        corpoTabela.replaceChildren(...movimentacoes.map(criarLinha));
        contador.textContent = movimentacoes.length >= LIMITE
            ? `A lista mostra ${LIMITE} movimentações (o limite da tela). Os totais consideram todo o período; reduza o período ou filtre para ver as demais.`
            : `${movimentacoes.length} ${movimentacoes.length === 1 ? "movimentação encontrada." : "movimentações encontradas."}`;
        mostrarTabela();
    }

    async function carregar() {
        const pedido = ++ultimoPedido;
        const filtros = filtrosAplicados;
        const parametros = new URLSearchParams({
            de: filtros.de,
            ate: filtros.ate,
            tipo: filtros.tipo,
            limite: String(LIMITE),
        });
        if (filtros.id_usuario) parametros.set("id_usuario", filtros.id_usuario);

        mostrarEstado("Carregando movimentações…");
        contador.textContent = "";
        limparTotais();
        descreverFiltros();

        try {
            const resultado = await Cantina.requisitar(`${API}?${parametros}`);
            if (pedido !== ultimoPedido) return; // chegou uma consulta mais nova
            renderizar(resultado);
        } catch (erro) {
            if (pedido !== ultimoPedido) return;
            // 422: a API recusou algum filtro; a mensagem vai para junto do campo.
            const camposInvalidos = Object.keys(erro.campos || {}).length > 0;
            if (camposInvalidos) Cantina.exibirErros(formulario, erro.campos);
            mostrarEstado(tratarErro(erro), { erro: true, aoTentar: camposInvalidos ? null : carregar });
        }
    }

    // ---------- eventos ----------

    Cantina.ligarLimpezaDeErros(formulario);

    // É uma consulta (nada é gravado): vale o botão "Aplicar filtros" ou Enter em um campo.
    formulario.addEventListener("submit", (evento) => {
        evento.preventDefault();
        aplicarFiltros();
    });

    document.getElementById("limpar-filtros").addEventListener("click", () => {
        preencherCampos(filtrosPadrao());
        aplicarFiltros();
        campoDe.focus();
    });

    // Impressão: sai só o conteúdo (totais e lançamentos), com o período e a data de emissão.
    window.addEventListener("beforeprint", () => {
        document.getElementById("texto-emissao").textContent =
            `Emitido em ${Cantina.formatarDataHora(new Date().toISOString())} por ${administrador.nome}.`;
    });

    document.getElementById("botao-imprimir").addEventListener("click", () => window.print());

    // ---------- início ----------

    preencherCampos(filtrosDaUrl());
    carregarOpcoesDeUsuario();
    aplicarFiltros();
});
