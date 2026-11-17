-- Esquema completo e atual do banco (equivale às migrações 002 a 005 aplicadas).
-- Use para criar o banco do zero manualmente (MySQL Workbench, por exemplo).
-- Quem usa `make up` não precisa deste arquivo: o Make aplica as migrações.
-- Requer MySQL 8.0.16+ (restrições CHECK).
CREATE DATABASE IF NOT EXISTS cantina_inteligente
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

USE cantina_inteligente;

-- PRODUTOS
-- id_produto é gerado automaticamente; não existe código manual.
-- "Excluir" no sistema apenas muda status para INATIVO: o registro nunca é apagado.
CREATE TABLE IF NOT EXISTS produtos (
    id_produto INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(500) NOT NULL DEFAULT '',
    categoria VARCHAR(50) NOT NULL,
    preco_compra_centavos INT NOT NULL,
    preco_venda_centavos INT NOT NULL,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    foto_caminho VARCHAR(255) NULL,
    zero_lactose BOOLEAN NOT NULL DEFAULT FALSE,
    zero_acucar BOOLEAN NOT NULL DEFAULT FALSE,
    status ENUM('ATIVO', 'INATIVO') NOT NULL DEFAULT 'ATIVO',
    criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),

    PRIMARY KEY (id_produto),

    CONSTRAINT chk_produtos_nome
        CHECK (CHAR_LENGTH(TRIM(nome)) BETWEEN 2 AND 100),
    CONSTRAINT chk_produtos_categoria
        CHECK (CHAR_LENGTH(TRIM(categoria)) BETWEEN 2 AND 50),
    CONSTRAINT chk_produtos_preco_compra
        CHECK (preco_compra_centavos > 0),
    CONSTRAINT chk_produtos_preco_venda
        CHECK (preco_venda_centavos > 0),
    CONSTRAINT chk_produtos_quantidade
        CHECK (quantidade_estoque >= 0),
    CONSTRAINT chk_produtos_descricao
        CHECK (CHAR_LENGTH(descricao) <= 500),
    CONSTRAINT chk_produtos_lactose
        CHECK (zero_lactose IN (0, 1)),
    CONSTRAINT chk_produtos_acucar
        CHECK (zero_acucar IN (0, 1)),

    INDEX idx_produtos_status_nome (status, nome)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;


-- AUDITORIA DOS PRODUTOS (RNF09)
-- 'EXCLUIR' permanece no ENUM apenas para registros antigos da AV04.
CREATE TABLE IF NOT EXISTS auditoria_produtos (
    id_auditoria INT NOT NULL AUTO_INCREMENT,
    id_produto INT NOT NULL,
    acao ENUM('INCLUIR', 'ALTERAR', 'INATIVAR', 'REATIVAR', 'EXCLUIR') NOT NULL,
    autor VARCHAR(100) NOT NULL,
    origem VARCHAR(100) NOT NULL,
    antes_json JSON NULL,
    depois_json JSON NOT NULL,
    registrado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    PRIMARY KEY (id_auditoria),
    INDEX idx_auditoria_produto (id_produto, registrado_em)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;
