-- Adequa a tabela de produtos às devolutivas da AV04 (entrega AV05).
-- Execute uma única vez depois da 004_auditoria_exclusao_mysql.sql.
--   * remove o código manual: o identificador é somente o id_produto (AUTO_INCREMENT);
--   * remove validade e estoque mínimo/máximo: fica só a quantidade em estoque;
--   * troca o preço único por preço de compra e preço de venda.
-- Produtos já cadastrados recebem preço de compra igual ao de venda; revise-os na tela.
USE cantina_inteligente;

-- Restrições CHECK precisam sair antes de apagar ou renomear as colunas que usam.
ALTER TABLE produtos
    DROP CHECK chk_produtos_codigo,
    DROP CHECK chk_produtos_estoque_minimo,
    DROP CHECK chk_produtos_estoque_maximo,
    DROP CHECK chk_produtos_preco;

ALTER TABLE produtos
    DROP COLUMN codigo_produto,
    DROP COLUMN estoque_minimo,
    DROP COLUMN estoque_maximo,
    DROP COLUMN validade,
    RENAME COLUMN preco_centavos TO preco_venda_centavos,
    ADD COLUMN preco_compra_centavos INT NULL AFTER categoria;

UPDATE produtos
SET preco_compra_centavos = preco_venda_centavos
WHERE id_produto > 0;

-- Regra nova: frutas recebem os selos automaticamente (a collation ignora maiúsculas/acentos).
UPDATE produtos
SET zero_lactose = TRUE, zero_acucar = TRUE
WHERE id_produto > 0 AND categoria IN ('Fruta', 'Frutas');

ALTER TABLE produtos
    MODIFY preco_compra_centavos INT NOT NULL,
    ADD CONSTRAINT chk_produtos_preco_compra CHECK (preco_compra_centavos > 0),
    ADD CONSTRAINT chk_produtos_preco_venda CHECK (preco_venda_centavos > 0);
