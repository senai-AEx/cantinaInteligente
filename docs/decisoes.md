# Decisões do projeto

Registro das escolhas do grupo e dos motivos. A justificativa completa das tecnologias está na seção 8 do [Documento do Sistema](documento-do-sistema.md).

## Stack

| Camada | Escolha | Motivo |
| --- | --- | --- |
| Backend | Python 3 + Flask | Simples, gratuito e conhecido pela equipe (baixo custo). |
| Banco | MySQL 8.0.16+ | Relacional, com transações, bloqueio de linha e restrições CHECK; roda em Docker ou instalação local. |
| Conector | MySQL Connector/Python | Driver oficial; consultas com parâmetros; credenciais em `.env` (fora do Git). |
| Frontend | HTML, CSS e JavaScript puros | Sem etapa de build; roda em qualquer navegador atual, no celular e no computador. |
| Sessão | Cookie assinado do Flask | Já vem no framework; `HttpOnly` e `SameSite=Lax`; não exige token no navegador. |
| Senha | Hash com `werkzeug.security` | Já vem com o Flask; a senha nunca é gravada em texto puro. |
| QR Code | Biblioteca `segno` | Só Python, sem dependências extras; gera SVG nítido para impressão, sem arquivos de imagem guardados no servidor. |
| Backup | `mysqldump` dentro do contêiner MySQL | Cópia completa e restauração com um comando (`make backup` e `make restore`), sem programa extra no computador. |
| Dinheiro | Inteiros em centavos | Evita erros de arredondamento. |
| Datas | Sessão MySQL em UTC | Registros consistentes; a tela mostra no horário local e os relatórios usam datas de Brasília. |
| Ambiente | Docker (MySQL) + Make | Mesmo banco e mesmos comandos em todos os computadores. |

## Decisões de negócio e de arquitetura (D1 a D9)

Decisões levantadas no [plano de execução](plano-de-execucao.md) e adotadas pelo grupo.

| # | Tema | Decisão | Motivo e consequência |
| --- | --- | --- | --- |
| D1 | Quem registra o crédito | **O próprio usuário declara o depósito** feito na caixa. O administrador confere pelos depósitos declarados e pode lançar ajuste. | Mantém o conceito da Cantina da Honestidade e não exige atendente. Cada declaração fica registrada com usuário, valor, data e hora. |
| D2 | Compra com saldo insuficiente | **Bloquear** e oferecer "Adicionar crédito". | O saldo nunca fica negativo (regra RN03), o que evita inconsistência entre compras e saldos. |
| D3 | Perfis | **Cliente e Administrador.** | Repositor e Gateway Pix saem do escopo e ficam como evolução futura no documento. |
| D4 | Valor da compra | **Debita o total dos produtos.** | Sai o "valor livre" do antigo RF06, que contradizia o desconto automático pedido na demanda. |
| D5 | Como servir as telas | **Pelo próprio Flask**, na mesma porta da API (5000). | Permite a sessão por cookie sem CORS e simplifica a execução: um servidor só. |
| D6 | Primeiro administrador | **Criado por comando** (`make admin`), com os dados `ADMIN_*` do `.env`. Clientes se cadastram sozinhos. | Não existe tela pública para criar administrador. Depois, um administrador pode mudar o perfil de outro usuário. |
| D7 | QR Code | **Um QR Code da cantina** (abre o catálogo) **e um por produto** (coloca o item na sacola), feito só depois das demais fases. | A demanda trata o QR Code como possibilidade; fica como RF13, marcado como previsto até ser implementado. |
| D8 | Publicar o sistema online | **Opcional**, só se sobrar tempo. | A banca aceita vídeo; o ambiente oficial da entrega é o local. |
| D9 | Ferramenta de planejamento | **Kanban do GitHub Projects** (no lugar do Trello citado na versão antiga do documento). | É a ferramenta que o grupo realmente usa; fica junto do código, das issues e dos pull requests. |

## Organização do código

Backend em camadas `routes → controller → service → repository`, um pacote por módulo de negócio (`usuarios`, `produtos`, `carteira`, `compras` e `admin`). Detalhes em [arquitetura.md](arquitetura.md). A divisão em camadas foi iniciada na branch do Luan e unificada na `develop`, substituindo o arquivo único `produtos.py` da AV04.

## Produto

Decisões tomadas a partir da devolutiva da AV04 (detalhes em [modelo-produto.md](modelo-produto.md)):

