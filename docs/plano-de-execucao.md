# Plano de execução — AV05 e AV06

**Feito em 17/11/2026 (terça).** Fontes: demanda do SAGA SENAI, AVA da UC (critérios, feedbacks e roteiro de estudos, lidos em 17/11), lista de correções da apresentação da AV04 e o código da branch `develop`.

## 1. Resumo

- **O projeto cobre hoje 2 dos 12 itens da demanda** (cadastro de produtos e consulta de preços). Usuários, login, carteira de créditos, compras, histórico, painel financeiro e relatórios ainda não existem — há apenas telas estáticas de login/cadastro e uma sacola que não grava nada.
- **"Implementar o projeto na íntegra"** é o feedback oficial da AV04 no AVA. Significa entregar **todas as funcionalidades da demanda**, não só o CRUD de produto.
- **Faltam 4 dias para a AV05 (21/11, 23:59) e 7 para a banca (24/11).**
- As correções pedidas na apresentação da AV04 (produto) **já estão feitas** na `develop`, mas **ainda sem commit**.
- O repositório está **privado** (responde 404 sem login). "Acesso liberado" é pré-requisito de correção da AV05.

## 2. Prazos e critérios (AVA)

| Entrega | Prazo | Critérios |
| --- | --- | --- |
| **AV05 — 25%** | **sáb 21/11, 23:59** | Pré-requisito: README com a execução + repositório com acesso liberado. Integração com banco **40%** · validação de campos (obrigatoriedade, tipos) e **máscaras 20%** · interface **10%** · **versão final do Documento do Sistema com as correções e a seção "Solução Tecnológica" 30%**. Publicar também o **vídeo de demonstração**. |
| **AV06 — 25%** | **ter 24/11**, banca entre 18:30 e 21:30 | Demonstração da aplicação **50%** · **checklist da norma ABNT NBR 17225:2025 10%** · qualidade da apresentação 20% · detalhamento da solução 20% · clareza e tempo 10%. Apresentação de **10 a 15 min**, **todos os integrantes falam**, demonstração por **vídeo sem áudio narrado ao vivo**, slides no modelo "Template P.I UniSENAI". |

O plano de trabalho da UC também pede, na AV05, **evidências de commits de todos os integrantes**. Hoje há commits de Pablo (28), Vanessa (11), Luan (7) e Eduardo (4); **Ana Cecília não tem nenhum**.

Atenção: os documentos antigos do repositório citavam 19/11 e 28/11. As datas válidas são as do AVA, acima.

**Conferir hoje:** na atividade "Escolha Horário da Banca" todas as 7 vagas aparecem cheias e o AVA mostra o aviso "Sua resposta não foi salva". Confirmar com a professora qual horário é o do Grupo 4.

## 3. O que a professora cobrou

| Origem | Cobrança | Situação |
| --- | --- | --- |
| AV02 (75) | Refazer **Partes Interessadas** no formato do template | Pendente (documento) |
| AV02 | Incluir requisito de **crédito**: cada estudante tem um crédito e as compras são abatidas do saldo | Pendente (documento e sistema) |
| AV02 | **Unificar RF06 e RF12** | Pendente (documento) |
| AV02 | **Excluir RF04** (fornecedores) e **RF10** (causa social) | Pendente (documento) |
| AV02 | **RF03: retirar validade** | Sistema ok; falta o documento |
| AV02 | Tirar **RNF06 e RNF09** dos RNFs (são regras de negócio) | Pendente (documento) |
| AV03 (90) | MER sem a entidade/atributo de **crédito** | Pendente (documento) |
| AV04 (85) | **Implementar o projeto na íntegra** | Pendente (fases 1 a 4) |
| Apresentação AV04 | Sem rótulos de zero lactose · gravar só no botão Salvar · preço de compra e de venda · só quantidade em estoque · excluir = inativar · sem código manual | **Feito** na `develop` (sem commit) |

## 4. Demanda × projeto

