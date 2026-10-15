-- MySQL 8.0.16+ (CHECK constraints are enforced from 8.0.16).
-- Execute uma única vez em um banco novo; a migração 003 depende desta tabela.
CREATE DATABASE IF NOT EXISTS cantina_inteligente
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE cantina_inteligente;

CREATE TABLE IF NOT EXISTS produtos (
    id_produto INT NOT NULL AUTO_INCREMENT,
    codigo_produto VARCHAR(32) NOT NULL,
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
    status ENUM('ATIVO', 'INATIVO') NOT NULL DEFAULT 'ATIVO',
    criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id_produto),
    CONSTRAINT uq_produtos_codigo UNIQUE (codigo_produto),
    CONSTRAINT chk_produtos_codigo
        CHECK (CHAR_LENGTH(TRIM(codigo_produto)) BETWEEN 3 AND 32),
    CONSTRAINT chk_produtos_nome
        CHECK (CHAR_LENGTH(TRIM(nome)) BETWEEN 2 AND 100),
    CONSTRAINT chk_produtos_categoria
        CHECK (CHAR_LENGTH(TRIM(categoria)) BETWEEN 2 AND 50),
    CONSTRAINT chk_produtos_preco CHECK (preco_centavos > 0),
    CONSTRAINT chk_produtos_quantidade CHECK (quantidade_estoque >= 0),
    CONSTRAINT chk_produtos_estoque_minimo CHECK (estoque_minimo >= 0),
    CONSTRAINT chk_produtos_estoque_maximo
        CHECK (estoque_maximo >= estoque_minimo),
    CONSTRAINT chk_produtos_descricao
        CHECK (CHAR_LENGTH(descricao) <= 500),
    CONSTRAINT chk_produtos_lactose CHECK (zero_lactose IN (0, 1)),
    CONSTRAINT chk_produtos_acucar CHECK (zero_acucar IN (0, 1)),
    INDEX idx_produtos_status_nome (status, nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;