// Tela administrativa de relatórios: vendas, compras registradas (quem comprou o quê),
// saldos, estoque e depósitos declarados, em abas, com seletor de período e impressão
// do relatório visível.
// Usa as funções compartilhadas do objeto Cantina (base.js).
document.addEventListener("DOMContentLoaded", async () => {
    "use strict";

    // Só administradores passam daqui: quem não está logado vai para o login e
    // quem não é administrador volta ao catálogo.
    const administrador = await Cantina.exigirAdministrador();

    const DIAS_PADRAO = 30;
    const LIMITE_DEPOSITOS = 200;
    const LIMITE_COMPRAS = 200;
    const el = Cantina.criarElemento;

    const formularioPeriodo = document.getElementById("form-periodo");
    const campoDe = document.getElementById("periodo-de");
    const campoAte = document.getElementById("periodo-ate");
    const botoesAtalho = [...document.querySelectorAll("[data-atalho-dias]")];
    const listaDeAbas = document.getElementById("abas-relatorios");
    const abas = [...listaDeAbas.querySelectorAll("[role='tab']")];
    const formularioCompras = document.getElementById("form-compras");
    const filtroUsuarioCompras = document.getElementById("compras-usuario");

    // Cada relatório: se depende do período, de onde vem e como é desenhado.
    // Opcionais: "formulario" e "filtro" (filtro próprio da aba, que entra na consulta),
    // "descricaoExtra" (complemento da linha de período) e "aoAbrir" (ao abrir a aba).
    const RELATORIOS = {
        vendas: {
            usaPeriodo: true,
            url: (periodo) => `/api/admin/relatorios/vendas?${new URLSearchParams(periodo)}`,
            renderizar: renderizarVendas,
        },
        compras: {
            usaPeriodo: true,
            formulario: formularioCompras,
            filtro: () => filtroUsuarioCompras.value,
            url: (periodo) => {
                const parametros = new URLSearchParams({ ...periodo, limite: String(LIMITE_COMPRAS) });
                if (filtroUsuarioCompras.value) parametros.set("id_usuario", filtroUsuarioCompras.value);
                return `/api/admin/compras?${parametros}`;
            },
            descricaoExtra: () => (filtroUsuarioCompras.value ? ` · Usuário: ${rotuloDoUsuarioFiltrado()}` : ""),
            aoAbrir: carregarOpcoesDeUsuario,
            renderizar: renderizarCompras,
        },
        saldos: {
            usaPeriodo: false,
            url: () => "/api/admin/relatorios/saldos",
            renderizar: renderizarSaldos,
        },
        estoque: {
            usaPeriodo: false,
            url: () => "/api/admin/relatorios/estoque",
            renderizar: renderizarEstoque,
        },
        depositos: {
            usaPeriodo: true,
            url: (periodo) => `/api/admin/movimentacoes?${new URLSearchParams({ tipo: "CREDITO", ...periodo, limite: String(LIMITE_DEPOSITOS) })}`,
            renderizar: renderizarDepositos,
        },
    };

    // Controle de carga por relatório: o que já foi buscado e qual foi o último pedido.
    const controles = {};
    Object.keys(RELATORIOS).forEach((nome) => { controles[nome] = { chave: null, pedido: 0 }; });

    let periodo = null; // { de: "AAAA-MM-DD", ate: "AAAA-MM-DD" } aplicado
    let relatorioAtivo = "vendas";
    let opcoesDeUsuario = "pendentes"; // "pendentes", "carregando" ou "prontas" (filtro da aba Compras)

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

    // Últimos N dias, incluindo hoje.
    function periodoDosUltimosDias(dias) {
        const hoje = hojeEmBrasilia();
        return { de: somarDias(hoje, -(dias - 1)), ate: hoje };
    }

    // ---------- utilitários ----------

    const preco = Cantina.formatarPreco;

    function inteiro(valor) {
        return Number(valor || 0).toLocaleString("pt-BR");
    }

    function definirTexto(id, texto) {
        document.getElementById(id).textContent = texto;
    }

    function tratarErro(erro) {
        if (erro.status === 401) {
            Cantina.irParaLogin();
            return "Sua sessão terminou. Abrindo a tela de login…";
        }
        if (erro.status === 403) {
            return "Sua conta não tem permissão de administrador para ver os relatórios.";
        }
        return erro.message;
    }

    function celula(conteudo, classe = "", cabecalhoDeLinha = false) {
        const elemento = document.createElement(cabecalhoDeLinha ? "th" : "td");
        if (cabecalhoDeLinha) elemento.scope = "row";
        if (classe) elemento.className = classe;
        if (conteudo instanceof Node) elemento.append(conteudo);
        else elemento.textContent = conteudo ?? "";
        return elemento;
    }

    function linha(celulas, classe = "") {
        const elemento = document.createElement("tr");
        if (classe) elemento.className = classe;
        elemento.append(...celulas);
        return elemento;
    }

    // Preenche o <tbody>; sem itens, mostra uma linha única com o texto de lista vazia.
    function preencherTabela(idCorpo, itens, colunas, textoVazio, criarLinha) {
        const corpo = document.getElementById(idCorpo);
        const lista = itens || [];
        if (!lista.length) {
            const vazia = celula(textoVazio, "celula-vazia");
            vazia.colSpan = colunas;
            corpo.replaceChildren(linha([vazia]));
            return;
        }
        corpo.replaceChildren(...lista.map(criarLinha));
    }

    function etiquetaDeSituacao(status) {
        const ativo = status === "ATIVO";
        return el("span", ativo ? "etiqueta etiqueta-sucesso" : "etiqueta etiqueta-erro", ativo ? "Ativo" : "Inativo");
    }

    // Barra horizontal proporcional ao maior valor da coluna. É decorativa
    // (aria-hidden): o número fica escrito ao lado.
    function criarBarra(centavos, maior) {
        const valor = Number(centavos || 0);
        const proporcao = maior > 0 ? Math.max(0, Math.min(100, (valor / maior) * 100)) : 0;
        const conjunto = el("div", "barra-linha");
        const trilho = el("span", "barra-trilho");
        trilho.setAttribute("aria-hidden", "true");
        const preenchimento = el("span", "barra-preenchimento");
        preenchimento.style.width = `${proporcao.toFixed(1)}%`;
        trilho.append(preenchimento);
        conjunto.append(trilho, el("span", "barra-valor", preco(valor)));
        return conjunto;
    }

    // ---------- menu lateral ----------

    document.getElementById("alternar-menu").addEventListener("click", (evento) => {
        const recolhido = document.getElementById("menu-admin").classList.toggle("recolhido");
        document.querySelector(".layout-admin").classList.toggle("menu-recolhido", recolhido);
        evento.currentTarget.setAttribute("aria-expanded", String(!recolhido));
        evento.currentTarget.textContent = recolhido ? "Expandir menu" : "Recolher menu";
    });

    // ---------- desenho de cada relatório ----------

    function renderizarVendas(dados) {
        const resumo = dados.resumo || {};
        definirTexto("vendas-compras", inteiro(resumo.quantidade_compras));
        definirTexto("vendas-itens", inteiro(resumo.itens_vendidos));
        definirTexto("vendas-total", preco(resumo.total_centavos));
        definirTexto("vendas-custo", preco(resumo.custo_centavos));
        definirTexto("vendas-lucro", preco(resumo.lucro_centavos));
        definirTexto("vendas-ticket", preco(resumo.ticket_medio_centavos));

        preencherTabela("vendas-por-produto", dados.por_produto, 5, "Nenhum produto vendido no período.", (item) => linha([
            celula(item.nome, "", true),
            celula(item.categoria || "—"),
            celula(inteiro(item.quantidade), "numero"),
            celula(preco(item.total_centavos), "numero"),
            celula(preco(item.lucro_centavos), "numero"),
        ]));

        // Consumo por usuário: quem comprou e quanto, do maior para o menor total.
        preencherTabela("vendas-por-usuario", dados.por_usuario, 5, "Nenhum usuário fez compras neste período.", (usuario) => linha([
            celula(usuario.nome, "", true),
            celula(usuario.matricula || "—", "texto-quebravel"),
            celula(inteiro(usuario.quantidade_compras), "numero"),
            celula(inteiro(usuario.itens), "numero"),
            celula(preco(usuario.total_centavos), "numero"),
        ]));

        const dias = dados.por_dia || [];
        const maiorTotal = Math.max(0, ...dias.map((dia) => Number(dia.total_centavos || 0)));
        preencherTabela("vendas-por-dia", dias, 3, "Nenhuma venda no período.", (dia) => linha([
            celula(formatarDia(dia.data), "celula-data", true),
            celula(inteiro(dia.quantidade_compras), "numero"),
            celula(criarBarra(dia.total_centavos, maiorTotal)),
        ]));
    }

    // Itens de uma compra, um por linha: "2 × Barra de Cereal".
    function listaDeItens(itens) {
        if (!itens || !itens.length) return document.createTextNode("—");
        const lista = el("ul", "lista-itens-compra");
        // role="list": a lista continua anunciada mesmo sem os marcadores (list-style: none).
        lista.setAttribute("role", "list");
        itens.forEach((item) => {
            lista.append(el("li", "", `${inteiro(item.quantidade)} × ${item.nome}`));
        });
        return lista;
    }

    function renderizarCompras(dados) {
        const compras = dados.compras || [];
        const total = Number(dados.total_compras ?? compras.length);
        definirTexto("compras-total", inteiro(total));
        definirTexto("compras-quantidade", inteiro(compras.length));

        // total_compras conta todo o período; a lista traz só as mais recentes, até o limite.
        const avisoLimite = document.getElementById("compras-aviso-limite");
        avisoLimite.hidden = total <= compras.length;
        avisoLimite.textContent = avisoLimite.hidden
            ? ""
            : `A lista mostra só as ${inteiro(compras.length)} compras mais recentes, de um total de ${inteiro(total)} no período. Para ver as demais, reduza o período ou escolha um usuário.`;

        const textoVazio = filtroUsuarioCompras.value
            ? "Este usuário não fez compras neste período."
            : "Nenhuma compra registrada neste período.";
        preencherTabela("compras-lista", compras, 5, textoVazio, (compra) => {
            const usuario = compra.usuario || {};
            const celulaUsuario = celula("");
            celulaUsuario.append(el("span", "nome-usuario", usuario.nome || "Usuário não identificado"));
            if (usuario.matricula) {
                celulaUsuario.append(el("span", "texto-secundario", `Matrícula ${usuario.matricula}`));
            }
            return linha([
                celula(Cantina.formatarDataHora(compra.data_hora), "celula-data"),
                // \u00a0 = espaço que não quebra: "Nº 12" fica sempre na mesma linha.
                celula(`Nº\u00a0${compra.id_compra}`, "", true),
                celulaUsuario,
                celula(listaDeItens(compra.itens)),
                celula(preco(compra.valor_total_centavos), "numero"),
            ]);
        });
    }

    function rotuloDoUsuarioFiltrado() {
        const opcao = filtroUsuarioCompras.selectedOptions[0];
        return opcao ? opcao.textContent : `nº ${filtroUsuarioCompras.value}`;
    }

    // Lista de usuários do filtro da aba Compras, buscada na primeira vez que a aba abre.
    // Se falhar, o filtro fica só com "Todos os usuários" e tenta de novo na próxima abertura.
    async function carregarOpcoesDeUsuario() {
        if (opcoesDeUsuario !== "pendentes") return;
        opcoesDeUsuario = "carregando";
        try {
            const resultado = await Cantina.requisitar("/api/admin/usuarios?status=TODOS&perfil=TODOS");
            const selecionado = filtroUsuarioCompras.value;
            const opcoes = (resultado.usuarios || []).map((usuario) => {
                const inativo = usuario.status === "INATIVO" ? " (inativo)" : "";
                return new Option(`${usuario.nome} — matrícula ${usuario.matricula}${inativo}`, String(usuario.id_usuario));
            });
            filtroUsuarioCompras.replaceChildren(new Option("Todos os usuários", ""), ...opcoes);
            filtroUsuarioCompras.value = selecionado;
            opcoesDeUsuario = "prontas";
        } catch {
            opcoesDeUsuario = "pendentes";
        }
    }

    function renderizarSaldos(dados) {
        definirTexto("saldos-total", preco(dados.total_saldos_centavos));
        definirTexto("saldos-usuarios", inteiro(dados.quantidade_usuarios));

        preencherTabela("saldos-lista", dados.usuarios, 4, "Nenhum cliente cadastrado.", (usuario) => linha([
            celula(usuario.nome, "", true),
            celula(usuario.matricula, "texto-quebravel"),
            celula(etiquetaDeSituacao(usuario.status)),
            celula(preco(usuario.saldo_centavos), "numero"),
        ]));
    }

    function renderizarEstoque(dados) {
        definirTexto("estoque-produtos", inteiro(dados.quantidade_produtos));
        definirTexto("estoque-zerados", inteiro(dados.sem_estoque));
        definirTexto("estoque-itens", inteiro(dados.total_itens));
        definirTexto("estoque-valor", preco(dados.valor_estoque_centavos));

        preencherTabela("estoque-lista", dados.produtos, 7, "Nenhum produto cadastrado.", (produto) => {
            const zerado = Number(produto.quantidade_estoque || 0) === 0;
            // Zerado: a etiqueta com o texto "Sem estoque" acompanha o fundo de aviso da linha.
            const quantidade = celula(inteiro(produto.quantidade_estoque), "numero");
            if (zerado) quantidade.append(" ", el("span", "etiqueta etiqueta-aviso", "Sem estoque"));
            return linha([
                celula(produto.nome, "", true),
                celula(produto.categoria || "—"),
                celula(etiquetaDeSituacao(produto.status)),
                quantidade,
                celula(preco(produto.preco_compra_centavos), "numero"),
                celula(preco(produto.preco_venda_centavos), "numero"),
                celula(preco(produto.valor_estoque_centavos), "numero"),
            ], zerado ? "linha-alerta" : "");
        });
    }

    function renderizarDepositos(dados) {
        const depositos = dados.movimentacoes || [];
        definirTexto("depositos-total", preco(dados.totais?.creditos_centavos));
        definirTexto("depositos-quantidade", inteiro(depositos.length));

        // O total considera todo o período, mesmo quando a lista chega cortada pelo limite.
        const avisoLimite = document.getElementById("depositos-aviso-limite");
        avisoLimite.hidden = depositos.length < LIMITE_DEPOSITOS;
        avisoLimite.textContent = avisoLimite.hidden
            ? ""
            : `A lista mostra ${LIMITE_DEPOSITOS} depósitos (o limite da tela). O total declarado considera todos os depósitos do período.`;

        preencherTabela("depositos-lista", depositos, 4, "Nenhum depósito declarado no período.", (deposito) => linha([
            celula(Cantina.formatarDataHora(deposito.data_hora), "celula-data"),
            celula(deposito.usuario?.nome || "Usuário não identificado"),
            celula(deposito.usuario?.matricula || "—", "texto-quebravel"),
            celula(preco(deposito.valor_centavos), "numero"),
        ]));
    }

    // ---------- carga e estados (carregando, erro, pronto) ----------

    function partesDoPainel(nome) {
        const painel = document.getElementById(`painel-${nome}`);
        return {
            estado: painel.querySelector("[data-estado]"),
            conteudo: painel.querySelector("[data-conteudo]"),
            periodo: painel.querySelector("[data-periodo]"),
        };
    }

    function mostrarEstado(nome, texto, { erro = false, aoTentar = null } = {}) {
        const { estado, conteudo } = partesDoPainel(nome);
        estado.replaceChildren(el("p", "", texto));
        estado.classList.toggle("estado-erro", erro);
        if (aoTentar) {
            const botao = el("button", "botao botao-secundario nao-imprimir", "Tentar novamente");
            botao.type = "button";
            botao.addEventListener("click", aoTentar);
            estado.append(botao);
        }
        estado.hidden = false;
        conteudo.hidden = true;
    }

    function mostrarConteudo(nome) {
        const { estado, conteudo } = partesDoPainel(nome);
        estado.hidden = true;
        estado.replaceChildren();
        conteudo.hidden = false;
    }

    // Linha abaixo do título: período do relatório ou momento da consulta.
    function descreverPeriodo(nome, dados) {
        const { periodo: saida } = partesDoPainel(nome);
        if (RELATORIOS[nome].usaPeriodo) {
            const de = dados?.periodo?.de || periodo.de;
            const ate = dados?.periodo?.ate || periodo.ate;
            const textoPeriodo = de === ate
                ? `Período: ${formatarDia(de)}`
                : `Período: ${formatarDia(de)} a ${formatarDia(ate)}`;
            saida.textContent = textoPeriodo + (RELATORIOS[nome].descricaoExtra?.() || "");
        } else {
            saida.textContent = `Situação atual, consultada em ${Cantina.formatarDataHora(new Date().toISOString())}. Não depende do período.`;
        }
    }

    // 422: a API recusou algum filtro; cada mensagem vai para junto do seu campo
    // (datas no formulário de período; os demais no filtro da própria aba).
    function exibirErrosDosFiltros(definicao, campos) {
        const doPeriodo = {};
        const daAba = {};
        Object.entries(campos).forEach(([campo, mensagem]) => {
            const destino = definicao.formulario?.elements.namedItem(campo) ? daAba : doPeriodo;
            destino[campo] = mensagem;
        });
        if (Object.keys(doPeriodo).length) Cantina.exibirErros(formularioPeriodo, doPeriodo);
        if (Object.keys(daAba).length) Cantina.exibirErros(definicao.formulario, daAba);
    }

    // Busca o relatório só quando ainda não foi carregado para o período (e o filtro) atual.
    async function carregarRelatorio(nome, { forcar = false } = {}) {
        const definicao = RELATORIOS[nome];
        const controle = controles[nome];
        const chave = (definicao.usaPeriodo ? `${periodo.de}|${periodo.ate}` : "atual")
            + (definicao.filtro ? `|${definicao.filtro()}` : "");
        if (!forcar && controle.chave === chave) return;

        const pedido = ++controle.pedido;
        controle.chave = chave;
        if (definicao.formulario) Cantina.limparErros(definicao.formulario);
        descreverPeriodo(nome);
        mostrarEstado(nome, "Carregando relatório…");

        try {
            const dados = await Cantina.requisitar(definicao.url(periodo));
            if (pedido !== controle.pedido) return; // chegou um pedido mais novo
            definicao.renderizar(dados);
            descreverPeriodo(nome, dados);
            mostrarConteudo(nome);
        } catch (erro) {
            if (pedido !== controle.pedido) return;
            controle.chave = null; // permite tentar de novo
            const camposInvalidos = Object.keys(erro.campos || {}).length > 0;
            if (camposInvalidos) exibirErrosDosFiltros(definicao, erro.campos);
            mostrarEstado(nome, tratarErro(erro), {
                erro: true,
                aoTentar: camposInvalidos ? null : () => carregarRelatorio(nome, { forcar: true }),
            });
        }
    }

    // ---------- abas ----------

    function selecionarAba(aba, { focar = false, registrarNaUrl = true } = {}) {
        abas.forEach((item) => {
            const ativa = item === aba;
            item.setAttribute("aria-selected", String(ativa));
            item.tabIndex = ativa ? 0 : -1;
            document.getElementById(item.getAttribute("aria-controls")).hidden = !ativa;
        });
        relatorioAtivo = aba.dataset.relatorio;
        if (focar) aba.focus();
        // Guarda a aba na URL (#saldos, por exemplo) para a página reabrir no mesmo relatório.
        if (registrarNaUrl) {
            window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}#${relatorioAtivo}`);
        }
        RELATORIOS[relatorioAtivo].aoAbrir?.();
        carregarRelatorio(relatorioAtivo);
    }

    abas.forEach((aba) => {
        aba.addEventListener("click", () => selecionarAba(aba));
    });

    // Setas esquerda/direita, Home e End trocam de aba (padrão de abas acessíveis).
    listaDeAbas.addEventListener("keydown", (evento) => {
        const atual = abas.indexOf(document.activeElement);
        if (atual < 0) return;
        let destino = null;
        if (evento.key === "ArrowRight") destino = (atual + 1) % abas.length;
        else if (evento.key === "ArrowLeft") destino = (atual - 1 + abas.length) % abas.length;
        else if (evento.key === "Home") destino = 0;
        else if (evento.key === "End") destino = abas.length - 1;
        if (destino === null) return;
        evento.preventDefault();
        selecionarAba(abas[destino], { focar: true });
    });

    // ---------- período ----------

    function marcarAtalhoAtivo() {
        botoesAtalho.forEach((botao) => {
            const doAtalho = periodoDosUltimosDias(Number(botao.dataset.atalhoDias));
            const ativo = Boolean(periodo) && doAtalho.de === periodo.de && doAtalho.ate === periodo.ate;
            botao.setAttribute("aria-pressed", String(ativo));
        });
    }

    function validarPeriodo(de, ate) {
        const erros = {};
        if (!dataValida(de)) erros.de = "Informe a data inicial.";
        if (!dataValida(ate)) erros.ate = "Informe a data final.";
        if (!erros.de && !erros.ate && de > ate) erros.de = "A data inicial não pode ser depois da data final.";
        return erros;
    }

    // Valida o período e recarrega o relatório aberto; os outros recarregam ao abrir a aba.
    function aplicarPeriodo() {
        Cantina.limparErros(formularioPeriodo);
        const de = campoDe.value;
        const ate = campoAte.value;
        if (Cantina.exibirErros(formularioPeriodo, validarPeriodo(de, ate))) return;
        periodo = { de, ate };
        marcarAtalhoAtivo();
        Object.values(controles).forEach((controle) => { controle.chave = null; });
        carregarRelatorio(relatorioAtivo, { forcar: true });
    }

    Cantina.ligarLimpezaDeErros(formularioPeriodo);

    // É uma consulta (nada é gravado): vale o botão "Atualizar relatório" ou Enter em um campo.
    formularioPeriodo.addEventListener("submit", (evento) => {
        evento.preventDefault();
        aplicarPeriodo();
    });

    botoesAtalho.forEach((botao) => {
        botao.addEventListener("click", () => {
            const doAtalho = periodoDosUltimosDias(Number(botao.dataset.atalhoDias));
            campoDe.value = doAtalho.de;
            campoAte.value = doAtalho.ate;
            aplicarPeriodo();
        });
    });

    // ---------- filtro de usuário da aba Compras ----------

    // É uma consulta (nada é gravado): a lista é refeita ao escolher o usuário.
    filtroUsuarioCompras.addEventListener("change", () => carregarRelatorio("compras"));
    // O botão "Atualizar lista" (ou Enter no campo) refaz a consulta com o filtro escolhido.
    formularioCompras.addEventListener("submit", (evento) => {
        evento.preventDefault();
        carregarRelatorio("compras", { forcar: true });
    });

    // ---------- impressão ----------

    // Sai só o relatório da aba aberta (as outras estão com hidden), com título,
    // período e data de emissão; menu, filtros e abas têm a classe .nao-imprimir.
    window.addEventListener("beforeprint", () => {
        const texto = `Emitido em ${Cantina.formatarDataHora(new Date().toISOString())} por ${administrador.nome}.`;
        document.querySelectorAll("[data-emissao]").forEach((saida) => { saida.textContent = texto; });
    });

    document.getElementById("botao-imprimir").addEventListener("click", () => window.print());

    // ---------- início ----------

    const padrao = periodoDosUltimosDias(DIAS_PADRAO);
    campoDe.value = padrao.de;
    campoAte.value = padrao.ate;
    periodo = padrao;
    marcarAtalhoAtivo();

    // Abre a aba indicada na URL (#compras, #saldos, #estoque, #depositos); sem isso, Vendas.
    const abaInicial = abas.find((aba) => aba.dataset.relatorio === window.location.hash.slice(1)) || abas[0];
    selecionarAba(abaInicial, { registrarNaUrl: false });
});
