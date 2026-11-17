# Testes manuais — cadastro de produtos (AV05)

Roteiro para conferir, com MySQL ligado, as correções pedidas na devolutiva da AV04. Marque apenas o que for observado.

| Informação | Preenchimento |
| --- | --- |
| Data e responsável | |
| Commit testado | |
| Navegador e tamanho de tela | |

Preparação: `make up` (ou `make api` + `make web`), depois abra `http://127.0.0.1:5500/html/catalogo_produtos_adm.html`.

## Devolutivas da AV04

- [ ] **D01 — Sem código manual:** o formulário não pede código. Após salvar, o card mostra "Código: N", gerado pelo banco.
- [ ] **D02 — Preço de compra e de venda:** o formulário tem os dois campos; o card mostra os dois valores.
- [ ] **D03 — Só quantidade em estoque:** não existem campos de estoque mínimo/máximo nem de validade.
- [ ] **D04 — Sem rótulos de zero lactose:** o formulário não tem as caixas de zero lactose/zero açúcar. Um produto da categoria *Frutas* aparece com os dois selos; um de *Bebidas*, sem selos.
- [ ] **D05 — Enter não grava:** preencha o cadastro e pressione Enter em vários campos. O modal continua aberto e nada é salvo (confira a lista e o banco).
- [ ] **D06 — Grava só no botão:** clique em **Salvar produto**. O produto aparece na lista e no banco.
- [ ] **D07 — Excluir não apaga:** clique em **Excluir** e confirme. O produto aparece como *Inativo*, some do catálogo do cliente e continua na tabela `produtos` com `status = 'INATIVO'`. Não existe opção de exclusão definitiva.
- [ ] **D08 — Reativar:** clique em **Reativar**; o produto volta aos ativos com o mesmo código.

## Validação e máscaras

- [ ] **V01 — Máscara de moeda:** digitar `450` no preço mostra `4,50`; letras são ignoradas.
- [ ] **V02 — Obrigatórios:** salvar com nome, categoria ou preços vazios mostra mensagem junto a cada campo.
- [ ] **V03 — Venda menor que compra:** compra 5,00 e venda 4,00 é recusado com mensagem no campo de venda.
- [ ] **V04 — Estoque:** quantidade negativa é recusada; zero é aceito e o card mostra "Sem estoque".
- [ ] **V05 — Foto:** JPG/PNG/WebP até 5 MB têm prévia; outros formatos ou arquivos maiores são recusados mantendo os demais dados digitados.
- [ ] **V06 — Validação no servidor:** pela API, `POST` com `preco_venda_centavos` menor que o de compra, ou com `codigo_produto`, responde `422` e nada é gravado.

## Persistência e auditoria

- [ ] **P01 — Alterar:** mude o preço de venda e a quantidade; após recarregar a página os valores persistem.
- [ ] **P02 — Reiniciar:** pare e suba a aplicação de novo; os dados continuam.
- [ ] **P03 — Auditoria:** `GET /api/produtos/{id}/auditoria` lista `INCLUIR`, `ALTERAR`, `INATIVAR` e `REATIVAR` com antes/depois.
- [ ] **P04 — Layout:** listagem, formulário e confirmação funcionam em 360 × 800 px e no desktop sem rolagem horizontal.

## Resultado

| Resultado | Preenchimento |
| --- | --- |
| Casos aprovados | |
| Falhas e issues abertas | |
| Evidências | |
