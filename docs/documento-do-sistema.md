# Documento do Sistema — textos para a AV05

Trechos para atualizar o Documento do Sistema (template da professora) de acordo com o que está implementado. Revise a redação com o grupo antes de colar; a numeração dos requisitos deve seguir a versão final combinada na issue #8.

## Requisitos afetados pela devolutiva do produto

**RF02:** O sistema deve permitir ao administrador cadastrar, consultar, editar e excluir produtos da Cantina da Honestidade. O código do produto é gerado automaticamente; o cadastro registra nome, categoria, descrição, foto, preço de compra, preço de venda e quantidade em estoque. A exclusão é lógica: o produto fica inativo e permanece no banco de dados.

**RF03:** O sistema deve listar para os clientes os produtos ativos com estoque, informando nome, preço de venda, foto e, para frutas, os selos zero lactose e zero açúcar.

**RF11 (ajuste sugerido):** como não há mais estoque mínimo, o relatório passa a considerar "produtos sem estoque" (quantidade igual a zero) em vez de "abaixo do nível mínimo".

**Regra de negócio sugerida:** O preço de venda não pode ser menor que o preço de compra.

## 6. MER — entidade PRODUTO

Substituir os atributos da entidade PRODUTO por:

`id_produto` (PK, automático), `nome`, `descricao`, `categoria`, `preco_compra`, `preco_venda`, `quantidade_estoque`, `foto`, `zero_lactose`, `zero_acucar`, `status`.

Remover `codigo_qr` e `validade`. No banco, os preços ficam em centavos (`preco_compra_centavos`, `preco_venda_centavos`). A tabela `auditoria_produtos` registra as alterações (RNF09).

## 8. Proposta de solução tecnológica escolhida

A Cantina Inteligente é uma aplicação web cliente/servidor composta por:

- **Frontend:** páginas em HTML5, CSS3 e JavaScript, responsivas a partir de 360 × 800 px (RNF07), que funcionam nos navegadores atuais sem instalação (RNF01).
- **Backend:** API REST em Python 3 com o framework Flask, organizada em camadas (rotas, controle, serviço e repositório) para facilitar a inclusão de novos módulos — usuários, carteira, compras e relatórios — sem reconstruir o sistema (RNF11).
- **Banco de dados:** MySQL 8, com chaves primárias automáticas, restrições de integridade (CHECK) e transações que gravam cada alteração junto com sua auditoria (RNF09, RNF10).
- **Ferramentas:** Git e GitHub para versionamento, Docker para padronizar o MySQL entre os computadores da equipe e testes automatizados com `unittest`.

Todas as tecnologias são gratuitas e de código aberto, atendendo à restrição de baixo custo (RNF12).

### 8.1 Topologia (opcional)

Navegador (telas HTML/JS) → HTTP/JSON → API Flask (porta 5000) → MySQL (porta 3306). As fotos dos produtos ficam na pasta `assets/produtos` do servidor.

## 9.2 Repositório da aplicação

https://github.com/senai-AEx/cantinaInteligente — branch `develop` para integração e `main` para versões entregues.
