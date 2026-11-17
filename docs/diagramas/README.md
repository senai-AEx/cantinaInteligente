# Diagramas do Documento do Sistema

Cada arquivo `.mmd` é um diagrama em [Mermaid](https://mermaid.js.org/) (texto que vira imagem). O conteúdo é o mesmo dos blocos `mermaid` do [Documento do Sistema](../documento-do-sistema.md). Se alterar um diagrama, altere nos dois lugares.

| Arquivo | Seção do documento | Diagrama |
| --- | --- | --- |
| `mer.mmd` | 6 | Modelo Entidade-Relacionamento |
| `casos-de-uso.mmd` | 7.1 | Casos de uso |
| `sequencia-compra.mmd` | 7.2 | Sequência — finalizar compra |
| `sequencia-credito.mmd` | 7.2 | Sequência — adicionar crédito |
| `atividades-compra.mmd` | 7.3 | Atividades — fluxo da compra |
| `classes.mmd` | 7.4 | Classes |
| `componentes.mmd` | 7.5 | Componentes |
| `implantacao.mmd` | 7.6 | Implantação |
| `topologia.mmd` | 8.1 | Topologia da solução |

## Exportar para PNG

### Opção 1 — pelo navegador (mais simples)

1. Abra <https://mermaid.live>.
2. Apague o exemplo do painel **Code** e cole o conteúdo do arquivo `.mmd`.
3. Confira o desenho no painel da direita.
4. Em **Actions**, clique em **PNG** (ou **SVG**) para baixar a imagem.
5. Cole a imagem no Documento do Sistema, na seção indicada na tabela acima.

### Opção 2 — pelo terminal (todos de uma vez)

Requer o Node.js instalado. Na raiz do repositório, um comando por diagrama:

```sh
npx -y @mermaid-js/mermaid-cli -i docs/diagramas/mer.mmd -o docs/diagramas/mer.png -b white -s 2
```

Para exportar todos (Git Bash, macOS ou Linux):

```sh
for arquivo in docs/diagramas/*.mmd; do npx -y @mermaid-js/mermaid-cli -i "$arquivo" -o "${arquivo%.mmd}.png" -b white -s 2; done
```

`-b white` deixa o fundo branco e `-s 2` dobra a resolução, para a imagem ficar nítida no PDF. Na primeira execução o `npx` baixa a ferramenta e um navegador interno; pode demorar alguns minutos.

### Opção 3 — pelo GitHub

O GitHub desenha blocos `mermaid` automaticamente. Abra o [Documento do Sistema](../documento-do-sistema.md) no site do repositório e faça uma captura de tela do diagrama.

## Cuidados ao colar no documento

- Use a legenda no padrão do template: `Imagem N: título do diagrama` acima e `Fonte: Elaborado pela equipe do Projeto Aplicado II (2026).` abaixo.
- Os diagramas de sequência e o MER são largos: no Google Docs ou Word, coloque a página em paisagem ou reduza a imagem sem deixar o texto ilegível.
- Se um diagrama não desenhar, o erro costuma ser um caractere especial fora das aspas. Mantenha os rótulos entre aspas duplas e os identificadores sem espaços nem acentos.
- Os arquivos `.png` gerados não precisam ir para o repositório; se o grupo quiser guardá-los, mantenha-os nesta pasta.
