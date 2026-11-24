// Tela administrativa de usuários: busca, edição do cadastro, inativação/reativação,
// ajuste de saldo e redefinição de senha. Usa as funções compartilhadas do objeto
// Cantina (base.js).
document.addEventListener("DOMContentLoaded", async () => {
    "use strict";

    // Só administradores passam daqui: quem não está logado vai para o login e
    // quem não é administrador volta ao catálogo.
    const administrador = await Cantina.exigirAdministrador();

    const API = "/api/admin/usuarios";
    const AJUSTE_MAXIMO_CENTAVOS = 100000; // R$ 1.000,00 por ajuste
    const ATRASO_BUSCA_MS = 350;
    const NOMES_PERFIL = { ADMINISTRADOR: "Administrador", CLIENTE: "Cliente" };
    const el = Cantina.criarElemento;

    const mensagemApi = document.getElementById("mensagem-api");
    const formularioFiltros = document.getElementById("form-filtros");
    const campoBusca = document.getElementById("busca-usuarios");
    const filtroStatus = document.getElementById("filtro-status");
    const filtroPerfil = document.getElementById("filtro-perfil");
    const contador = document.getElementById("contador-usuarios");
    const estadoLista = document.getElementById("estado-usuarios");
    const areaTabela = document.getElementById("area-tabela-usuarios");
    const corpoTabela = document.getElementById("corpo-tabela-usuarios");

    const modalEdicao = document.getElementById("modal-editar-usuario");
    const modalSituacao = document.getElementById("modal-situacao-usuario");
    const modalAjuste = document.getElementById("modal-ajuste-saldo");
    const modalSenha = document.getElementById("modal-redefinir-senha");
    const modais = [modalEdicao, modalSituacao, modalAjuste, modalSenha];
    const formularioEdicao = document.getElementById("form-editar-usuario");
    const formularioAjuste = document.getElementById("form-ajuste-saldo");
    const formularioSenha = document.getElementById("form-redefinir-senha");
    const caixaMostrarSenhas = document.getElementById("mostrar-senhas");
    const botaoConfirmarSituacao = document.getElementById("confirmar-situacao");
    const erroSituacao = document.getElementById("erro-situacao-usuario");
    const saldoResultante = document.getElementById("ajuste-saldo-resultante");

    const usuariosPorId = new Map();
    const focosAnteriores = new WeakMap();
    let usuarioSelecionado = null;
    let chaveAjuste = null;
    let ultimoPedido = 0;
    let temporizadorBusca = null;

    // ---------- utilitários ----------

    function ehProprioUsuario(usuario) {
        return Number(usuario.id_usuario) === Number(administrador.id_usuario);
    }

    function campoEdicao(nome) {
        return formularioEdicao.elements.namedItem(nome);
    }

    function campoAjuste(nome) {
        return formularioAjuste.elements.namedItem(nome);
    }

    function campoSenha(nome) {
        return formularioSenha.elements.namedItem(nome);
    }

    function valorComSinal(centavos) {
        return (centavos < 0 ? "− " : "+ ") + Cantina.formatarPreco(Math.abs(centavos));
    }

    const plural = Cantina.plural;

    // Traduz o erro da API em um texto claro. Sessão encerrada leva ao login.
    function tratarErro(erro) {
        if (erro.status === 401) {
            Cantina.irParaLogin();
            return "Sua sessão terminou. Abrindo a tela de login…";
        }
        if (erro.status === 403) {
            return "Sua conta não tem permissão de administrador para esta operação.";
        }
        if (erro.codigo === "OPERACAO_PROPRIA") {
            return "Você não pode inativar a sua própria conta nem retirar o seu próprio perfil de administrador. Peça a outro administrador.";
        }
        if (erro.codigo === "SALDO_INSUFICIENTE") {
            const saldo = erro.detalhes?.saldo_centavos;
            return Number.isInteger(saldo)
                ? `O desconto é maior que o saldo do usuário (${Cantina.formatarPreco(saldo)}). O saldo não pode ficar negativo.`
                : "O desconto é maior que o saldo do usuário. O saldo não pode ficar negativo.";
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

    // ---------- menu lateral ----------

    document.getElementById("alternar-menu").addEventListener("click", (evento) => {
        const recolhido = document.getElementById("menu-admin").classList.toggle("recolhido");
        document.querySelector(".layout-admin").classList.toggle("menu-recolhido", recolhido);
        evento.currentTarget.setAttribute("aria-expanded", String(!recolhido));
        evento.currentTarget.textContent = recolhido ? "Expandir menu" : "Recolher menu";
    });

    // ---------- modais ----------

    function abrirModal(modal, focoInicial = null) {
        focosAnteriores.set(modal, document.activeElement);
        modal.classList.add("aberto");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-aberto");
        const conteudo = modal.querySelector(".modal-conteudo");
        if (conteudo) conteudo.scrollTop = 0;
        const primeiroCampo = focoInicial || modal.querySelector(
            "input:not([type='hidden']):not([disabled]), select:not([disabled]), textarea, button:not([disabled])",
        );
        primeiroCampo?.focus({ preventScroll: true });
    }

    // Ao fechar, o foco volta para o botão que abriu o modal.
    function fecharModal(modal) {
        if (!modal.classList.contains("aberto")) return;
        modal.classList.remove("aberto");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-aberto");
        // Senhas digitadas não ficam guardadas na página depois que o modal fecha.
        if (modal === modalSenha) limparFormularioSenha();
        const focoAnterior = focosAnteriores.get(modal);
        if (focoAnterior?.isConnected) focoAnterior.focus();
    }

    modais.forEach((modal) => {
        modal.addEventListener("click", (evento) => {
            if (evento.target === modal || evento.target.closest("[data-fechar-modal]")) fecharModal(modal);
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

    // ---------- listagem ----------

    function lerFiltros() {
        return {
            q: campoBusca.value.trim(),
            status: filtroStatus.value,
            perfil: filtroPerfil.value,
        };
    }

    function semFiltros(filtros) {
        return !filtros.q && filtros.status === "TODOS" && filtros.perfil === "TODOS";
    }

    // Estado da lista: carregando, vazio ou erro (com botão para tentar de novo).
    function mostrarEstado(texto, { erro = false, aoTentar = null } = {}) {
        estadoLista.replaceChildren(el("p", "", texto));
        estadoLista.classList.toggle("estado-erro", erro);
        if (aoTentar) {
            const botao = el("button", "botao botao-secundario", "Tentar novamente");
            botao.type = "button";
            botao.addEventListener("click", aoTentar);
            estadoLista.append(botao);
        }
        estadoLista.hidden = false;
        areaTabela.hidden = true;
        areaTabela.removeAttribute("aria-busy");
    }

    function mostrarTabela() {
        estadoLista.hidden = true;
        estadoLista.replaceChildren();
        areaTabela.hidden = false;
        areaTabela.removeAttribute("aria-busy");
    }

    function atualizarResumo(usuarios) {
        document.getElementById("total-ativos").textContent =
            usuarios.filter((usuario) => usuario.status === "ATIVO").length;
        document.getElementById("total-inativos").textContent =
            usuarios.filter((usuario) => usuario.status === "INATIVO").length;
        document.getElementById("total-administradores").textContent =
            usuarios.filter((usuario) => usuario.perfil === "ADMINISTRADOR").length;
    }

    // E-mail com ponto de quebra depois do "@", para caber em colunas estreitas.
    function celulaEmail(email) {
        const elemento = celula("", "texto-quebravel");
        const [parteLocal, ...dominio] = String(email || "").split("@");
        elemento.append(parteLocal);
        if (dominio.length) elemento.append("@", document.createElement("wbr"), dominio.join("@"));
        return elemento;
    }

    // O nome do usuário entra no rótulo acessível, pois os botões se repetem em cada linha.
    function botaoDeAcao(texto, acao, rotulo, classe = "") {
        const botao = el("button", `botao-tabela ${classe}`.trim(), texto);
        botao.type = "button";
        botao.dataset.acao = acao;
        botao.setAttribute("aria-label", rotulo);
        return botao;
    }

    function criarLinha(usuario) {
        const linha = document.createElement("tr");
        linha.dataset.usuarioId = usuario.id_usuario;
        const proprio = ehProprioUsuario(usuario);
        const ativo = usuario.status === "ATIVO";

        const nome = celula(usuario.nome, "", true);
        if (proprio) nome.append(" ", el("span", "etiqueta", "Você"));

        const perfil = usuario.perfil === "ADMINISTRADOR"
            ? el("span", "etiqueta etiqueta-destaque", NOMES_PERFIL.ADMINISTRADOR)
            : document.createTextNode(NOMES_PERFIL[usuario.perfil] || usuario.perfil || "—");

        const situacao = el("span", ativo ? "etiqueta etiqueta-sucesso" : "etiqueta etiqueta-erro", ativo ? "Ativo" : "Inativo");

        const acoes = el("div", "tabela-acoes");
        acoes.append(
            botaoDeAcao("Editar", "editar", `Editar ${usuario.nome}`),
            botaoDeAcao("Ajustar saldo", "ajustar", `Ajustar saldo de ${usuario.nome}`),
            botaoDeAcao("Redefinir senha", "senha", `Redefinir senha de ${usuario.nome}`),
        );
        // O administrador não pode inativar a própria conta: a ação nem é oferecida.
        if (!proprio) {
            acoes.append(ativo
                ? botaoDeAcao("Inativar", "situacao", `Inativar ${usuario.nome}`, "botao-perigo")
                : botaoDeAcao("Reativar", "situacao", `Reativar ${usuario.nome}`));
        }
        const linkMovimentacoes = el("a", "botao-tabela", "Movimentações");
        linkMovimentacoes.href = `/html/movimentacoes_adm.html?id_usuario=${encodeURIComponent(usuario.id_usuario)}`;
        linkMovimentacoes.setAttribute("aria-label", `Movimentações de ${usuario.nome}`);
        acoes.append(linkMovimentacoes);

        linha.append(
            nome,
            celula(usuario.matricula, "texto-quebravel"),
            celulaEmail(usuario.email),
            celula(usuario.cpf_mascarado || "—", "celula-fixa"),
            celula(perfil),
            celula(situacao),
            celula(Cantina.formatarPreco(usuario.saldo_centavos), "numero"),
            celula(acoes),
        );
        return linha;
    }

    function renderizarLista(usuarios, filtros) {
        usuariosPorId.clear();
        if (!usuarios.length) {
            corpoTabela.replaceChildren();
            contador.textContent = "Nenhum usuário encontrado.";
            mostrarEstado(semFiltros(filtros)
                ? "Ainda não há usuários cadastrados."
                : "Nenhum usuário corresponde a essa busca ou a esses filtros.");
            return;
        }
        usuarios.forEach((usuario) => usuariosPorId.set(String(usuario.id_usuario), usuario));
        corpoTabela.replaceChildren(...usuarios.map(criarLinha));
        contador.textContent = plural(usuarios.length, "usuário encontrado.", "usuários encontrados.");
        mostrarTabela();
    }

    async function carregarLista() {
        const pedido = ++ultimoPedido;
        const filtros = lerFiltros();
        const parametros = new URLSearchParams({ status: filtros.status, perfil: filtros.perfil });
        if (filtros.q) parametros.set("q", filtros.q);

        // Com a tabela já na tela, ela continua visível enquanto a nova busca chega.
        if (areaTabela.hidden) mostrarEstado("Carregando usuários…");
        else areaTabela.setAttribute("aria-busy", "true");

        try {
            const resultado = await Cantina.requisitar(`${API}?${parametros}`);
            if (pedido !== ultimoPedido) return; // chegou uma busca mais nova
            const usuarios = resultado.usuarios || [];
            if (semFiltros(filtros)) atualizarResumo(usuarios);
            renderizarLista(usuarios, filtros);
        } catch (erro) {
            if (pedido !== ultimoPedido) return;
            contador.textContent = "";
            mostrarEstado(tratarErro(erro), { erro: true, aoTentar: carregarLista });
        }
    }

    // Os cartões contam todos os usuários, mesmo com filtros aplicados na lista.
    async function carregarResumo() {
        try {
            const resultado = await Cantina.requisitar(`${API}?status=TODOS&perfil=TODOS`);
            atualizarResumo(resultado.usuarios || []);
        } catch {
            // O resumo é complementar: se a API falhar, a lista já mostra o erro.
        }
    }

    async function recarregar() {
        const tarefas = [carregarLista()];
        if (!semFiltros(lerFiltros())) tarefas.push(carregarResumo());
        await Promise.all(tarefas);
    }

    // Depois de gravar, a lista é refeita: devolve o foco para a mesma ação do mesmo usuário.
    function focarAcao(idUsuario, acao) {
        const linha = corpoTabela.querySelector(`tr[data-usuario-id="${Number(idUsuario)}"]`);
        const alvo = linha?.querySelector(`[data-acao="${acao}"]`) || linha?.querySelector("[data-acao]") || campoBusca;
        alvo.focus({ preventScroll: true });
    }

    // ---------- filtros ----------

    campoBusca.addEventListener("input", () => {
        window.clearTimeout(temporizadorBusca);
        temporizadorBusca = window.setTimeout(carregarLista, ATRASO_BUSCA_MS);
    });

    filtroStatus.addEventListener("change", carregarLista);
    filtroPerfil.addEventListener("change", carregarLista);

    // Enter no campo de busca consulta na hora (é uma consulta, nada é gravado).
    formularioFiltros.addEventListener("submit", (evento) => {
        evento.preventDefault();
        window.clearTimeout(temporizadorBusca);
        carregarLista();
    });

    document.getElementById("limpar-filtros").addEventListener("click", () => {
        window.clearTimeout(temporizadorBusca);
        formularioFiltros.reset();
        carregarLista();
        campoBusca.focus();
    });

    // ---------- edição do cadastro ----------

    function abrirEdicao(usuario) {
        usuarioSelecionado = usuario;
        formularioEdicao.reset();
        Cantina.limparErros(formularioEdicao);
        campoEdicao("nome").value = usuario.nome || "";
        campoEdicao("matricula").value = usuario.matricula || "";
        campoEdicao("email").value = usuario.email || "";

        // Regra do sistema: ninguém retira o próprio perfil de administrador.
        const proprio = ehProprioUsuario(usuario);
        const perfil = campoEdicao("perfil");
        perfil.value = usuario.perfil;
        perfil.disabled = proprio;
        document.getElementById("editar-perfil-ajuda").textContent = proprio
            ? "Você não pode alterar o seu próprio perfil de administrador."
            : "Administradores acessam este painel. Clientes compram e consultam apenas a própria conta.";

        document.getElementById("editar-cpf").textContent = usuario.cpf_mascarado || "Não informado";
        abrirModal(modalEdicao, campoEdicao("nome"));
    }

    // Mesmas regras do servidor (que valida de novo); aqui evita idas desnecessárias.
    function validarEdicao() {
        const erros = {};
        const nome = campoEdicao("nome").value.trim();
        const matricula = campoEdicao("matricula").value.trim();
        const email = campoEdicao("email").value.trim();
        const perfil = campoEdicao("perfil").value;

        if (!nome) erros.nome = "Informe o nome completo.";
        else if (nome.length < 3 || nome.length > 100) erros.nome = "O nome deve ter de 3 a 100 caracteres.";
        else if (!/\p{L}/u.test(nome)) erros.nome = "O nome precisa ter pelo menos uma letra.";

        if (!matricula) erros.matricula = "Informe a matrícula.";
        else if (!/^\d{4,20}$/.test(matricula)) erros.matricula = "A matrícula deve ter só números, de 4 a 20 dígitos.";

        if (!email) erros.email = "Informe o e-mail.";
        else if (email.length > 150) erros.email = "O e-mail deve ter no máximo 150 caracteres.";
        else if (!Cantina.validarEmail(email)) erros.email = "Informe um e-mail válido, como nome@exemplo.com.";

        if (!(perfil in NOMES_PERFIL)) erros.perfil = "Escolha o perfil do usuário.";
        return erros;
    }

    async function salvarEdicao() {
        const usuario = usuarioSelecionado;
        if (!usuario) return;
        Cantina.limparErros(formularioEdicao);
        if (Cantina.exibirErros(formularioEdicao, validarEdicao())) return;

        const dados = {
            nome: campoEdicao("nome").value.trim(),
            matricula: campoEdicao("matricula").value.trim(),
            email: campoEdicao("email").value.trim(),
            perfil: campoEdicao("perfil").value,
        };
        const botaoSalvar = formularioEdicao.querySelector("button[type='submit']");
        await Cantina.comBotaoOcupado(botaoSalvar, "Salvando…", async () => {
            try {
                const resultado = await Cantina.requisitar(`${API}/${usuario.id_usuario}`, { method: "PUT", json: dados });
                fecharModal(modalEdicao);
                await recarregar();
                focarAcao(usuario.id_usuario, "editar");
                Cantina.mostrarMensagem(mensagemApi, `Cadastro de ${resultado.usuario?.nome || dados.nome} atualizado.`, "sucesso");
                // Se o administrador editou o próprio cadastro, o cabeçalho mostra o nome novo.
                if (ehProprioUsuario(usuario)) Cantina.atualizarSessao();
            } catch (erro) {
                if (Object.keys(erro.campos || {}).length) {
                    Cantina.exibirErros(formularioEdicao, erro.campos);
                } else {
                    formularioEdicao.querySelector(".feedback-form").textContent = tratarErro(erro);
                }
            }
        });
    }

    // ---------- inativar e reativar ----------

    function abrirSituacao(usuario) {
        usuarioSelecionado = usuario;
        const inativar = usuario.status === "ATIVO";
        erroSituacao.textContent = "";
        document.getElementById("titulo-situacao-usuario").textContent = inativar ? "Inativar usuário" : "Reativar usuário";
        document.getElementById("texto-situacao-usuario").textContent = inativar
            ? `Deseja inativar "${usuario.nome}"? O usuário não será apagado; apenas perde o acesso e pode ser reativado.`
            : `Deseja reativar "${usuario.nome}"? O usuário volta a ter acesso ao sistema, com o mesmo cadastro e o mesmo saldo.`;
        botaoConfirmarSituacao.textContent = inativar ? "Inativar usuário" : "Reativar usuário";
        botaoConfirmarSituacao.classList.toggle("botao-perigo", inativar);
        botaoConfirmarSituacao.classList.toggle("botao-principal", !inativar);
        // O foco começa em Cancelar, para a confirmação exigir uma escolha consciente.
        abrirModal(modalSituacao, document.getElementById("cancelar-situacao"));
    }

    botaoConfirmarSituacao.addEventListener("click", async () => {
        const usuario = usuarioSelecionado;
        if (!usuario) return;
        const inativar = usuario.status === "ATIVO";
        erroSituacao.textContent = "";
        await Cantina.comBotaoOcupado(botaoConfirmarSituacao, inativar ? "Inativando…" : "Reativando…", async () => {
            try {
                await Cantina.requisitar(`${API}/${usuario.id_usuario}/${inativar ? "inativar" : "reativar"}`, { method: "PATCH" });
                fecharModal(modalSituacao);
                await recarregar();
                focarAcao(usuario.id_usuario, "situacao");
                Cantina.mostrarMensagem(mensagemApi, inativar
                    ? `A conta de ${usuario.nome} foi inativada: continua no cadastro, sem acesso ao sistema, e pode ser reativada.`
                    : `A conta de ${usuario.nome} foi reativada e voltou a ter acesso ao sistema.`, "sucesso");
            } catch (erro) {
                erroSituacao.textContent = tratarErro(erro);
            }
        });
    });

    // ---------- ajuste de saldo ----------

    // Valor com sinal, como a API espera: positivo acrescenta, negativo desconta.
    function valorDoAjuste() {
        const centavos = Cantina.textoParaCentavos(campoAjuste("valor_centavos").value);
        return campoAjuste("tipo").value === "DESCONTAR" ? -centavos : centavos;
    }

    function atualizarSaldoResultante() {
        const saldoAtual = Number(usuarioSelecionado?.saldo_centavos || 0);
        const resultante = saldoAtual + valorDoAjuste();
        saldoResultante.textContent = resultante < 0
            ? "o desconto é maior que o saldo atual."
            : Cantina.formatarPreco(resultante);
        saldoResultante.classList.toggle("valor-negativo", resultante < 0);
    }

    function abrirAjuste(usuario) {
        usuarioSelecionado = usuario;
        // Uma chave por abertura do modal: reenviar depois de uma falha de rede
        // não lança o mesmo ajuste duas vezes.
        chaveAjuste = Cantina.novaChave();
        formularioAjuste.reset();
        Cantina.limparErros(formularioAjuste);
        document.getElementById("ajuste-usuario").textContent = `${usuario.nome} (matrícula ${usuario.matricula})`;
        document.getElementById("ajuste-saldo-atual").textContent = Cantina.formatarPreco(usuario.saldo_centavos);
        atualizarSaldoResultante();
        abrirModal(modalAjuste, formularioAjuste.querySelector("input[name='tipo']:checked"));
    }

    function validarAjuste() {
        const erros = {};
        const valor = valorDoAjuste();
        const modulo = Math.abs(valor);
        const saldoAtual = Number(usuarioSelecionado?.saldo_centavos || 0);
        const motivo = campoAjuste("motivo").value.trim();

        if (modulo < 1) erros.valor_centavos = "Informe o valor do ajuste (mínimo de R$ 0,01).";
        else if (modulo > AJUSTE_MAXIMO_CENTAVOS) erros.valor_centavos = "O valor máximo de um ajuste é R$ 1.000,00.";
        else if (saldoAtual + valor < 0) {
            erros.valor_centavos = `O desconto não pode ser maior que o saldo atual (${Cantina.formatarPreco(saldoAtual)}).`;
        }

        if (!motivo) erros.motivo = "Informe o motivo do ajuste.";
        else if (motivo.length < 5 || motivo.length > 150) erros.motivo = "O motivo deve ter de 5 a 150 caracteres.";
        return erros;
    }

    async function salvarAjuste() {
        const usuario = usuarioSelecionado;
        if (!usuario) return;
        Cantina.limparErros(formularioAjuste);
        if (Cantina.exibirErros(formularioAjuste, validarAjuste())) return;

        const valor = valorDoAjuste();
        const dados = {
            valor_centavos: valor,
            motivo: campoAjuste("motivo").value.trim(),
            chave_idempotencia: chaveAjuste,
        };
        const feedback = formularioAjuste.querySelector(".feedback-form");
        const botaoSalvar = formularioAjuste.querySelector("button[type='submit']");
        await Cantina.comBotaoOcupado(botaoSalvar, "Lançando…", async () => {
            try {
                const resultado = await Cantina.requisitar(`${API}/${usuario.id_usuario}/ajustes`, { method: "POST", json: dados });
                const lancado = resultado.movimentacao?.valor_centavos;
                const novoSaldo = resultado.carteira?.saldo_centavos;
                const textoSaldo = Number.isInteger(novoSaldo) ? ` Novo saldo: ${Cantina.formatarPreco(novoSaldo)}.` : "";
                fecharModal(modalAjuste);
                await recarregar();
                focarAcao(usuario.id_usuario, "ajustar");
                if (ehProprioUsuario(usuario) && Number.isInteger(novoSaldo)) Cantina.atualizarSaldoCabecalho(novoSaldo);

                // Mesma chave reenviada com outro valor: o servidor devolve o ajuste já gravado.
                if (Number.isInteger(lancado) && lancado !== valor) {
                    Cantina.mostrarMensagem(mensagemApi, `Este ajuste já tinha sido gravado na primeira tentativa, com ${valorComSinal(lancado)}. Nada foi lançado de novo.${textoSaldo}`);
                } else {
                    Cantina.mostrarMensagem(mensagemApi, `Ajuste de ${valorComSinal(valor)} lançado para ${usuario.nome}.${textoSaldo}`, "sucesso");
                }
            } catch (erro) {
                if (Object.keys(erro.campos || {}).length) {
                    Cantina.exibirErros(formularioAjuste, erro.campos);
                } else if (erro.codigo === "SALDO_INSUFICIENTE") {
                    // O saldo mudou desde que a lista foi carregada: mostra o valor atual.
                    const saldo = erro.detalhes?.saldo_centavos;
                    if (Number.isInteger(saldo)) {
                        usuario.saldo_centavos = saldo;
                        document.getElementById("ajuste-saldo-atual").textContent = Cantina.formatarPreco(saldo);
                        atualizarSaldoResultante();
                    }
                    Cantina.exibirErros(formularioAjuste, { valor_centavos: tratarErro(erro) });
                } else if (erro.status === 0) {
                    // Sem resposta: a chave é mantida para a nova tentativa não duplicar o ajuste.
                    feedback.textContent = "Sem resposta do servidor: não foi possível confirmar o ajuste. Clique em Lançar ajuste de novo — o mesmo ajuste não é gravado duas vezes.";
                } else {
                    feedback.textContent = tratarErro(erro);
                }
            }
        });
    }

    // ---------- redefinição de senha ----------

    // A caixa "Mostrar senhas" troca os dois campos entre texto oculto e texto visível.
    function aplicarVisibilidadeDasSenhas() {
        const tipo = caixaMostrarSenhas.checked ? "text" : "password";
        campoSenha("nova_senha").type = tipo;
        campoSenha("confirmar_senha").type = tipo;
    }

    // Apaga as senhas, desmarca "Mostrar senhas" e tira as mensagens de erro.
    function limparFormularioSenha() {
        formularioSenha.reset();
        aplicarVisibilidadeDasSenhas();
        Cantina.limparErros(formularioSenha);
    }

    function abrirRedefinicao(usuario) {
        usuarioSelecionado = usuario;
        limparFormularioSenha();
        document.getElementById("senha-usuario").textContent = `${usuario.nome} (matrícula ${usuario.matricula})`;
        abrirModal(modalSenha, campoSenha("nova_senha"));
    }

    // Mesma regra de senha do servidor (que valida de novo). A senha não é
    // aparada: espaços digitados fazem parte dela.
    function validarRedefinicao() {
        const erros = {};
        const novaSenha = campoSenha("nova_senha").value;
        const confirmacao = campoSenha("confirmar_senha").value;

        if (!novaSenha) erros.nova_senha = "Informe a nova senha.";
        else if (!Cantina.validarSenha(novaSenha)) {
            erros.nova_senha = "A senha precisa ter de 8 a 72 caracteres, com pelo menos uma letra e um número.";
        }

        if (!confirmacao) erros.confirmar_senha = "Digite a senha de novo para confirmar.";
        else if (confirmacao !== novaSenha) erros.confirmar_senha = "As senhas não são iguais.";
        return erros;
    }

    async function salvarSenha() {
        const usuario = usuarioSelecionado;
        if (!usuario) return;
        Cantina.limparErros(formularioSenha);
        if (Cantina.exibirErros(formularioSenha, validarRedefinicao())) return;

        const dados = {
            nova_senha: campoSenha("nova_senha").value,
            confirmar_senha: campoSenha("confirmar_senha").value,
        };
        const botaoSalvar = formularioSenha.querySelector("button[type='submit']");
        await Cantina.comBotaoOcupado(botaoSalvar, "Redefinindo…", async () => {
            try {
                const resultado = await Cantina.requisitar(`${API}/${usuario.id_usuario}/senha`, { method: "POST", json: dados });
                // Fechar o modal apaga os campos e devolve o foco ao botão "Redefinir senha" da linha.
                fecharModal(modalSenha);
                // A mensagem cita só o nome: a senha nunca aparece na tela.
                Cantina.mostrarMensagem(mensagemApi, `Senha de ${resultado.usuario?.nome || usuario.nome} redefinida.`, "sucesso");
            } catch (erro) {
                if (Object.keys(erro.campos || {}).length) {
                    Cantina.exibirErros(formularioSenha, erro.campos);
                } else {
                    formularioSenha.querySelector(".feedback-form").textContent = tratarErro(erro);
                }
            }
        });
    }

    caixaMostrarSenhas.addEventListener("change", aplicarVisibilidadeDasSenhas);

    // Enter em uma caixa de seleção enviaria o formulário: aqui ele só marca ou
    // desmarca a caixa, porque a senha é gravada apenas pelo clique no botão.
    caixaMostrarSenhas.addEventListener("keydown", (evento) => {
        if (evento.key !== "Enter") return;
        evento.preventDefault();
        caixaMostrarSenhas.checked = !caixaMostrarSenhas.checked;
        aplicarVisibilidadeDasSenhas();
    });

    // ---------- formulários: máscaras, erros e gravação só pelo botão ----------

    [formularioEdicao, formularioAjuste, formularioSenha].forEach((formulario) => {
        Cantina.bloquearEnvioPorEnter(formulario);
        Cantina.ligarLimpezaDeErros(formulario);
    });
    Cantina.ligarSomenteDigitos(campoEdicao("matricula"), 20);
    Cantina.ligarMascaraMoeda(campoAjuste("valor_centavos"));

    // Depois da máscara: o saldo resultante acompanha o valor já formatado.
    campoAjuste("valor_centavos").addEventListener("input", atualizarSaldoResultante);
    formularioAjuste.querySelectorAll("input[name='tipo']").forEach((opcao) => {
        opcao.addEventListener("change", () => {
            Cantina.limparErroCampo(formularioAjuste, "valor_centavos");
            atualizarSaldoResultante();
        });
    });

    formularioEdicao.addEventListener("submit", (evento) => {
        evento.preventDefault();
        if (evento.submitter?.type !== "submit") return;
        salvarEdicao();
    });

    formularioAjuste.addEventListener("submit", (evento) => {
        evento.preventDefault();
        if (evento.submitter?.type !== "submit") return;
        salvarAjuste();
    });

    formularioSenha.addEventListener("submit", (evento) => {
        evento.preventDefault();
        if (evento.submitter?.type !== "submit") return;
        salvarSenha();
    });

    // ---------- ações da tabela ----------

    corpoTabela.addEventListener("click", (evento) => {
        const botao = evento.target.closest("button[data-acao]");
        if (!botao) return;
        const usuario = usuariosPorId.get(botao.closest("tr")?.dataset.usuarioId);
        if (!usuario) return;
        Cantina.mostrarMensagem(mensagemApi, "");
        if (botao.dataset.acao === "editar") abrirEdicao(usuario);
        else if (botao.dataset.acao === "ajustar") abrirAjuste(usuario);
        else if (botao.dataset.acao === "senha") abrirRedefinicao(usuario);
        else if (botao.dataset.acao === "situacao") abrirSituacao(usuario);
    });

    carregarLista();
});
