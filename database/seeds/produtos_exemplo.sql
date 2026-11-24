-- Produtos fictícios para desenvolvimento e demonstração.
-- Aplicar com `python scripts/banco.py semear` ou executando este arquivo no MySQL Workbench.
-- Valores em centavos: 750 = R$ 7,50. Frutas recebem os selos automaticamente.
USE cantina_inteligente;

INSERT INTO produtos (
    nome, descricao, categoria,
    preco_compra_centavos, preco_venda_centavos, quantidade_estoque,
    foto_caminho, zero_lactose, zero_acucar, status
) VALUES
('Suco de Laranja', 'Suco de laranja integral 300 ml.', 'Bebidas', 480, 750, 20, NULL, FALSE, FALSE, 'ATIVO'),
('Sanduíche Natural', 'Sanduíche natural de frango com alface e cenoura.', 'Lanches', 800, 1200, 15, NULL, FALSE, FALSE, 'ATIVO'),
('Barra de Cereal', 'Barra de cereal de castanhas, embalagem individual.', 'Doces', 250, 450, 40, NULL, FALSE, FALSE, 'ATIVO'),
('Maçã', 'Maçã Fuji, unidade.', 'Frutas', 150, 300, 25, NULL, TRUE, TRUE, 'ATIVO');
