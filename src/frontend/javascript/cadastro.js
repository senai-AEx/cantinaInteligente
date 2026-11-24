// Tela de cadastro: aplica as máscaras, confere os campos com as regras do
// contrato da API e cria a conta. O cadastro só é gravado pelo clique no botão.
document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const formulario = document.getElementById("form-cadastro");
    const feedback = formulario.querySelector(".feedback-form");
    const botao = document.getElementById("botao-cadastro");
    const mostrarSenhas = document.getElementById("mostrar-senhas-cadastro");
    const regrasSenha = document.getElementById("regras-senha");
    const campos = {
        nome: formulario.elements.namedItem("nome"),
        matricula: formulario.elements.namedItem("matricula"),
        cpf: formulario.elements.namedItem("cpf"),
        email: formulario.elements.namedItem("email"),
        senha: formulario.elements.namedItem("senha"),
        confirmar_senha: formulario.elements.namedItem("confirmar_senha"),
    };
    let enviando = false;

    // ---------- máscaras ----------

    Cantina.ligarSomenteDigitos(campos.matricula, 20);
    Cantina.ligarMascaraCpf(campos.cpf);

    // ---------- dica da senha ----------

    // Marca cada regra como cumprida (✓) ou não (○) enquanto o usuário digita.
    function atualizarRegrasDaSenha() {
        const senha = campos.senha.value;
        const cumpridas = {
            tamanho: senha.length >= 8 && senha.length <= 72,
            letra: /[A-Za-zÀ-ÿ]/.test(senha),
            numero: /\d/.test(senha),
        };
        regrasSenha.querySelectorAll("[data-regra]").forEach((item) => {
            const cumprida = cumpridas[item.dataset.regra];
            item.classList.toggle("regra-cumprida", cumprida);
            item.querySelector(".marca-regra").textContent = cumprida ? "✓" : "○";
            item.querySelector("[data-estado-regra]").textContent = cumprida ? "(cumprida)" : "(falta cumprir)";
        });
    }

    campos.senha.addEventListener("input", atualizarRegrasDaSenha);

    mostrarSenhas.addEventListener("change", () => {
        const tipo = mostrarSenhas.checked ? "text" : "password";
        campos.senha.type = tipo;
        campos.confirmar_senha.type = tipo;
    });

    // ---------- validação (mesmas regras do servidor) ----------

    function lerDados() {
        return {
            nome: campos.nome.value.trim(),
            matricula: Cantina.somenteDigitos(campos.matricula.value),
            // O CPF segue para a API só com os 11 números.
            cpf: Cantina.somenteDigitos(campos.cpf.value),
            email: campos.email.value.trim(),
            senha: campos.senha.value,
            confirmar_senha: campos.confirmar_senha.value,
        };
    }

    function validar(dados) {
        const erros = {};

        if (!dados.nome) erros.nome = "Informe seu nome completo.";
        else if (dados.nome.length < 3) erros.nome = "O nome precisa ter pelo menos 3 caracteres.";
        else if (dados.nome.length > 100) erros.nome = "O nome pode ter no máximo 100 caracteres.";
        else if (!/\p{L}/u.test(dados.nome)) erros.nome = "O nome precisa ter pelo menos uma letra.";

        if (!dados.matricula) erros.matricula = "Informe sua matrícula.";
        else if (dados.matricula.length < 4) erros.matricula = "A matrícula precisa ter pelo menos 4 dígitos.";
        else if (dados.matricula.length > 20) erros.matricula = "A matrícula pode ter no máximo 20 dígitos.";

        if (!dados.cpf) erros.cpf = "Informe seu CPF.";
        else if (dados.cpf.length !== 11) erros.cpf = "O CPF precisa ter 11 números.";
        else if (!Cantina.validarCpf(dados.cpf)) erros.cpf = "CPF inválido. Confira os números digitados.";

        if (!dados.email) erros.email = "Informe seu e-mail.";
        else if (dados.email.length > 150) erros.email = "O e-mail pode ter no máximo 150 caracteres.";
        else if (!Cantina.validarEmail(dados.email)) erros.email = "Informe um e-mail válido, como nome@exemplo.com.";

        if (!dados.senha) erros.senha = "Crie uma senha.";
        else if (!Cantina.validarSenha(dados.senha)) {
            erros.senha = "A senha precisa ter de 8 a 72 caracteres, com pelo menos uma letra e um número.";
        }

        if (!dados.confirmar_senha) erros.confirmar_senha = "Digite a senha de novo para confirmar.";
        else if (dados.confirmar_senha !== dados.senha) erros.confirmar_senha = "As senhas não são iguais.";

        return erros;
    }

    // ---------- envio ----------

    async function criarConta() {
        if (enviando) return;
        Cantina.limparErros(formulario);

        const dados = lerDados();
        if (Cantina.exibirErros(formulario, validar(dados))) return;

        enviando = true;
        try {
            await Cantina.comBotaoOcupado(botao, "Criando conta...", () =>
                Cantina.requisitar("/api/auth/cadastro", { method: "POST", json: dados }));
            // O cadastro já deixa o usuário logado.
            window.location.href = "/html/catalogo_produtos.html?aviso=bem-vindo";
        } catch (erro) {
            enviando = false;
            // Erros por campo vindos da API (inclusive matrícula, CPF ou e-mail já cadastrados).
            if (Object.keys(erro.campos || {}).length) {
                Cantina.exibirErros(formulario, erro.campos);
                return;
            }
            Cantina.mostrarMensagem(feedback, erro.message, "erro");
        }
    }

    // Regra do sistema: Enter em um campo não grava; só o clique no botão "Criar conta".
    Cantina.bloquearEnvioPorEnter(formulario);
    Cantina.ligarLimpezaDeErros(formulario);

    formulario.addEventListener("submit", (evento) => {
        evento.preventDefault();
        criarConta();
    });

    atualizarRegrasDaSenha();

    // Quem já está logado não precisa criar outra conta: segue para a sua área.
    Cantina.sessao().then((usuario) => {
        if (!usuario) return;
        window.location.replace(usuario.perfil === "ADMINISTRADOR"
            ? "/html/painel_adm.html"
            : "/html/catalogo_produtos.html");
    });
});
