
CREATE TABLE IF NOT EXISTS produtos (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,

    codigo_produto VARCHAR(32) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(500) NOT NULL DEFAULT '',
    categoria VARCHAR(50) NOT NULL,

    preco_centavos INT NOT NULL,

    quantidade_estoque INT NOT NULL DEFAULT 0,
    estoque_minimo INT NOT NULL DEFAULT 0,
    estoque_maximo INT NOT NULL DEFAULT 0,

    validade DATE NULL,
    foto_caminho VARCHAR(255) NULL,

    zero_lactose BOOLEAN NOT NULL DEFAULT FALSE,
    zero_acucar BOOLEAN NOT NULL DEFAULT FALSE,

    status ENUM('ATIVO', 'INATIVO')
        NOT NULL DEFAULT 'ATIVO',

    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_codigo
        CHECK (CHAR_LENGTH(TRIM(codigo_produto)) BETWEEN 3 AND 32),

    CONSTRAINT chk_nome
        CHECK (CHAR_LENGTH(TRIM(nome)) BETWEEN 2 AND 100),

    CONSTRAINT chk_categoria
        CHECK (CHAR_LENGTH(TRIM(categoria)) BETWEEN 2 AND 50),

    CONSTRAINT chk_preco
        CHECK (preco_centavos > 0),

    CONSTRAINT chk_quantidade
        CHECK (quantidade_estoque >= 0),

    CONSTRAINT chk_estoque_minimo
        CHECK (estoque_minimo >= 0),

    CONSTRAINT chk_estoque_maximo
        CHECK (estoque_maximo >= estoque_minimo),

    CONSTRAINT chk_descricao
        CHECK (CHAR_LENGTH(descricao) <= 500)
);

CREATE INDEX idx_produtos_status_nome
ON produtos (status, nome);
