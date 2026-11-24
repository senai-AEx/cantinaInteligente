# Cantina Inteligente — Grupo 4

Sistema web para a **Cantina da Honestidade do SENAI Fraiburgo (SC)**. O usuário se cadastra, declara os depósitos que fez na caixa da cantina (créditos em uma carteira virtual) e registra as próprias compras, que são descontadas do saldo. A administração gerencia produtos e usuários, acompanha as movimentações e emite relatórios.

Projeto Aplicado II — Centro Universitário SENAI Santa Catarina. Stack: **Python + Flask + MySQL**, com telas em HTML, CSS e JavaScript.

## O que o sistema faz

| Para o cliente | Para a administração |
| --- | --- |
| Cadastro e login por matrícula, e-mail ou CPF | Cadastro de produtos (preço de compra e de venda, estoque, foto) |
| Catálogo com preços e sacola de compras | Gestão de usuários (editar, inativar, ajustar saldo) |
| Carteira: adicionar crédito e consultar saldo e extrato | Movimentações financeiras com filtros |
| Compra com desconto automático do saldo e baixa do estoque | Relatórios de vendas, saldos, estoque e depósitos declarados |
| Histórico de compras | Auditoria das alterações de produtos |
| Troca da própria senha | Redefinição de senha de um usuário |
| Compra rápida pelo QR Code do produto | QR Codes para imprimir (cantina e produtos) |

Nada é apagado do banco: excluir um produto ou um usuário apenas o deixa inativo.

## Pré-requisitos

- **Python 3.10** ou mais novo.
- **MySQL 8** (8.0.16 ou mais nova) instalado e ligado no computador.
- **Git**, para baixar o projeto.

