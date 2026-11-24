// Tela inicial do painel: resumo da cantina e atalhos. Só administradores passam daqui.
document.addEventListener("DOMContentLoaded", async () => {
    // Quem não está logado vai para o login; quem não é administrador volta ao catálogo.
    await Cantina.exigirAdministrador();

    const mensagem = document.getElementById("mensagem-painel");
    try {
        const [produtos, resposta] = await Promise.all([
            Cantina.requisitar("/api/produtos?status=TODOS"),
            Cantina.requisitar("/api/admin/usuarios?status=ATIVO"),
        ]);
        const aVenda = produtos.filter((produto) => produto.status === "ATIVO");

        document.getElementById("total-produtos-ativos").textContent = aVenda.length;
        document.getElementById("total-sem-estoque").textContent =
            aVenda.filter((produto) => produto.quantidade_estoque === 0).length;
        document.getElementById("total-produtos-inativos").textContent = produtos.length - aVenda.length;
        document.getElementById("total-usuarios-ativos").textContent = resposta.usuarios.length;
    } catch (erro) {
        Cantina.mostrarMensagem(mensagem, "Não foi possível carregar o resumo. Recarregue a página.", "erro");
    }
});
