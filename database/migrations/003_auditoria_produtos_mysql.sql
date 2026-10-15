
USE cantina_inteligente;

CREATE TABLE IF NOT EXISTS auditoria_produtos (
    id_auditoria INT AUTO_INCREMENT PRIMARY KEY,

    id_produto INT NOT NULL,

    acao ENUM(
        'INCLUIR',
        'ALTERAR',
        'INATIVAR',
        'REATIVAR'
    ) NOT NULL,

    autor VARCHAR(100) NOT NULL,
    origem VARCHAR(100) NOT NULL,

    antes_json JSON NULL,
    depois_json JSON NULL,

    registrado_em DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_auditoria_produto
        FOREIGN KEY (id_produto)
        REFERENCES produtos(id_produto)
        ON DELETE RESTRICT
);

CREATE INDEX idx_auditoria_produto
ON auditoria_produtos (id_produto, registrado_em);
