# Cantina Inteligente — AV04 (Grupo 4)

Base de trabalho para apresentar **Manter Produto** com banco de dados. Este projeto contém a organização, as decisões e a primeira migração SQL; **a aplicação e as telas ainda serão desenvolvidas pela equipe**.

## Contexto

Projeto Aplicado II do Centro Universitário SENAI Santa Catarina para a Cantina da Honestidade da unidade Fraiburgo (SC). Equipe 4: Ana Cecília Pereira Lacerda Costa, Eduardo Peixoto dos Passos da Silva, Luan Lima de Souza, Pablo Santos e Vanessa Kathleen Góes Leite. A apresentação da AV04 está marcada para **15/10/2026, às 20h40** no cronograma fornecido.

Acompanhar as tarefas no [Kanban da AV04](https://github.com/orgs/senai-AEx/projects/1) e a entrega no [marco AV04 — CRUD de Produto](https://github.com/senai-AEx/cantinaInteligente/milestone/1).

## Decisões de partida

- **Funcionalidade:** incluir, consultar, alterar e inativar/reativar produtos. A inativação representa a exclusão na AV04 e preserva compras e auditoria.
- **Identificação:** `codigo_produto` único. Usar EAN/GTIN da embalagem quando existir; caso contrário, gerar código interno. O QR identifica a cantina, não cada produto.
- **Produto:** nome, descrição, categoria, preço, estoque, mínimo, máximo, validade, foto, selos e situação. Ver regras em [modelo-produto.md](docs/modelo-produto.md).
- **Stack pendente de decisão do grupo:** Python + Flask, SQLite e HTML/CSS/JavaScript são a proposta inicial da estrutura. Os arquivos atuais de dependências e migração refletem essa proposta e deverão ser alinhados ao resultado da votação.
- **Dinheiro:** preço armazenado em centavos inteiros; exibição em reais.

Na proposta inicial, Flask integra com SQLite, que não precisa de servidor separado. A interface responsiva atende à direção de PWA apresentada na AV02; a instalação como PWA depende de manifesto, ícones e contexto seguro e fica depois do CRUD funcional.

## Pastas e arquivos

```text
cantinaInteligente/
├── .editorconfig             # Padrão de edição de arquivos de texto
├── .gitattributes            # Quebras de linha e tratamento de binários
├── CONTRIBUTING.md           # Fluxo de trabalho da equipe
├── assets/produtos/          # Fotos locais dos produtos
├── database/migrations/      # Esquema inicial SQLite, sujeito à stack escolhida
├── docs/                     # Requisitos, modelo, decisões, contrato e roteiros
├── src/backend/              # Aplicação e acesso ao banco (a criar)
├── src/frontend/             # Telas responsivas (a criar)
├── tests/                    # Testes dos fluxos (a criar)
└── requirements.txt          # Dependência da proposta inicial com Flask
```

## Guia para a equipe

- [Como contribuir](CONTRIBUTING.md): escolher issue, criar branch, fazer commit e abrir PR.
- [Requisitos da AV04](docs/requisitos-av04.md): funcionalidade e critérios da avaliação.
- [Modelo de Produto](docs/modelo-produto.md): campos e regras de negócio.
- [Contrato do CRUD](docs/contrato-crud.md): operações e respostas esperadas.
- [Decisões de projeto](docs/decisoes.md): escolhas iniciais e motivos.
- [Testes manuais](docs/testes-manuais-av04.md): casos para conferir quando a aplicação existir.
- [Roteiro da apresentação](docs/roteiro-apresentacao-av04.md): preparação e sequência da demonstração.

## Ordem de trabalho

1. Confirmar a stack com o grupo e alinhar as decisões, dependências, migração e issues.
2. Preparar o ambiente e o banco de desenvolvimento. Se a proposta inicial for aprovada, usar `requirements.txt` e `database/migrations/001_produtos.sql`.
3. Implementar as rotas e regras de [contrato-crud.md](docs/contrato-crud.md).
4. Construir tela de lista/consulta e formulário de inclusão/edição com validação.
5. Executar o checklist manual, conferir persistência após reiniciar e ensaiar a apresentação.

Os comandos reais de instalação, execução e testes deverão ser adicionados ao README durante a implementação.

## Fontes do projeto

- `AV02_Cantina_Inteligente_Solucao_e_Requisitos.pdf`: proposta de PWA, EAN/GTIN, banco relacional e critérios de produto.
- `AV03_GRUPO_4.pdf`: RF02/RF03, atributos do DER e requisitos não funcionais.
- Enunciado e tabela da AV04 enviados nesta conversa.

Referências técnicas da proposta inicial: [Flask e SQLite](https://flask.palletsprojects.com/en/stable/tutorial/database/), [SQLite em Python](https://docs.python.org/3/library/sqlite3.html) e [instalação de PWA](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable).