Não é preciso Docker nem Make. O `instalar.py` cria o ambiente Python (`.venv`) e instala as bibliotecas do `requirements.txt` (Flask, mysql-connector-python, python-dotenv e segno). A lista completa, com o motivo de cada item, está em [docs/arquitetura.md](docs/arquitetura.md#dependências).

## Executar localmente

> Primeira vez? Siga o passo a passo completo, com a instalação do MySQL no Windows, macOS e Linux e os problemas comuns, em **[docs/como-rodar.md](docs/como-rodar.md)**.

Com o MySQL instalado e ligado, são três passos. Rode os comandos dentro da pasta do projeto.

**1. Baixar o projeto**

```sh
git clone https://github.com/senai-AEx/cantinaInteligente.git
cd cantinaInteligente
git switch develop
```

**2. Instalar (só na primeira vez)**

```sh
python instalar.py
```

Cria o `.env` (gerando as senhas e a chave que faltam), o ambiente `.venv` com as bibliotecas, o banco `cantina_inteligente` com as tabelas, os produtos de exemplo e os usuários de demonstração. Pede a senha do usuário `root` do MySQL, que você definiu ao instalar o MySQL. Pode ser rodado de novo sem problema. O `.env` é só seu e não vai para o GitHub.

**3. Ligar o sistema**

```sh
python iniciar.py
```

Confere a conexão com o MySQL, aplica as migrações que faltam e liga o sistema em **http://127.0.0.1:5000**, abrindo o navegador. `Ctrl+C` desliga o sistema; o MySQL continua ligado. Use `python iniciar.py --sem-navegador` para não abrir o navegador.

No Windows, se `python` abrir a Microsoft Store, use `py -3` no lugar de `python`. No macOS e no Linux, use `python3`.

Para ver a matrícula e a senha dos usuários de demonstração (ficam só no seu `.env`):

```sh
python scripts/credenciais.py
```

| Endereço | Tela |
| --- | --- |
| http://127.0.0.1:5000/ | Início |
| http://127.0.0.1:5000/html/catalogo_produtos.html | Catálogo e sacola |
| http://127.0.0.1:5000/html/cadastro.html | Criar conta |
| http://127.0.0.1:5000/html/login.html | Entrar |
| http://127.0.0.1:5000/html/minha_conta.html | Saldo, créditos, extrato e compras |
| http://127.0.0.1:5000/html/catalogo_produtos_adm.html | Painel administrativo |
| http://127.0.0.1:5000/api/health/db | Teste da conexão com o banco |

### Comandos

| Comando | Ação |
| --- | --- |
| `python instalar.py` | Instalação completa (primeira vez; pode repetir) |
| `python iniciar.py` | Liga o sistema (`--sem-navegador` não abre o navegador) |
| `python scripts/credenciais.py` | Mostra os dados dos usuários de demonstração |
| `python scripts/criar_admin.py` | Cria ou redefine o administrador (dados `ADMIN_*` do `.env`) |
| `python scripts/banco.py testar` | Confere a conexão com o MySQL |
| `python scripts/banco.py backup` | Grava uma cópia do banco em `backups/` |
| `python scripts/banco.py restaurar ARQUIVO` | Volta o banco a uma cópia (substitui os dados atuais) |
| `python scripts/testes.py` | Roda os testes automatizados |

Outros comandos do banco (`migrar`, `semear`) e os atalhos opcionais com `make` estão em [docs/como-rodar.md](docs/como-rodar.md#comandos-do-dia-a-dia).

### QR Code e teste pelo celular

No painel, a tela **QR Codes** gera o código da cantina (abre o catálogo) e um por produto (abre o catálogo com o item já na sacola), prontos para imprimir.

O QR Code leva o endereço do sistema. Com o padrão (`127.0.0.1`) ele só abre neste computador. Para abrir pelo celular na mesma rede Wi-Fi, ajuste no `.env` e rode `python iniciar.py` de novo:

```
APP_HOST=0.0.0.0
URL_PUBLICA=http://<IP deste computador na rede>:5000
```

Use isso só em rede de confiança: o sistema fica acessível a quem estiver na mesma rede.

### Problemas comuns

Os erros mais comuns (MySQL desligado, senha do root errada, Python antigo) estão com a mensagem exata e a solução em [docs/como-rodar.md](docs/como-rodar.md#problemas-comuns). Se aparecer "Não encontrei o MySQL em 127.0.0.1:3306", ligue o serviço do MySQL e rode o comando de novo.

## Organização

```
instalar.py        instalação completa (rode uma vez)
iniciar.py         liga o sistema
assets/produtos/   fotos enviadas pela tela (não versionadas)
database/          migrations/, seeds/ e schema.sql
docs/              documentação (índice em docs/README.md)
scripts/           banco.py (instalar, migrar, semear, testar, backup, restaurar),
                   criar_demo.py, criar_admin.py, credenciais.py, testes.py e
                   _ambiente.py (ajudas comuns: .venv e .env)
src/backend/       API Flask: usuarios, produtos, carteira, compras, admin e qr,
                   cada módulo em camadas routes → controller → service → repository
src/frontend/      telas HTML, CSS e JavaScript (servidas pelo próprio Flask)
tests/             testes automatizados
```

- [Como rodar o projeto](docs/como-rodar.md)
- [Arquitetura e pastas](docs/arquitetura.md)
- [Contrato da API](docs/contrato-api.md) e [API de produtos](docs/contrato-api-produtos.md)
- [Documento do Sistema](docs/documento-do-sistema.md)
- [Roteiro de testes manuais](docs/testes-manuais.md)
- [Plano de execução AV05/AV06](docs/plano-de-execucao.md)

## Segurança

- Senhas guardadas apenas como hash; sessão por cookie `HttpOnly`.
- As rotas administrativas exigem perfil de administrador no servidor (não basta esconder o botão na tela).
- Compra e crédito acontecem em transação: saldo, estoque e extrato nunca ficam em desacordo.
- O ambiente local usa credenciais de demonstração. Antes de publicar em um servidor real, troque as senhas do `.env` e sirva o sistema por HTTPS.

## Equipe

Equipe 4 (integrantes listados no Documento do Sistema). Fluxo de trabalho em [CONTRIBUTING.md](CONTRIBUTING.md).
