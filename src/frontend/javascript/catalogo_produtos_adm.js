// FUNÇÕES PARA O MODAL DE CADASTRO DE PRODUTOS

document.addEventListener("DOMContentLoaded", function () {

    const botaoAbrir = document.getElementById("abrir-cadastro-produto");
    const modal = document.getElementById("modal-cadastro-produto");
    const botaoFechar = document.getElementById("fechar-cadastro-produto");

    botaoAbrir.addEventListener("click", function () {
        modal.classList.add("aberto");
        modal.setAttribute("aria-hidden", "false");
    });

    botaoFechar.addEventListener("click", function () {
        modal.classList.remove("aberto");
        modal.setAttribute("aria-hidden", "true");
    });

    // MODAL DE EDIÇÃO DE PRODUTOS

    const modalEditar = document.getElementById("modal-editar-produto");
    const botaoFecharEditar = document.getElementById("fechar-editar-produto");
    const botoesEditar = document.querySelectorAll(".acoes-produto .botao-principal");

    botoesEditar.forEach(function (botao) {
        botao.addEventListener("click", function () {
            modalEditar.classList.add("aberto");
            modalEditar.setAttribute("aria-hidden", "false");
        });
    });

    botaoFecharEditar.addEventListener("click", function () {
        modalEditar.classList.remove("aberto");
        modalEditar.setAttribute("aria-hidden", "true");
    });

    // MODAL DE EXCLUSÃO DE PRODUTOS

    // MODAL DE EXCLUSÃO DE PRODUTOS

    const modalExcluir = document.getElementById("modal-excluir-produto");
    const botaoFecharExcluir = document.getElementById("fechar-excluir-produto");
    const botaoConfirmarSenhaExcluir = document.getElementById("botao-confirmar-senha-exclusao");
    const campoSenhaExcluir = document.getElementById("senha-confirmacao-exclusao");

    let produtoSelecionadoParaExcluir = null;

    const botoesExcluir = document.querySelectorAll(".acoes-produto .botao-excluir");

    botoesExcluir.forEach(function (botao) {
        botao.addEventListener("click", function () {
            produtoSelecionadoParaExcluir = botao.closest(".card-produto");

            campoSenhaExcluir.value = "";

            modalExcluir.classList.add("aberto");
            modalExcluir.setAttribute("aria-hidden", "false");

            campoSenhaExcluir.focus();
        });
    });

    function fecharModalExcluir() {
        modalExcluir.classList.remove("aberto");
        modalExcluir.setAttribute("aria-hidden", "true");

        campoSenhaExcluir.value = "";
        produtoSelecionadoParaExcluir = null;
    }

    botaoFecharExcluir.addEventListener("click", fecharModalExcluir);

    botaoConfirmarSenhaExcluir.addEventListener("click", function () {
        if (!campoSenhaExcluir.value.trim()) {
            campoSenhaExcluir.focus();
            return;
        }

        // A validação real da senha será implementada no backend.
        alert("A validação da senha ainda não foi implementada.");
    });

});