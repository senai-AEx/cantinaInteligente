// Tela inicial: troca os botões de visitante pela saudação, pelo saldo e pelos atalhos
// de quem já entrou. O HTML sozinho mostra a versão de visitante (funciona sem JavaScript);
// aqui só se alternam os blocos com o atributo hidden.
document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const blocoVisitante = document.getElementById("acoes-visitante");
    const blocoLogado = document.getElementById("acoes-logado");
    const saudacao = document.getElementById("saudacao-inicio");
    const saldo = document.getElementById("saldo-inicio");
    const botaoPainel = document.getElementById("botao-painel");

    // usuario: o usuário logado ({nome, perfil, saldo_centavos, ...}) ou null para visitante.
    function mostrarSessao(usuario) {
        const logado = Boolean(usuario);
        if (logado) {
            const primeiroNome = String(usuario.nome || "").trim().split(/\s+/)[0];
            saudacao.textContent = primeiroNome ? `Olá, ${primeiroNome}!` : "Olá!";
            saldo.textContent = Cantina.formatarPreco(usuario.saldo_centavos);
        }
        // O atalho do painel só aparece para administradores.
        botaoPainel.hidden = !logado || usuario.perfil !== "ADMINISTRADOR";
        blocoVisitante.hidden = logado;
        blocoLogado.hidden = !logado;
    }

    async function iniciar() {
        // Cantina.pronta() espera o cabeçalho e a sessão e devolve o usuário ou null.
        mostrarSessao(await Cantina.pronta());
    }

    iniciar();

    // Ao voltar pelo botão do navegador, a tela pode vir guardada de antes do login
    // ou da saída: confere a sessão de novo.
    window.addEventListener("pageshow", async (evento) => {
        if (evento.persisted) mostrarSessao(await Cantina.atualizarSessao());
    });
});
