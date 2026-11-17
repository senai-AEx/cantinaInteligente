# Modelo de produto

Modelo em vigor a partir da AV05, já com as devolutivas da AV04 aplicadas. O esquema completo está em [`database/schema.sql`](../database/schema.sql); bancos criados na AV04 são atualizados pela migração [`005_produto_av05_mysql.sql`](../database/migrations/005_produto_av05_mysql.sql).

## Entidade `produtos`

| Campo | Tipo | Regra |
| --- | --- | --- |
| `id_produto` | inteiro | **Código do produto.** Gerado pelo banco (`AUTO_INCREMENT`); não é digitado no cadastro. |
| `nome` | texto, 2–100 | Obrigatório; não aceita apenas espaços. |
| `descricao` | texto, até 500 | Opcional. |
| `categoria` | texto, 2–50 | Obrigatória. |
| `preco_compra_centavos` | inteiro | Obrigatório, maior que zero. Quanto a cantina paga pelo produto. |
| `preco_venda_centavos` | inteiro | Obrigatório, maior que zero e **não menor que o preço de compra**. É o preço exibido ao cliente. |
| `quantidade_estoque` | inteiro | Não negativo; padrão 0. Único controle de estoque do produto. |
| `foto_caminho` | texto | Opcional; arquivo em `assets/produtos/` enviado pela tela. |
| `zero_lactose`, `zero_acucar` | booleanos | **Definidos pelo sistema:** verdadeiros quando a categoria é *Frutas*; falsos nas demais. Não aparecem no formulário. |
| `status` | `ATIVO` / `INATIVO` | Padrão `ATIVO`. **Excluir** um produto muda para `INATIVO`. |
| `criado_em`, `atualizado_em` | data/hora UTC | Controle automático. |

Valores monetários são guardados em centavos (inteiros) para evitar erros de arredondamento: R$ 4,50 = `450`.

## O que mudou em relação à AV04

| Antes (AV04) | Agora | Motivo |
| --- | --- | --- |
| `codigo_produto` digitado e único | Removido; o código é o `id_produto` automático | Devolutiva: ID automático, sem código manual. |
| `preco_centavos` | `preco_compra_centavos` + `preco_venda_centavos` | Devolutiva: preço de compra e de venda. |
| `estoque_minimo`, `estoque_maximo` | Removidos | Devolutiva: manter somente quantidade em estoque. |
| `validade` | Removida | Devolutiva: retirar validade do RF03 e do produto. |
| Selos marcados à mão | Automáticos para Frutas | Devolutiva: remover os rótulos de zero lactose do cadastro; aplicar a regra para frutas. |
| Botão "Excluir definitivamente" | Removido; Excluir = inativar | Devolutiva: o produto deve continuar no banco como inativo (RNF10). |

## Exclusão lógica

O sistema não apaga produtos. Ao excluir, o produto:

- sai do catálogo do cliente e da lista de ativos;
- continua na tabela `produtos` com `status = 'INATIVO'`, com todos os dados;
- pode ser reativado pela tela administrativa;
- tem a ação registrada em `auditoria_produtos` (`INATIVAR`).

A API não possui rota `DELETE` para produtos.

## Auditoria

`auditoria_produtos` guarda ação (`INCLUIR`, `ALTERAR`, `INATIVAR`, `REATIVAR`), autor, origem, data/hora e os dados antes/depois. A gravação do produto e a da auditoria acontecem na mesma transação: ou as duas são salvas, ou nenhuma. O valor `EXCLUIR` continua no ENUM apenas para registros antigos da AV04.

## Pendências de negócio

- Confirmar com a cantina se outras categorias além de *Frutas* devem receber os selos.
- Produtos migrados da AV04 receberam preço de compra igual ao de venda; revise-os na tela.
