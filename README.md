# Cantina Inteligente — AV04 (Grupo 4)

Base de trabalho para apresentar **Manter Produto** com banco de dados. Este projeto contém a organização, as decisões e a primeira migração SQL; **a aplicação e as telas ainda serão desenvolvidas pela equipe**.

## Contexto

Projeto Aplicado II do Centro Universitário SENAI Santa Catarina para a Cantina da Honestidade da unidade Fraiburgo (SC). Equipe 4: Ana Cecília Pereira Lacerda Costa, Eduardo Peixoto dos Passos da Silva, Luan Lima de Souza, Pablo Santos e Vanessa Kathleen Góes Leite. A apresentação da AV04 está marcada para **15/10/2026, às 20h40** no cronograma fornecido.

## Decisões de partida

- **Funcionalidade:** incluir, consultar, alterar e inativar/reativar produtos. A inativação representa a exclusão na AV04 e preserva compras e auditoria.
- **Identificação:** `codigo_produto` único. Usar EAN/GTIN da embalagem quando existir; caso contrário, gerar código interno. O QR identifica a cantina, não cada produto.
- **Produto:** nome, descrição, categoria, preço, estoque, mínimo, máximo, validade, foto, selos e situação. Ver regras em [modelo-produto.md](docs/modelo-produto.md).
- **Tecnologia inicial:** Python + Flask no backend, SQLite no banco, HTML/CSS/JavaScript no frontend. A interface será responsiva e preparada para a PWA proposta na AV02.
- **Dinheiro:** preço armazenado em centavos inteiros; exibição em reais.

Essa escolha é pequena para a AV04: Flask documenta a integração direta com SQLite, que não precisa de servidor separado. Se o uso crescer, a camada de dados pode ser substituída sem redesenhar as telas. A instalação como PWA depende de manifesto, ícones e contexto seguro; fica depois do CRUD funcional.

## Pastas

```text
cantinaInteligente/
├── assets/produtos/           # Fotos locais dos produtos
├── database/migrations/       # 001_produtos.sql: esquema inicial SQLite
├── docs/                      # Requisitos, modelo, decisões e contrato CRUD
├── src/backend/               # Aplicação Flask e acesso ao banco (a criar)
├── src/frontend/              # Telas responsivas (a criar)
├── tests/                     # Testes dos fluxos (a criar)
└── requirements.txt           # Dependência inicial do backend
```

## Ordem de trabalho

1. Criar ambiente virtual Python e instalar `requirements.txt`.
2. Aplicar `database/migrations/001_produtos.sql` em um banco SQLite de desenvolvimento.
3. Implementar as rotas e regras de [contrato-crud.md](docs/contrato-crud.md).
4. Construir tela de lista/consulta e formulário de inclusão/edição com validação.
5. Demonstrar os quatro fluxos e conferir os dados no banco antes e depois de reiniciar a aplicação.

## Fontes do projeto

- `AV02_Cantina_Inteligente_Solucao_e_Requisitos.pdf`: proposta de PWA, EAN/GTIN, banco relacional e critérios de produto.
- `AV03_GRUPO_4.pdf`: RF02/RF03, atributos do DER e requisitos não funcionais.
- Enunciado e tabela da AV04 enviados nesta conversa.

Referências técnicas: [Flask e SQLite](https://flask.palletsprojects.com/en/stable/tutorial/database/), [SQLite em Python](https://docs.python.org/3/library/sqlite3.html) e [instalação de PWA](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable).