| # | Item da demanda | Hoje | Fase |
| --- | --- | --- | --- |
| 1 | Cadastro de usuários | Tela estática, sem nome/CPF e sem backend | 1 |
| 2 | Login com matrícula, e-mail ou CPF | Tela estática só com matrícula | 1 |
| 3 | Cadastro de produtos | **Pronto** | — |
| 4 | Consulta dos preços | **Pronto** (catálogo) | — |
| 5 | Adição de créditos (carteira virtual) | Não existe | 2 |
| 6 | Consulta do saldo | Não existe | 2 |
| 7 | Registro das compras | Sacola só no navegador; o modal avisa que "o sistema ainda não envia pedidos" | 3 |
| 8 | Desconto automático do saldo | Não existe | 3 |
| 9 | Histórico de compras | Não existe | 3 |
| 10 | Painel admin: usuários, produtos e movimentações | Só produtos | 4 |
| 11 | Relatórios de vendas e saldos | Não existe | 4 |
| 12 | QR Code ou outro método que facilite o registro | Não existe (a demanda trata como "possibilidade") | 6 |

**Restrições da demanda**

| Restrição | Hoje | O que garante |
| --- | --- | --- |
| Não descaracterizar a Cantina da Honestidade | Ok | O próprio usuário registra a compra e declara o depósito; ninguém "libera" produto (decisão D1) |
| Não permitir acesso não autorizado | **Falha**: a API administrativa está aberta | Login, sessão e permissão por perfil (fase 1) |
| Não gerar inconsistência entre compras e saldos | Não se aplica ainda | Compra em uma única transação, bloqueio de linha, saldo nunca negativo, proteção contra clique duplo (fase 3) |
| Baixo custo | Ok | Python, Flask e MySQL, todos gratuitos |
| Permitir expansões sem reconstruir | Ok | Backend em camadas, um pacote por módulo |

## 5. Decisões para fechar hoje no grupo

Cada uma tem uma recomendação; sem resposta, o plano segue com a recomendada.

| # | Decisão | Recomendação |
| --- | --- | --- |
| D1 | Quem registra o crédito? | **O próprio usuário declara o depósito** ("coloquei R$ 20 na caixa"). O administrador confere pelo relatório de depósitos e pode lançar ajuste. É o que mantém o conceito de honestidade e não exige atendente. |
| D2 | Compra com saldo insuficiente | **Bloquear** e oferecer "Adicionar crédito". Saldo nunca fica negativo. |
| D3 | Perfis | **Cliente e Administrador.** Repositor e Gateway Pix saem do escopo (ficam como evolução futura no documento). |
| D4 | Valor da compra | **Debita o total dos produtos.** Sai o "valor livre" do antigo RF06, que contradiz o desconto automático da demanda. |
| D5 | Como servir as telas | **Pelo próprio Flask** (uma porta só). Permite sessão por cookie sem CORS e simplifica execução e publicação. |
| D6 | Primeiro administrador | Criado por comando (`make admin`) com credenciais de demonstração; clientes se cadastram sozinhos. |
| D7 | QR Code | Um QR da cantina que abre o catálogo, e QR por produto que já coloca o item na sacola. Só depois das fases 1 a 5. |
| D8 | Publicar o sistema online | Opcional (o roteiro sugere). Só se sobrar tempo; a banca aceita vídeo. |
| D9 | Ferramenta de planejamento no documento | O documento cita Trello, mas o grupo usa o Kanban do GitHub. Escolher uma e citar a que está atualizada. |

## 6. Fases

Prioridade: **P0** = sem isso a AV05 não fecha · **P1** = pontua diretamente · **P2** = só se sobrar tempo.

### Fase 0 — Fechar o que já está feito (P0, hoje)

- Commit e push da `develop` (unificação do backend, correções do produto, docs).
- PR `develop` → `main`.
- Liberar acesso ao repositório (público, ou professora como colaboradora).
- Atualizar o Kanban com as fases deste plano.

Pronto quando: `main` atualizada, `make test` verde e o link do repositório abrir para a professora.

### Fase 1 — Usuários e login (P0)

Banco (migração `006`): `tipos_usuario`, `usuarios` (nome, matrícula, CPF, e-mail, senha com hash, perfil, situação; matrícula, CPF e e-mail únicos) e `carteiras` (uma por usuário, saldo em centavos, `CHECK saldo >= 0`).

Backend (`src/backend/usuarios/` e `src/backend/auth/`, nas mesmas camadas de `produtos`):

