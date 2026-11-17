# Decisões do projeto

## Stack

| Camada | Escolha | Motivo |
| --- | --- | --- |
| Backend | Python 3 + Flask | Simples, gratuito e conhecido pela equipe (RNF12). |
| Banco | MySQL 8.0.16+ | Relacional, com restrições CHECK aplicadas; roda em Docker ou instalação local. |
| Conector | MySQL Connector/Python | Driver oficial; credenciais em `.env` (fora do Git). |
| Frontend | HTML, CSS e JavaScript puros | Sem etapa de build; roda em qualquer navegador atual (RNF01). |
| Dinheiro | Inteiros em centavos | Evita erros de arredondamento. |
| Datas | Sessão MySQL em UTC | Auditoria consistente. |

## Organização do código

Backend em camadas `routes → controller → service → repository`, um pacote por módulo de negócio. Detalhes em [arquitetura.md](arquitetura.md). Essa divisão foi iniciada na branch do Luan e unificada na develop, substituindo o arquivo único `produtos.py` da AV04.

## Produto

Decisões tomadas a partir da devolutiva da AV04 (detalhes em [modelo-produto.md](modelo-produto.md)):

- **Código:** o identificador é o `id_produto` gerado pelo banco; não há código digitado.
- **Preços:** preço de compra e preço de venda; a venda não pode ser menor que a compra.
- **Estoque:** somente quantidade. Sem mínimo, máximo ou validade.
- **Selos:** automáticos para a categoria Frutas; não aparecem no formulário.
- **Exclusão:** sempre lógica (`status = INATIVO`). O produto e o histórico ficam no banco (RNF10). A rota de exclusão física da AV04 foi removida.
- **Gravação:** o formulário só grava pelo clique no botão Salvar; Enter não envia.
- **Auditoria:** cada gravação registra autor, origem, data/hora e antes/depois na mesma transação (RNF09).

## Segurança

Ainda não há login. As rotas administrativas devem ficar em ambiente local até a implementação de autenticação e autorização por perfil (RNF08, issue #11). `X-Actor` apenas identifica o operador informado pela tela.
