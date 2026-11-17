# Como contribuir

Este guia organiza o trabalho da equipe. A stack é Python + Flask + MySQL (veja [decisões](docs/decisoes.md)).

## Antes de começar

1. Escolha uma tarefa no [Kanban](https://github.com/orgs/senai-AEx/projects/1).
2. Confira as dependências e os critérios de aceite da issue.
3. Defina o responsável na issue e mova o cartão para **Em andamento** quando iniciar.
4. Leia a [arquitetura](docs/arquitetura.md), o [modelo de Produto](docs/modelo-produto.md) e a [API de produtos](docs/contrato-api-produtos.md).

## Trabalhar em uma branch

A integração acontece na `develop`; a `main` recebe as versões entregues. Com o trabalho local já salvo em commit, atualize a `develop` e crie uma branch para a issue. Exemplo para a issue 11:

```sh
git switch develop
git pull --ff-only origin develop
git switch -c feat/11-usuarios
```

Use nomes curtos, sem espaços ou acentos. Exemplos de prefixos: `feat/` para funcionalidades, `fix/` para correções e `docs/` para documentação. Se a atualização falhar por divergência, combine a integração com a equipe antes de continuar.

## Commit e push

- Faça commits pequenos, com uma mudança clara por vez.
- Escreva mensagens diretas, como `feat: adicionar consulta de produtos` ou `docs: atualizar roteiro da AV04`.
- Confira `git status` e `git diff` antes de selecionar os arquivos.
- Adicione somente os arquivos da tarefa. Depois use `git diff --cached` para revisar o que entrará no commit.
- Arquivos `.env`, senhas, bancos locais e dependências instaladas devem ficar fora do commit.

Após o commit, publique a branch. Para o exemplo acima:

```sh
git push -u origin feat/11-usuarios
```

## Abrir e revisar o PR

Abra um pull request da sua branch para `develop`. Antes, rode `make test` e resolva conflitos com a `develop` na sua branch. Na descrição, informe:

- O que mudou e qual issue atende.
- Como conferir a mudança e quais testes foram executados.
- Imagens das telas, quando houver alteração visual.
- Pendências conhecidas.

Use `Closes #2` somente se o PR resolver toda a issue 2. Para uma entrega parcial, use `Refs #2`.

Mova o cartão para **Em revisão** e peça a conferência de outro integrante. Após integrar o PR e validar os critérios de aceite, confira se a issue está fechada e o cartão em **Concluído**.

## Conferência antes da entrega

Use os [testes manuais](docs/testes-manuais.md) e marque somente o que foi executado. Mudanças no banco entram como nova migração em `database/migrations/` (nunca edite uma migração já aplicada) e também no `database/schema.sql`.

Os arquivos `.editorconfig` e `.gitattributes` padronizam a edição e as quebras de linha. Use um editor com suporte a EditorConfig. Se o grupo mudar uma regra de negócio ou confirmar a stack, registre em [decisões](docs/decisoes.md) e alinhe a documentação e as issues afetadas.
