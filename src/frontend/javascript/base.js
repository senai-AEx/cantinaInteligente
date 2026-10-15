// FUNÇÃO P/ CARREGAR HEADER E FOOTER DO ARQUIVO PADRÃO (base.html)
// EM OUTRAS PGS

async function carregarBase() {
    try {
        const resposta = await fetch("base.html");

        if (!resposta.ok) {
            throw new Error("Não foi possível carregar o base.html");
        }

        const html = await resposta.text();
        const documento = new DOMParser().parseFromString(html, "text/html");

        const header = documento.querySelector("header");
        const footer = documento.querySelector("footer");

        const localHeader = document.getElementById("header-container");
        const localFooter = document.getElementById("footer-container");

        if (header && localHeader) {
            localHeader.replaceWith(header);
        }

        if (footer && localFooter) {
            localFooter.replaceWith(footer);
        }
        document.dispatchEvent(new Event("layoutbase:carregada"));
    } catch (erro) {
        console.error("Erro ao carregar header e footer:", erro);
    }
}

carregarBase();