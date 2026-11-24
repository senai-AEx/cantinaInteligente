-- Esquema completo e atual do banco (equivale às migrações 002 a 006 aplicadas).
-- Use para criar o banco do zero manualmente (MySQL Workbench, por exemplo).
-- Quem usa `python iniciar.py` não precisa deste arquivo: o próprio sistema aplica as migrações.
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


-- ===== USUÁRIOS, CARTEIRA, COMPRAS E MOVIMENTAÇÕES (migração 006) =====

-- PERFIS DE ACESSO
CREATE TABLE IF NOT EXISTS tipos_usuario (
    id_tipo_usuario TINYINT UNSIGNED NOT NULL,
    nome VARCHAR(30) NOT NULL,
    PRIMARY KEY (id_tipo_usuario),
    CONSTRAINT uq_tipos_usuario_nome UNIQUE (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT IGNORE INTO tipos_usuario (id_tipo_usuario, nome) VALUES
    (1, 'ADMINISTRADOR'),
    (2, 'CLIENTE');

-- USUÁRIOS
-- Login por matrícula, e-mail ou CPF: os três são únicos.
-- A senha nunca é guardada em texto puro, apenas o hash.
-- Usuários não são apagados: "excluir" muda status para INATIVO.
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    matricula VARCHAR(20) NOT NULL,
    cpf CHAR(11) NOT NULL,
    email VARCHAR(150) NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    id_tipo_usuario TINYINT UNSIGNED NOT NULL DEFAULT 2,
    status ENUM('ATIVO', 'INATIVO') NOT NULL DEFAULT 'ATIVO',
    criado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuarios_matricula UNIQUE (matricula),
    CONSTRAINT uq_usuarios_cpf UNIQUE (cpf),
    CONSTRAINT uq_usuarios_email UNIQUE (email),
    CONSTRAINT fk_usuarios_tipo FOREIGN KEY (id_tipo_usuario)
        REFERENCES tipos_usuario (id_tipo_usuario),
    CONSTRAINT chk_usuarios_nome CHECK (CHAR_LENGTH(TRIM(nome)) BETWEEN 3 AND 100),
    CONSTRAINT chk_usuarios_matricula CHECK (CHAR_LENGTH(matricula) BETWEEN 4 AND 20),
    CONSTRAINT chk_usuarios_cpf CHECK (CHAR_LENGTH(cpf) = 11),
    INDEX idx_usuarios_status_nome (status, nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- CARTEIRA (crédito do usuário)
-- Uma carteira por usuário. O saldo nunca fica negativo.
CREATE TABLE IF NOT EXISTS carteiras (
    id_carteira INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    saldo_centavos INT NOT NULL DEFAULT 0,
    atualizado_em DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id_carteira),
    CONSTRAINT uq_carteiras_usuario UNIQUE (id_usuario),
    CONSTRAINT fk_carteiras_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario),
    CONSTRAINT chk_carteiras_saldo CHECK (saldo_centavos >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- COMPRAS
-- chave_idempotencia: gerada pela tela; repetir a confirmação não duplica a compra.
CREATE TABLE IF NOT EXISTS compras (
    id_compra INT NOT NULL AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    valor_total_centavos INT NOT NULL,
    chave_idempotencia CHAR(36) NOT NULL,
    data_hora DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id_compra),
    CONSTRAINT uq_compras_chave UNIQUE (chave_idempotencia),
    CONSTRAINT fk_compras_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios (id_usuario),
    CONSTRAINT chk_compras_total CHECK (valor_total_centavos > 0),
    INDEX idx_compras_usuario_data (id_usuario, data_hora),
    INDEX idx_compras_data (data_hora)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ITENS DA COMPRA
-- Guarda o preço de venda e o custo do momento da compra, para os relatórios
-- não mudarem quando o preço do produto for alterado depois.
CREATE TABLE IF NOT EXISTS itens_compra (
    id_item_compra INT NOT NULL AUTO_INCREMENT,
    id_compra INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario_centavos INT NOT NULL,
    custo_unitario_centavos INT NOT NULL,
    subtotal_centavos INT NOT NULL,
    PRIMARY KEY (id_item_compra),
    CONSTRAINT uq_itens_compra_produto UNIQUE (id_compra, id_produto),
    CONSTRAINT fk_itens_compra_compra FOREIGN KEY (id_compra)
        REFERENCES compras (id_compra),
    CONSTRAINT fk_itens_compra_produto FOREIGN KEY (id_produto)
        REFERENCES produtos (id_produto),
    CONSTRAINT chk_itens_quantidade CHECK (quantidade > 0),
    CONSTRAINT chk_itens_preco CHECK (preco_unitario_centavos > 0),
    CONSTRAINT chk_itens_subtotal CHECK (subtotal_centavos = quantidade * preco_unitario_centavos),
    INDEX idx_itens_compra_produto (id_produto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- MOVIMENTAÇÕES DA CARTEIRA (extrato)
-- valor_centavos tem sinal: CREDITO > 0, DEBITO < 0, AJUSTE diferente de zero.
-- saldo_apos_centavos registra o saldo logo depois do lançamento.
-- id_autor: quem lançou (o próprio usuário, ou o administrador em um AJUSTE).
CREATE TABLE IF NOT EXISTS movimentacoes (
    id_movimentacao INT NOT NULL AUTO_INCREMENT,
    id_carteira INT NOT NULL,
    tipo ENUM('CREDITO', 'DEBITO', 'AJUSTE') NOT NULL,
    valor_centavos INT NOT NULL,
    saldo_apos_centavos INT NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    id_compra INT NULL,
    id_autor INT NOT NULL,
    chave_idempotencia CHAR(36) NULL,
    data_hora DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id_movimentacao),
    CONSTRAINT uq_movimentacoes_compra UNIQUE (id_compra),
    CONSTRAINT uq_movimentacoes_chave UNIQUE (chave_idempotencia),
    CONSTRAINT fk_movimentacoes_carteira FOREIGN KEY (id_carteira)
        REFERENCES carteiras (id_carteira),
    CONSTRAINT fk_movimentacoes_compra FOREIGN KEY (id_compra)
        REFERENCES compras (id_compra),
    CONSTRAINT fk_movimentacoes_autor FOREIGN KEY (id_autor)
        REFERENCES usuarios (id_usuario),
    CONSTRAINT chk_movimentacoes_valor CHECK (
        (tipo = 'CREDITO' AND valor_centavos > 0)
        OR (tipo = 'DEBITO' AND valor_centavos < 0)
        OR (tipo = 'AJUSTE' AND valor_centavos <> 0)
    ),
    CONSTRAINT chk_movimentacoes_saldo CHECK (saldo_apos_centavos >= 0),
    INDEX idx_movimentacoes_carteira_data (id_carteira, data_hora),
    INDEX idx_movimentacoes_data (data_hora)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
