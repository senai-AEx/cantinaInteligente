-- Execute uma única vez depois da migração 003_auditoria_produtos_mysql.sql.
-- A auditoria fica preservada mesmo quando o produto é excluído definitivamente.
USE cantina_inteligente;

ALTER TABLE auditoria_produtos
    DROP FOREIGN KEY fk_auditoria_produto;

ALTER TABLE auditoria_produtos
    MODIFY acao ENUM('INCLUIR', 'ALTERAR', 'INATIVAR', 'REATIVAR', 'EXCLUIR') NOT NULL;
