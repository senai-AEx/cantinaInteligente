-- Execute depois da migração 002_produtos_mysql.sql.
USE cantina_inteligente;

CREATE TABLE IF NOT EXISTS auditoria_produtos (
    id_auditoria INT NOT NULL AUTO_INCREMENT,
    id_produto INT NOT NULL,
    acao ENUM('INCLUIR', 'ALTERAR', 'INATIVAR', 'REATIVAR') NOT NULL,
    autor VARCHAR(100) NOT NULL,
    origem VARCHAR(100) NOT NULL,
    antes_json JSON NULL,
    depois_json JSON NOT NULL,
    registrado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id_auditoria),
    CONSTRAINT fk_auditoria_produto
        FOREIGN KEY (id_produto)
        REFERENCES produtos(id_produto)
        ON DELETE RESTRICT,
    INDEX idx_auditoria_produto (id_produto, registrado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;