- **Código:** o identificador é o `id_produto` gerado pelo banco; não há código digitado.
- **Preços:** preço de compra e preço de venda; a venda não pode ser menor que a compra.
- **Estoque:** somente quantidade. Sem mínimo, máximo ou validade.
- **Selos:** automáticos para a categoria Frutas; não aparecem no formulário.
- **Exclusão:** sempre lógica (`status = INATIVO`). O produto e o histórico ficam no banco. Não existe rota de exclusão física.
- **Gravação:** o formulário só grava pelo clique no botão Salvar; Enter não envia.
- **Auditoria:** cada gravação registra autor (o administrador logado), origem, data/hora e antes/depois na mesma transação.

## Usuários e segurança

- **Cadastro:** nome, matrícula, CPF, e-mail e senha. Matrícula, CPF e e-mail são únicos. Todo cadastro pela tela nasce como Cliente, com uma carteira de saldo zero.
- **Login:** um único campo aceita matrícula, e-mail ou CPF. A mensagem de erro é a mesma para qualquer falha, para não revelar se o identificador existe.
- **Senha:** de 8 a 72 caracteres, com letra e número; guardada só como hash.
- **Sessão:** cookie `HttpOnly`, com o usuário relido do banco a cada requisição. Usuário inativado perde o acesso na hora.
- **Permissão:** conferida no servidor em toda rota restrita (`401` sem login, `403` sem permissão). Esconder o menu na tela é só conveniência.
- **Exclusão:** usuários não são apagados, apenas inativados. O administrador não inativa a si mesmo nem tira o próprio perfil.
- **Privacidade:** a API não devolve a senha e devolve o CPF mascarado. O CPF não é editável depois do cadastro.

## Carteira e compras

- **Crédito:** de R$ 1,00 a R$ 500,00 por declaração, com a descrição "Depósito declarado na caixa".
- **Ajuste:** só o administrador, com motivo de 5 a 150 caracteres e até R$ 1.000,00 por lançamento; não pode deixar o saldo negativo.
- **Compra:** de 1 a 50 itens, quantidade de 1 a 99 por item. O nome e o preço nunca vêm da tela: são lidos do banco com o produto travado.
- **Transação única:** compra, itens, baixa do estoque, débito e movimentação são gravados juntos ou nada é gravado.
- **Bloqueio de linha:** a carteira é travada antes dos produtos, e os produtos sempre em ordem de código, para evitar espera circular entre duas compras.
- **Idempotência:** chave única por operação; repetir o envio devolve o registro já gravado.
- **Preço do momento:** o item da compra guarda o preço de venda e o custo; os relatórios não mudam quando o preço do produto é alterado.
- **Declaração de depósito:** na tela, o usuário informa o valor e marca a declaração de que fez o depósito; sem a declaração, a tela não envia.
- **Conferência da caixa:** feita pela aba "Depósitos declarados" dos relatórios, que usa a consulta de movimentações do tipo CRÉDITO no período e mostra o total declarado.

## Requisitos: numeração da versão final

A versão final do Documento do Sistema renumerou os requisitos. Use sempre a numeração nova nos documentos e nas issues.

| Versão anterior | Versão final |
| --- | --- |
| RNF06 (idempotência) | **RN01** (regra de negócio) |
| RNF09 (auditabilidade) | **RN02** (regra de negócio) |
| RNF07 (responsividade, 360 × 800 px) | RNF06 |
| RNF08 (segurança) | RNF07 |
| RNF10 (integridade) | RNF08 |
| RNF11 (escalabilidade) | RNF09 |
| RNF12 (custo) | RNF10 |
| RNF13 (confiabilidade) | RNF11 |
| RF06 + RF12 (finalizar e registrar a compra) | RF08 |
| RF04 (fornecedores) e RF10 (causa social) | Retirados |
| RF08 (relato de problemas) | Retirado |

Alguns comentários no código e no `database/schema.sql` ainda citam a numeração antiga (por exemplo, "RNF09" na auditoria de produtos e "RNF10" na exclusão lógica). Eles se referem, respectivamente, à RN02 e ao RNF08 da versão final.

## Fora do escopo desta entrega

Pix ou outro pagamento eletrônico, aplicativo mobile instalável, cadastro de fornecedores, validade de produtos, estoque mínimo e perfil de repositor. Ficam registrados como evolução para os próximos Projetos Aplicados.
