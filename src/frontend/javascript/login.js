// Tela de login: confere os campos, entra no sistema e leva o usuário para a área certa.
document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const formulario = document.getElementById("form-login");
    const feedback = formulario.querySelector(".feedback-form");
    const botao = formulario.querySelector("button[type='submit']");
    const campoIdentificador = formulario.elements.namedItem("identificador");
    const campoSenha = formulario.elements.namedItem("senha");
    const mostrarSenha = document.getElementById("mostrar-senha-login");
    const aviso = document.getElementById("aviso-login");
    // Tela que o usuário queria abrir antes de ser trazido para o login.
    const destinoPedido = new URLSearchParams(window.location.search).get("destino");
    let enviando = false;

    // Para onde ir depois de entrar: o destino pedido (se for interno) ou a área do perfil.
    function paginaInicial(usuario) {
        const padrao = usuario.perfil === "ADMINISTRADOR"
            ? "/html/painel_adm.html"
            : "/html/catalogo_produtos.html";
        return Cantina.destinoSeguro(destinoPedido, padrao);
    }

    // CPF digitado com pontos e traço segue só com os números; matrícula e e-mail seguem como estão.
    function normalizarIdentificador(texto) {
        const valor = texto.trim();
        return /^[\d.\-\s]+$/.test(valor) ? Cantina.somenteDigitos(valor) : valor;
    }

    function validar(dados) {
        const erros = {};
        if (!dados.identificador) erros.identificador = "Informe sua matrícula, seu e-mail ou seu CPF.";
        if (!dados.senha) erros.senha = "Informe sua senha.";
        return erros;
    }

    async function entrar() {
        if (enviando) return;
        Cantina.limparErros(formulario);

        const dados = {
            identificador: normalizarIdentificador(campoIdentificador.value),
            senha: campoSenha.value,
        };
        if (Cantina.exibirErros(formulario, validar(dados))) return;

        enviando = true;
        try {
            const resultado = await Cantina.comBotaoOcupado(botao, "Entrando...", () =>
                Cantina.requisitar("/api/auth/login", { method: "POST", json: dados }));
            window.location.href = paginaInicial(resultado.usuario || {});
        } catch (erro) {
            enviando = false;
            if (erro.status === 422 && Object.keys(erro.campos || {}).length) {
                Cantina.exibirErros(formulario, erro.campos);
                return;
            }
            // 401 (dados incorretos), 403 (usuário inativo) ou falha de comunicação.
            Cantina.mostrarMensagem(feedback, erro.message, "erro");
            if (erro.status === 401) {
                campoSenha.focus();
                campoSenha.select();
            }
        }
    }

    // No login, Enter em um campo pode enviar: não é gravação de cadastro.
    formulario.addEventListener("submit", (evento) => {
        evento.preventDefault();
        entrar();
    });

    mostrarSenha.addEventListener("change", () => {
        campoSenha.type = mostrarSenha.checked ? "text" : "password";
    });

    Cantina.ligarLimpezaDeErros(formulario);

    if (destinoPedido) {
        Cantina.mostrarMensagem(aviso, "Entre com a sua conta para continuar.");
    }

    // Quem já está logado não precisa ver esta tela.
    Cantina.sessao().then((usuario) => {
        if (usuario) window.location.replace(paginaInicial(usuario));
    });
});
