-- Base SQLite do CRUD de produtos da AV04.
-- Aplicar uma vez em um banco novo. Mudanças futuras devem entrar em outra migração.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS produtos (
    id_produto INTEGER PRIMARY KEY,
    codigo_produto TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(codigo_produto)) BETWEEN 3 AND 32),
    nome TEXT NOT NULL CHECK (length(trim(nome)) BETWEEN 2 AND 100),
    descricao TEXT NOT NULL DEFAULT '' CHECK (length(descricao) <= 500),
    categoria TEXT NOT NULL CHECK (length(trim(categoria)) BETWEEN 2 AND 50),
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos > 0),
    quantidade_estoque INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_estoque >= 0),
    estoque_minimo INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    estoque_maximo INTEGER NOT NULL DEFAULT 0
        CHECK (estoque_maximo >= estoque_minimo),
    validade TEXT CHECK (
        validade IS NULL OR
        (length(validade) = 10 AND
         validade GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')
    ),
    foto_caminho TEXT CHECK (foto_caminho IS NULL OR length(foto_caminho) <= 255),
    zero_lactose INTEGER NOT NULL DEFAULT 0 CHECK (zero_lactose IN (0, 1)),
    zero_acucar INTEGER NOT NULL DEFAULT 0 CHECK (zero_acucar IN (0, 1)),
    status TEXT NOT NULL DEFAULT 'ATIVO' CHECK (status IN ('ATIVO', 'INATIVO')),
    criado_em TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    atualizado_em TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_produtos_status_nome ON produtos (status, nome);

CREATE TABLE IF NOT EXISTS auditoria_produtos (
    id_auditoria INTEGER PRIMARY KEY,
    id_produto INTEGER NOT NULL REFERENCES produtos(id_produto) ON DELETE RESTRICT,
    acao TEXT NOT NULL CHECK (acao IN ('INCLUIR', 'ALTERAR', 'INATIVAR', 'REATIVAR')),
    autor TEXT NOT NULL,
    origem TEXT NOT NULL,
    antes_json TEXT,
    depois_json TEXT,
    registrado_em TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_auditoria_produto ON auditoria_produtos (id_produto, registrado_em);
