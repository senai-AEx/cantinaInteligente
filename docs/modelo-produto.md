# Modelo de produto definido para a AV04

## Entidade `produtos`

| Campo | Tipo lógico | Regra |
| --- | --- | --- |
| `id_produto` | identificador inteiro | Gerado pelo banco; chave primária. |
| `codigo_produto` | texto, até 32 caracteres | Obrigatório e único. EAN/GTIN da embalagem ou código interno como `CI-0001`. |
| `nome` | texto, 2–100 caracteres | Obrigatório; não aceitar apenas espaços. |
| `descricao` | texto, até 500 caracteres | Opcional. |
| `categoria` | texto, 2–50 caracteres | Obrigatória; texto simples nesta etapa. |
| `preco_centavos` | inteiro | Obrigatório e maior que zero; a tela mostra R$. |
| `quantidade_estoque` | inteiro | Não negativo; saldo inicial para a AV04. |
| `estoque_minimo` | inteiro | Não negativo; limiar de alerta. |
| `estoque_maximo` | inteiro | Não negativo e ≥ mínimo; alvo de reposição, não limite rígido para quantidade. |
| `validade` | data ISO `AAAA-MM-DD` | Opcional; representa a **menor validade** do estoque atual. |
| `foto_caminho` | caminho relativo | Opcional; arquivo local em `assets/produtos/`. |
| `zero_lactose`, `zero_acucar` | booleanos | Selos opcionais do RF03. |
| `status` | `ATIVO` ou `INATIVO` | Padrão `ATIVO`; inativar muda para `INATIVO` e permite reativação. Excluir remove definitivamente a linha de produto. |
| `criado_em`, `atualizado_em` | data e hora UTC | Controle de alterações. |

## Identificador e QR

A AV02 propõe leitura do **EAN/GTIN do produto** e QR para entrar na **cantina**. O DER da AV03 nomeia o campo do produto `codigo_qr`. Para evitar imprimir QR individual em cada item, adotamos `codigo_produto` no banco e na interface. Ele aceita o código de barras existente ou um código interno para itens sem EAN/GTIN. O atributo `codigo_qr` da AV03 fica, portanto, **substituído por `codigo_produto`** nesta implementação; o QR da cantina pertence a outra parte do sistema.

## Validade e estoque

Produtos embalados podem chegar em lotes com validades diferentes. Para a demonstração da AV04, `validade` registra a data mais próxima entre as unidades disponíveis. Ao repor o produto, esse valor deve ser revisto. O controle por lote e FEFO previsto como evolução na AV02 substitui essa simplificação depois. Produto inativo, sem estoque ou com validade anterior à data atual não aparece no catálogo disponível; continua consultável pela administração.

O estoque inicial fica no produto para atender ao DER da AV03 e ao CRUD da AV04. Movimentos de entrada, venda e ajuste previstos na AV02 serão outra funcionalidade; quando existirem, deverão atualizar `quantidade_estoque` na mesma transação e manter histórico.

## Auditoria

A tabela `auditoria_produtos` guarda produto, ação, autor, origem, data/hora e dados antes/depois para inclusão, alteração, inativação, reativação e exclusão definitiva. A exclusão registra uma cópia final do produto antes de remover sua linha. A migração `004_auditoria_exclusao_mysql.sql` remove a chave estrangeira da auditoria para que o histórico sobreviva à exclusão. O backend grava a mudança e a auditoria na **mesma transação**.

Fontes: RF02/RF03 e DER de `AV03_GRUPO_4.pdf`; RF04/RF18 e arquitetura de `AV02_Cantina_Inteligente_Solucao_e_Requisitos.pdf`.
