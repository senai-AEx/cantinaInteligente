// FUNÇÕES PARA O MODAL DE PAGAMENTO 

const modal = document.getElementById("modal-pix");
const modalCorpo = document.getElementById("modal-corpo");

const botaoFinalizar = document.querySelector(".botao-finalizar");
const botaoFechar = document.getElementById("fechar-modal-pix");
const botaoGerarPix = document.getElementById("gerar-pix");
const botaoVoltar = document.getElementById("voltar-editar-valor");
const botaoCopiarPix = document.getElementById("copiar-pix");

const areaQrcode = document.getElementById("area-qrcode");
const valorPagamento = document.getElementById("valor-pagamento");
const valorPagamentoFixo = document.getElementById("valor-pagamento-fixo");
const rotuloValorPagamento = document.getElementById("rotulo-valor-pagamento");
const codigoPix = document.getElementById("codigo-pix");

// Abre o modal
botaoFinalizar.addEventListener("click", () => {
    modal.classList.add("aberto");
    modal.setAttribute("aria-hidden", "false");
});

// Retorna à etapa de escolha do valor
function voltarParaEdicao() {
    modalCorpo.classList.remove("pix-gerado");

    areaQrcode.hidden = true;
    botaoGerarPix.hidden = false;
    botaoVoltar.hidden = true;

    valorPagamento.hidden = false;
    valorPagamentoFixo.hidden = true;
    valorPagamentoFixo.textContent = "";

    rotuloValorPagamento.textContent = "Quanto você deseja pagar?";
}

// Fecha o modal e restaura o estado inicial
function fecharModal() {
    modal.classList.remove("aberto");
    modal.setAttribute("aria-hidden", "true");
    voltarParaEdicao();
}

botaoFechar.addEventListener("click", fecharModal);

modal.addEventListener("click", (evento) => {
    if (evento.target === modal) {
        fecharModal();
    }
});

// Confirma o valor escolhido
botaoGerarPix.addEventListener("click", () => {
    const valor = Number(valorPagamento.value);

    if (!Number.isFinite(valor) || valor <= 0) {
        alert("Informe um valor válido maior que zero.");
        valorPagamento.focus();
        return;
    }

    // Exibe o valor confirmado como texto
    valorPagamentoFixo.textContent = valor.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });

    valorPagamento.hidden = true;
    valorPagamentoFixo.hidden = false;

    rotuloValorPagamento.textContent = "Valor que você está pagando:";

    // Exibe o QR Code e reorganiza o modal
    modalCorpo.classList.add("pix-gerado");
    areaQrcode.hidden = false;
    botaoGerarPix.hidden = true;
    botaoVoltar.hidden = false;
});

// Permite alterar o valor escolhido
botaoVoltar.addEventListener("click", voltarParaEdicao);

// Copia o código Pix quando estiver disponível
botaoCopiarPix.addEventListener("click", async () => {
    const codigo = codigoPix.value.trim();

    if (!codigo) {
        alert("O código Pix ainda não está disponível.");
        return;
    }

    try {
        await navigator.clipboard.writeText(codigo);
        alert("Código Pix copiado!");
    } catch {
        codigoPix.select();
        alert("Selecione e copie o código Pix manualmente.");
    }
});