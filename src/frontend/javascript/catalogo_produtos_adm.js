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

});