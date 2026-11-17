// Minha conta: resumo do usuário, declaração de crédito (depósito na caixa),
// extrato da carteira e histórico de compras. A tela exige login.
document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    // Limites do contrato da API para um crédito declarado.
    const VALOR_MINIMO = 100;      // R$ 1,00
    const VALOR_MAXIMO = 50000;    // R$ 500,00
    const LIMITE_DAS_LISTAS = 50;
    const elemento = Cantina.criarElemento;
    const formatarPreco = Cantina.formatarPreco;

    // Resumo
    const saudacao = document.getElementById("saudacao-conta");
    const saldoConta = document.getElementById("saldo-conta");
    const dicaSaldo = document.getElementById("dica-saldo");

    // Adicionar crédito
    const formCredito = document.getElementById("form-credito");
    const campoValor = formCredito.elements.namedItem("valor_centavos");
    const campoDeclaracao = formCredito.elements.namedItem("declaracao");
    const atalhosValor = document.getElementById("atalhos-valor");
    const feedbackCredito = formCredito.querySelector(".feedback-form");
    const botaoCredito = document.getElementById("botao-credito");
    const mensagemCredito = document.getElementById("mensagem-credito");

    // Extrato e compras
    const tituloExtrato = document.getElementById("titulo-extrato");
    const estadoExtrato = document.getElementById("estado-extrato");
    const rolagemExtrato = document.getElementById("rolagem-extrato");
    const linhasExtrato = document.getElementById("linhas-extrato");
    const tituloCompras = document.getElementById("titulo-compras");
    const estadoCompras = document.getElementById("estado-compras");
    const listaCompras = document.getElementById("lista-compras");

    let saldoCentavos = null;
    let enviando = false;
    // Chave de idempotência do crédito em aberto: {chave, valor}. É reutilizada se o usuário
    // tentar de novo o mesmo valor (por exemplo, após falha de rede) e trocada depois de um
    // crédito concluído ou quando o valor muda.
    let creditoPendente = null;

    // ---------- apoio ----------

    // Mostra um texto de estado (carregando, vazio ou erro) e, se for erro, o botão de tentar de novo.
    function mostrarEstado(container, texto, aoTentarDeNovo) {
        container.replaceChildren();
        container.hidden = !texto;
        if (!texto) return;
        container.append(elemento("p", "", texto));
        if (aoTentarDeNovo) {
            const botao = elemento("button", "botao botao-secundario", "Tentar novamente");
            botao.type = "button";
            botao.addEventListener("click", aoTentarDeNovo);
            container.append(botao);
        }
    }

    function criarData(iso) {
        const tempo = elemento("time", "", Cantina.formatarDataHora(iso) || "—");
        if (iso) tempo.dateTime = iso;
        return tempo;
    }

    // ---------- resumo ----------

    function definirSaldo(centavos) {
        saldoCentavos = centavos;
        saldoConta.textContent = formatarPreco(centavos);
        Cantina.atualizarSaldoCabecalho(centavos);
        const semSaldo = centavos <= 0;
        dicaSaldo.hidden = !semSaldo;
        dicaSaldo.textContent = semSaldo ? "Você ainda não tem saldo. Adicione crédito para registrar suas compras." : "";
    }

    function preencherResumo(usuario) {
        const primeiroNome = String(usuario.nome || "").trim().split(/\s+/)[0];
        if (primeiroNome) {
            saudacao.textContent = `Olá, ${primeiroNome}! Acompanhe seu saldo, declare seus depósitos e veja suas compras.`;
        }
        document.getElementById("conta-nome").textContent = usuario.nome || "—";
        document.getElementById("conta-matricula").textContent = usuario.matricula || "—";
        document.getElementById("conta-email").textContent = usuario.email || "—";
        document.getElementById("conta-cpf").textContent = usuario.cpf_mascarado || "—";
        definirSaldo(Number(usuario.saldo_centavos) || 0);
    }

    // ---------- adicionar crédito ----------

    function validarCredito(valor) {
        const erros = {};
        if (!valor) erros.valor_centavos = "Informe o valor que você depositou.";
        else if (valor < VALOR_MINIMO) erros.valor_centavos = "O valor mínimo é de R$ 1,00.";
        else if (valor > VALOR_MAXIMO) erros.valor_centavos = "O valor máximo por depósito é de R$ 500,00.";
        if (!campoDeclaracao.checked) erros.declaracao = "Marque a declaração para confirmar o depósito.";
        return erros;
    }

    function chaveDoCredito(valor) {
        if (!creditoPendente || creditoPendente.valor !== valor) {
            creditoPendente = { chave: Cantina.novaChave(), valor };
        }
        return creditoPendente.chave;
    }

    async function adicionarCredito() {
        if (enviando) return;
        Cantina.limparErros(formCredito);
        Cantina.mostrarMensagem(mensagemCredito, "");

        const valor = Cantina.textoParaCentavos(campoValor.value);
        if (Cantina.exibirErros(formCredito, validarCredito(valor))) return;

        enviando = true;
        try {
            const resultado = await Cantina.comBotaoOcupado(botaoCredito, "Registrando crédito...", () =>
                Cantina.requisitar("/api/carteira/creditos", {
                    method: "POST",
                    json: { valor_centavos: valor, chave_idempotencia: chaveDoCredito(valor) },
                }));

            // Crédito registrado: o próximo depósito usa outra chave.
            creditoPendente = null;
            const carteira = resultado.carteira || {};
            if (Number.isInteger(carteira.saldo_centavos)) definirSaldo(carteira.saldo_centavos);
            formCredito.reset();
            Cantina.mostrarMensagem(
                mensagemCredito,
                `Crédito de ${formatarPreco(valor)} adicionado. Seu saldo agora é de ${formatarPreco(saldoCentavos)}. Obrigado por manter a Cantina da Honestidade funcionando!`,
                "sucesso",
            );
            carregarExtrato();
        } catch (erro) {
            // Sessão expirada: volta para o login.
            if (erro.status === 401) {
                Cantina.irParaLogin();
                return;
            }
            if (Object.keys(erro.campos || {}).length) {
                Cantina.exibirErros(formCredito, erro.campos);
                return;
            }
            const complemento = erro.status === 0 ? " Pode tentar de novo: o crédito não será lançado em dobro." : "";
            Cantina.mostrarMensagem(feedbackCredito, erro.message + complemento, "erro");
        } finally {
            enviando = false;
        }
    }

    Cantina.ligarMascaraMoeda(campoValor);
    Cantina.ligarLimpezaDeErros(formCredito);
    // Regra do sistema: Enter em um campo não grava; só o clique no botão "Adicionar crédito".
    Cantina.bloquearEnvioPorEnter(formCredito);

    formCredito.addEventListener("submit", (evento) => {
        evento.preventDefault();
        adicionarCredito();
    });

    // Atalhos de valor: só preenchem o campo, não gravam nada.
    atalhosValor.addEventListener("click", (evento) => {
        const botao = evento.target.closest("button[data-valor]");
        if (!botao) return;
        campoValor.value = Cantina.centavosParaTexto(Number(botao.dataset.valor));
        // Avisa o campo da mudança (limpa a mensagem de erro, se houver).
        campoValor.dispatchEvent(new Event("input", { bubbles: true }));
    });

    // O bloqueio do Enter acima vale para tudo que não é o botão de enviar; aqui os
    // atalhos continuam acionáveis por Enter, como qualquer botão.
    atalhosValor.addEventListener("keydown", (evento) => {
        if (evento.key !== "Enter" || evento.repeat) return;
        const botao = evento.target.closest("button[data-valor]");
        if (!botao) return;
        evento.preventDefault();
        botao.click();
    });

    // ---------- extrato ----------

    const TIPOS_DE_MOVIMENTACAO = {
        CREDITO: { texto: "Crédito", classe: "etiqueta etiqueta-sucesso" },
        DEBITO: { texto: "Compra", classe: "etiqueta" },
        AJUSTE: { texto: "Ajuste", classe: "etiqueta etiqueta-ajuste" },
    };

    function criarLinhaDoExtrato(movimentacao) {
        const linha = elemento("tr");

        const data = elemento("td", "coluna-data");
        data.append(criarData(movimentacao.data_hora));

        const tipo = elemento("td");
        const info = TIPOS_DE_MOVIMENTACAO[movimentacao.tipo] || { texto: movimentacao.tipo || "—", classe: "etiqueta" };
        tipo.append(elemento("span", info.classe, info.texto));

        const descricao = elemento("td", "coluna-descricao", movimentacao.descricao || "—");

        // O valor leva sinal ("+" ou "−") além da cor; o leitor de tela ouve "entrada" ou "saída".
        const centavos = Number(movimentacao.valor_centavos) || 0;
        const entrada = centavos >= 0;
        const quantia = formatarPreco(Math.abs(centavos));
        const valor = elemento("td", `numero ${entrada ? "valor-positivo" : "valor-negativo"}`);
        const visivel = elemento("span", "", `${entrada ? "+" : "−"} ${quantia}`);
        visivel.setAttribute("aria-hidden", "true");
        valor.append(visivel, elemento("span", "somente-leitor", `${entrada ? "entrada de" : "saída de"} ${quantia}`));

        const saldo = elemento("td", "numero", formatarPreco(movimentacao.saldo_apos_centavos));

        linha.append(data, tipo, descricao, valor, saldo);
        return linha;
    }

    async function carregarExtrato() {
        // Na primeira carga mostra "Carregando"; nas seguintes a tabela fica na tela até chegar a nova.
        if (rolagemExtrato.hidden) mostrarEstado(estadoExtrato, "Carregando extrato...");
        try {
            const resultado = await Cantina.requisitar(`/api/carteira/movimentacoes?limite=${LIMITE_DAS_LISTAS}`);
            const movimentacoes = Array.isArray(resultado.movimentacoes) ? resultado.movimentacoes : [];
            linhasExtrato.replaceChildren(...movimentacoes.map(criarLinhaDoExtrato));
            rolagemExtrato.hidden = movimentacoes.length === 0;
            mostrarEstado(estadoExtrato, movimentacoes.length
                ? ""
                : "Você ainda não tem movimentações. Quando adicionar um crédito ou fizer uma compra, ela aparece aqui.");
        } catch (erro) {
            if (erro.status === 401) {
                Cantina.irParaLogin();
                return;
            }
            rolagemExtrato.hidden = true;
            mostrarEstado(estadoExtrato, `Não foi possível carregar o extrato. ${erro.message}`, () => {
                tituloExtrato.focus();
                carregarExtrato();
            });
        }
    }

    // ---------- minhas compras ----------

    function criarItemDaCompra(item) {
        const linha = elemento("li", "item-compra");
        linha.append(elemento("span", "item-nome", `${item.quantidade} × ${item.nome}`));
        linha.append(elemento("span", "item-unitario", `${formatarPreco(item.preco_unitario_centavos)} cada`));
        const subtotal = elemento("strong", "item-subtotal");
        subtotal.append(elemento("span", "somente-leitor", "Subtotal: "), formatarPreco(item.subtotal_centavos));
        linha.append(subtotal);
        return linha;
    }

    function criarCompra(compra) {
        const cartao = elemento("li", "compra");
        cartao.id = `compra-${compra.id_compra}`;

        const topo = elemento("div", "topo-compra");
        const identificacao = elemento("div", "identificacao-compra");
        identificacao.append(elemento("h3", "", `Compra nº ${compra.id_compra}`));
        const data = elemento("p", "data-compra");
        data.append(criarData(compra.data_hora));
        identificacao.append(data);

        const total = elemento("p", "total-da-compra");
        total.append(elemento("span", "", "Total "), elemento("strong", "", formatarPreco(compra.valor_total_centavos)));
        topo.append(identificacao, total);

        const itens = elemento("ul", "itens-da-compra");
        itens.setAttribute("aria-label", `Itens da compra nº ${compra.id_compra}`);
        (Array.isArray(compra.itens) ? compra.itens : []).forEach((item) => itens.append(criarItemDaCompra(item)));

        cartao.append(topo, itens);
        return cartao;
    }

    async function carregarCompras() {
        if (listaCompras.hidden) mostrarEstado(estadoCompras, "Carregando compras...");
        try {
            const resultado = await Cantina.requisitar(`/api/compras?limite=${LIMITE_DAS_LISTAS}`);
            const compras = Array.isArray(resultado.compras) ? resultado.compras : [];
            listaCompras.replaceChildren(...compras.map(criarCompra));
            listaCompras.hidden = compras.length === 0;
            if (compras.length) {
                mostrarEstado(estadoCompras, "");
                return;
            }
            mostrarEstado(estadoCompras, "Você ainda não registrou nenhuma compra.");
            const link = elemento("a", "link-acao", "Ver produtos da cantina");
            link.href = "/html/catalogo_produtos.html#produtos";
            estadoCompras.append(link);
        } catch (erro) {
            if (erro.status === 401) {
                Cantina.irParaLogin();
                return;
            }
            listaCompras.hidden = true;
            mostrarEstado(estadoCompras, `Não foi possível carregar suas compras. ${erro.message}`, () => {
                tituloCompras.focus();
                carregarCompras();
            });
        }
    }

    // ---------- início ----------

    // Depois que as listas carregam a página muda de altura: reposiciona na seção pedida
    // no endereço (#creditos, #extrato, #compras...).
    function irParaSecaoDoEndereco() {
        const id = window.location.hash.slice(1);
        if (!id) return;
        const secao = document.getElementById(id);
        if (!secao || !secao.matches("section")) return;
        secao.scrollIntoView();
        // Quem chega por "Adicionar crédito" já pode digitar o valor.
        if (id === "creditos") campoValor.focus({ preventScroll: true });
    }

    async function iniciar() {
        await Cantina.pronta();
        // Sem login, o usuário é levado para a tela de entrada e volta para cá depois.
        const usuario = await Cantina.exigirLogin();
        preencherResumo(usuario);
        await Promise.allSettled([carregarExtrato(), carregarCompras()]);
        irParaSecaoDoEndereco();
    }

    iniciar();
});
