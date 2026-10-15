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

});