- `POST /api/auth/cadastro` — cria usuário Cliente e a carteira na mesma transação.
- `POST /api/auth/login` — um campo "matrícula, e-mail ou CPF" + senha.
- `POST /api/auth/logout` e `GET /api/auth/eu`.
- Senha guardada com hash (`werkzeug.security`, já instalado). Sessão por cookie `HttpOnly`; `SECRET_KEY` no `.env`.
- Decoradores `login_obrigatorio` e `somente_administrador`. Rotas de escrita de produtos e upload passam a exigir Administrador; a auditoria usa o usuário logado no lugar do `X-Actor`.
- Flask passa a servir `src/frontend` (D5).

Telas: `login.html` e `cadastro.html` ligadas à API; cabeçalho muda conforme a sessão (Entrar/Criar conta ou nome, saldo e Sair; "Administração" só para administrador); páginas administrativas redirecionam quem não tem permissão.

Validação e máscaras (20% da AV05): CPF com máscara `000.000.000-00` e dígito verificador; matrícula só com números; e-mail válido; senha com no mínimo 8 caracteres, letra e número; confirmação de senha; mensagens junto ao campo; as mesmas regras repetidas no servidor.

Pronto quando: cadastro, login pelos três identificadores, logout e bloqueio da área administrativa funcionam com MySQL; duplicidade de matrícula/CPF/e-mail é recusada com mensagem no campo.

### Fase 2 — Carteira de créditos (P0)

Banco (na `006`): `movimentacoes` (carteira, tipo `CREDITO`/`DEBITO`/`AJUSTE`, valor, saldo após, descrição, compra relacionada, data/hora).

Backend (`src/backend/carteira/`): `GET /api/carteira` (saldo), `GET /api/carteira/movimentacoes` (extrato) e `POST /api/carteira/creditos` (declara depósito). Crédito e atualização do saldo na mesma transação, com bloqueio da linha da carteira.

Tela `minha_conta.html`: saldo, formulário "Adicionar crédito" com máscara de moeda e confirmação, extrato.

Pronto quando: declarar R$ 20,00 aumenta o saldo, aparece no extrato e persiste; valor zero, negativo ou acima do limite definido é recusado.

### Fase 3 — Compra, débito e histórico (P0)

Banco (na `006`): `compras` (usuário, total, data/hora, chave única contra duplicidade) e `itens_compra` (produto, quantidade, preço unitário, subtotal).

Backend (`src/backend/compras/`): `POST /api/compras` faz **tudo em uma transação**: bloqueia carteira e produtos, confere estoque e saldo, grava compra e itens, baixa o estoque, debita o saldo e registra a movimentação `DEBITO`. Qualquer falha desfaz tudo. A chave enviada pela tela impede que um clique duplo gere duas compras. `GET /api/compras` lista o histórico do usuário.

Telas: no catálogo, a sacola ganha **Finalizar compra** (mostra saldo, total e saldo após; exige login; mensagem de agradecimento ao concluir). Em `minha_conta.html`, a aba **Minhas compras** com os itens de cada compra.

Pronto quando: a compra reduz estoque e saldo exatamente no valor total, aparece no histórico e no extrato; saldo ou estoque insuficiente bloqueia sem gravar nada; repetir a confirmação não duplica.

### Fase 4 — Painel administrativo e relatórios (P0)

Backend (`src/backend/admin/`, tudo restrito a Administrador):

- Usuários: listar/buscar, editar, mudar perfil, inativar/reativar (sem exclusão física, como nos produtos) e lançar ajuste de saldo com motivo.
- Movimentações: listar com filtro por período, tipo e usuário.
- Relatórios: vendas por período (total, quantidade, por produto), saldos dos usuários, depósitos declarados (para conferir com a caixa) e produtos sem estoque.

Telas: `usuarios_adm.html`, `movimentacoes_adm.html` e `relatorios_adm.html`, com o mesmo menu lateral do painel de produtos. Relatórios com botão **Imprimir**; exportar CSV é P2.

Pronto quando: o administrador vê e filtra tudo acima, e os totais dos relatórios batem com as compras e créditos feitos no teste.

### Fase 5 — Validação, interface e acessibilidade (P1)

Vale 30% da AV05 (validação + interface) e 10% da AV06 (norma).

- Revisar todos os formulários: obrigatórios, tipos, limites, máscaras (CPF, moeda, matrícula), erro junto ao campo, foco no primeiro erro, nada gravado com Enter.
- Aplicar o [checklist da ABNT NBR 17225](https://www.academiadeacessibilidade.com.br/ferramentas/checklist-abnt/index.html) (16 grupos: teclado, imagens, cabeçalhos, regiões, formulários, cores etc.) e registrar o resultado em `docs/checklist-acessibilidade-nbr17225.md` — esse arquivo é a evidência para a banca.
- Problemas já medidos: botão laranja `#e87522` com texto branco tem contraste **3,0:1** (mínimo 4,5:1); placeholder **2,4:1**; texto de ajuda **4,0:1**; não há link "pular para o conteúdo".
- Conferir tudo em 360 × 800 px e no desktop, sem rolagem horizontal (RNF07).

Pronto quando: checklist preenchido, itens reprovados corrigidos ou justificados, e roteiro de testes manuais executado.

### Fase 6 — Extras (P2)

- QR Code da cantina e por produto, gerado no painel para imprimir (D7).
- Publicação online com credenciais de demonstração (D8).
- Exportar relatórios em CSV.

### Fase 7 — Documento do Sistema (P0, em paralelo desde hoje)

Vale 30% da AV05 e pede **todas as seções preenchidas**. Ponto de partida: [documento-do-sistema.md](documento-do-sistema.md).

| Seção | O que fazer |
| --- | --- |
| Histórico de versões | Registrar as versões desta revisão |
| 2. Descrição da solução | Atualizar para o que foi implementado (carteira, compra com débito) |
| 3. Partes interessadas | **Refazer no formato do template**: 3.1 Coordenação, 3.2 Professor, 3.3 Cliente |
| 4. Atores | Cliente e Administrador (D3) |
| 5.1 Requisitos funcionais | Reescrever conforme a seção 7 deste plano: incluir crédito, unificar RF06/RF12, excluir RF04 e RF10, tirar validade do RF03 |
| 5.2 Requisitos não funcionais | Tirar RNF06 e RNF09 (viram regras de negócio); corrigir "maio de 2023" no RNF01 |
| 6. MER | Refazer: PRODUTO sem `codigo_qr` e `validade`, com preço de compra e de venda; **crédito explícito** (saldo na CARTEIRA, tipo CRÉDITO/DÉBITO na MOVIMENTAÇÃO) |
| 7. UML | **Seis diagramas, hoje todos vazios**: casos de uso, sequência (finalizar compra), atividades (compra e crédito), classes, componentes e implantação |
| 8. Solução tecnológica | Preencher com tecnologias e justificativas; 8.1 topologia |
| 9.1 / 9.2 | Ferramenta de planejamento realmente usada (D9) e link do repositório |

Pronto quando: PDF gerado, revisado por dois integrantes, sem seção vazia e batendo com o sistema.

### Fase 8 — Entrega da AV05 (P0, sábado 21/11)

- Congelar o código na sexta à noite; `main` atualizada com tag `av05`.
- README conferido em um computador limpo (clonar, `make setup`, `make up`).
- Vídeo de demonstração **sem áudio** seguindo o roteiro: cadastro → login → crédito → compra → histórico → painel admin → relatórios → validações.
- Enviar no AVA: PDF do documento, link do repositório, link do vídeo.

### Fase 9 — Banca (AV06, 22 a 24/11)

- Slides no "Template P.I UniSENAI": problema, solução, diagramas principais, tecnologias, checklist NBR 17225, demonstração.
- Dividir as falas entre os cinco; ensaiar cronometrado (10 a 15 min) narrando o vídeo.
- Preparar respostas: por que o crédito é declarado, como o saldo nunca fica inconsistente, por que não há exclusão física, o que fica para o Projeto Aplicado III.

## 7. Requisitos funcionais propostos para o documento

| RF | Descrição | Origem |
| --- | --- | --- |
| RF01 | Cadastro de usuário (nome, matrícula, CPF, e-mail, senha) | Demanda 1 |
| RF02 | Login com matrícula, e-mail ou CPF | Demanda 2 |
| RF03 | Administrador mantém produtos (código automático, preços de compra e venda, estoque; exclusão lógica) | Demanda 3; antigo RF02 |
| RF04 | Catálogo com nome, preço, foto e selos | Demanda 4; antigo RF03 sem validade |
| RF05 | Sacola de compras | Antigo RF05 |
| RF06 | Adicionar créditos à carteira | Demanda 5; feedback AV02 |
| RF07 | Consultar saldo e extrato | Demanda 6 |
| RF08 | Finalizar e registrar a compra, debitando o saldo | Demanda 7 e 8; antigos RF06 + RF12 unificados |
| RF09 | Baixar o estoque após a compra | Antigo RF09 |
| RF10 | Histórico de compras | Demanda 9 |
| RF11 | Administrador gerencia usuários e movimentações financeiras | Demanda 10; antigo RF01 |
| RF12 | Relatórios de vendas, saldos e estoque | Demanda 11; antigo RF11 |
| RF13 | QR Code para facilitar o registro da compra | Demanda 12; antigo RF07 sem Pix |

Saem: fornecedores (antigo RF04) e causa social (antigo RF10), por orientação da professora; relato de problemas (antigo RF08), por não constar na demanda. A mensagem de agradecimento (antigo RF13) vira parte do RF08.

Regras de negócio (nova subseção): confirmação repetida não duplica compra nem crédito; toda operação registra data/hora, autor e antes/depois; saldo nunca negativo; preço de venda não menor que o de compra; produtos e usuários não são apagados, apenas inativados.

## 8. Cronograma

| Dia | Código | Documento e entrega |
| --- | --- | --- |
| **Ter 17/11** | Fase 0. Fechar D1–D9. Fase 1: migração `006` e backend de login | Partes interessadas, atores e RFs/RNFs reescritos |
| **Qua 18/11** | Fase 1: telas e proteção das rotas. Fase 2: carteira | MER refeito; casos de uso |
| **Qui 19/11** | Fase 3: compra, débito e histórico | Diagramas de sequência, atividades e classes |
| **Sex 20/11** | Fase 4: painel e relatórios. Fase 5: validação e acessibilidade. **Congelar à noite** | Componentes, implantação, seção 8; PDF para revisão |
| **Sáb 21/11** | Só correções de bloqueio | Vídeo, README final, **enviar AV05 até as 18h** (limite 23:59) |
| **Dom 22/11** | Fase 6, se houver fôlego | Slides e evidências do checklist NBR 17225 |
| **Seg 23/11** | — | Ensaio cronometrado com todos |
| **Ter 24/11** | — | **Banca** |

## 9. Divisão sugerida

Baseada no que cada um já fez no repositório; ajustem como preferirem. Cada um faz commit do próprio trabalho, na própria branch, com PR para a `develop`.

| Integrante | Frente |
| --- | --- |
| Pablo | Integração, fase 3 (compra) e revisão dos PRs |
| Luan | Backend das fases 1 e 2 (usuários, login, carteira) |
| Eduardo | Migração `006`, MER e fase 4 (consultas dos relatórios) |
| Vanessa | Telas das fases 1 a 4 e fase 5 (interface e acessibilidade) |
| Ana Cecília | Documento do Sistema, diagramas UML, checklist NBR 17225 e roteiro de testes — **versionados no repositório**, para ter commits próprios |

## 10. Riscos e o que cortar

| Risco | Resposta |
| --- | --- |
| Não dar tempo de tudo | Cortar nesta ordem: publicação online → QR Code → CSV → edição de usuário pelo admin. **Não cortar**: login, crédito, compra com débito, histórico, um relatório de vendas e um de saldos, documento e vídeo. |
| Documento atrasar (30% da nota) | Começa hoje, em paralelo ao código; diagramas feitos a partir do modelo da seção 6, não do código pronto |
| Conflitos de merge na reta final | PRs pequenos e diários para a `develop`; ninguém trabalha direto nela |
| Banco diferente em cada computador | Só mexer no banco por migração; `make migrate` antes de testar |
| Demonstração falhar ao vivo | A banca aceita vídeo gravado; gravar no sábado com dados de exemplo (`make seed`) |
| Repositório sem acesso para a professora | Resolver hoje, na fase 0 |

## 11. Não verificado

- Os vídeos do representante da cantina e das aulas tira-dúvidas (não foi possível ouvir). A regra de crédito veio do texto do feedback da AV02; vale alguém do grupo reassistir para confirmar D1.
- O conteúdo do "Template P.I UniSENAI" (arquivo .pptx no AVA, não baixado).
- As issues e o Kanban do GitHub (sem acesso nesta sessão).
