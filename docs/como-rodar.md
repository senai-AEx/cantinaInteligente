# Como rodar o projeto

Este guia leva você do zero até o sistema funcionando no seu computador. Leia uma etapa de cada vez e confira o "Você deve ver" antes de seguir.

Tempo estimado: 30 a 40 minutos na primeira vez (a maior parte é download e instalação). Nas próximas vezes, basta `make up`.

> Se algo der errado, vá direto para [Problemas comuns](#problemas-comuns). Quase todos os erros que aparecem estão lá.

---

## 1. O que você precisa instalar

| Programa | Para que serve | Como verificar |
| --- | --- | --- |
| **Python 3** (versão 3.10 ou mais nova) | Roda o servidor do sistema | `python --version` ou `py -3 --version` |
| **Docker Desktop** | Roda o banco de dados MySQL em um "contêiner" | Abra o programa e espere o ícone da baleia ficar parado |
| **GNU Make** | Executa os comandos do projeto (`make up`, `make demo`...) | `make --version` |
| **Git** | Baixa o projeto do GitHub | `git --version` |

### Windows

1. **Python:** baixe em [python.org](https://www.python.org/downloads/) e, na primeira tela do instalador, **marque "Add python.exe to PATH"** antes de clicar em Install.
   - Se o comando `python` abrir a Microsoft Store, desative o atalho em *Configurações → Aplicativos → Configurações avançadas de aplicativos → Aliases de execução de aplicativo* ou use o comando `py -3` no lugar de `python` (veja [Problemas comuns](#problemas-comuns)).
2. **Docker Desktop:** baixe em [docker.com](https://www.docker.com/products/docker-desktop/). Ele pode pedir para instalar o WSL 2; aceite e reinicie o computador se pedir.
3. **Make:** é o programa que mais costuma faltar no Windows. Escolha uma das opções:
   - pelo Chocolatey, se você já o tiver: `choco install make`;
   - ou pelo GnuWin32 em [gnuwin32.sourceforge.net](https://gnuwin32.sourceforge.net/packages/make.htm), instalando o pacote "Make".

   Depois de instalar, **feche e abra o terminal** para o `make` ser reconhecido.
4. **Git:** baixe em [git-scm.com](https://git-scm.com/downloads).

### macOS e Linux

- **Python 3:** já vem na maioria dos sistemas; confirme com `python3 --version`. Se faltar, instale pelo gerenciador de pacotes (Homebrew no macOS, `apt` no Ubuntu).
- **Docker Desktop** (macOS) ou **Docker Engine** (Linux).
- **Make** e **Git:** `xcode-select --install` no macOS já traz os dois; no Ubuntu, `sudo apt install make git`.

---

## 2. Baixar o projeto

Abra o terminal (PowerShell no Windows, Terminal no macOS/Linux) e escolha uma pasta, por exemplo `C:\Projetos` ou `~/Projetos`:

```bash
git clone https://github.com/senai-AEx/cantinaInteligente.git
cd cantinaInteligente
git switch develop
```

Você deve ver: a mensagem `Switched to a new branch 'develop'` ou `Switched to branch 'develop'`.

> O repositório é privado. Se o `git clone` pedir usuário e senha, peça acesso ao grupo e use o login do GitHub.

---

## 3. Preparar o projeto (só na primeira vez)

Dentro da pasta `cantinaInteligente`:

```bash
make setup
```

Esse comando faz três coisas:

- cria o arquivo **`.env`** (as configurações do seu computador), com senhas aleatórias já geradas;
- instala as bibliotecas Python dentro da pasta `.venv`;
- confere se tudo está pronto.

Você deve ver no final: `Ambiente pronto. Use make up para iniciar a aplicação.`

> **Se o `make` disser que `python` não existe**, rode o mesmo comando assim:
>
> ```bash
> make PYTHON="py -3" setup
> ```
>
> No macOS/Linux, use `make PYTHON=python3 setup`.

### O arquivo `.env`

O `.env` fica na raiz do projeto. Você só precisa mexer nele em casos específicos, listados em [Problemas comuns](#problemas-comuns). Ele não vai para o GitHub, então suas senhas ficam só no seu computador.

---

## 4. Subir o sistema

Com o **Docker Desktop aberto**, rode:

```bash
make up
```

O que acontece:

1. cria (ou liga) o banco de dados MySQL em um contêiner chamado `cantina-mysql`;
2. cria as tabelas que o sistema precisa;
3. liga o servidor do sistema.

> **A primeira vez demora.** O Docker baixa a imagem do MySQL (alguns minutos, conforme a internet). Espere aparecer `Running on http://127.0.0.1:5000`.

Você deve ver algo parecido com:

```
Sistema:        http://127.0.0.1:5000/
Catálogo:       http://127.0.0.1:5000/html/catalogo_produtos.html
Administração:  http://127.0.0.1:5000/html/catalogo_produtos_adm.html
Teste do banco: http://127.0.0.1:5000/api/health/db
Pressione Ctrl+C para parar.
```

**Deixe este terminal aberto.** Ele é o servidor. Para parar, aperte `Ctrl+C` nele.

---

## 5. Criar os dados de demonstração

Abra **outro terminal**, na mesma pasta do projeto, e rode:

```bash
make demo
```

Esse comando insere produtos de exemplo e cria dois usuários para você testar:

- um **administrador**;
- um **cliente**, com R$ 50,00 de crédito para já poder comprar.

Você deve ver: `Crédito inicial de R$ 50,00 lançado para o cliente de demonstração.`

Agora, para descobrir a matrícula e a senha de cada um:

```bash
make credenciais
```

Ele mostra matrícula, e-mail, CPF e senha. Esses dados ficam só no seu `.env`; não os compartilhe nem os coloque em trabalhos entregues.

---

## 6. Abrir o sistema

Abra o navegador e acesse:

| Endereço | O que é |
| --- | --- |
| http://127.0.0.1:5000/ | Página inicial |
| http://127.0.0.1:5000/html/login.html | Entrar |
| http://127.0.0.1:5000/html/catalogo_produtos.html | Catálogo e sacola (área do cliente) |
| http://127.0.0.1:5000/html/minha_conta.html | Saldo, crédito, extrato e compras (precisa estar logado) |
| http://127.0.0.1:5000/html/catalogo_produtos_adm.html | Painel administrativo (precisa ser administrador) |

Use **127.0.0.1**, não `localhost`. Os dois funcionam, mas o login de um não vale para o outro.

---

## 7. Roteiro de 5 minutos

Use os dados que apareceram em `make credenciais`.

**Como cliente:**

1. Entre com a **matrícula do cliente** e a senha dele.
2. No catálogo, clique em **Adicionar à sacola** em um produto (por exemplo, Suco de Laranja).
3. Clique em **Finalizar compra** e depois em **Confirmar compra**. Você verá o número da compra e o novo saldo.
4. Em **Minha conta**, veja o extrato e a compra registrada. Em **Adicionar crédito**, teste declarar um depósito (marque a declaração antes de confirmar).
5. Clique em **Sair**.

**Como administrador:**

6. Entre com a **matrícula do administrador**.
7. No painel de **produtos**, veja o custo (preço de compra) e o preço de venda de cada item.
8. Em **Relatórios**, abra as abas **Vendas** e **Compras**: a compra que você fez como cliente aparece lá.
9. Em **QR Codes**, veja os códigos que podem ser impressos.

---

## Comandos do dia a dia

| Comando | Quando usar |
| --- | --- |
| `make up` | Para ligar o sistema (com o Docker aberto). |
| `Ctrl+C` no terminal do `make up` | Para desligar o servidor. O banco continua ligado. |
| `make down` | Para desligar o banco também. Os dados são preservados. |
| `make status` | Para ver se o banco e o sistema estão rodando. |
| `make credenciais` | Para ver matrícula e senha dos usuários de demonstração. |
| `make admin` | Para criar ou trocar a senha do administrador (depois de editar `ADMIN_SENHA` no `.env`). |
| `make test` | Para rodar os testes automatizados. |
| `make backup` | Para guardar uma cópia do banco em `backups/`. |
| `make restore ARQUIVO=backups/nome.sql` | Para voltar o banco a uma cópia. **Substitui os dados atuais.** |

---

## Problemas comuns

### `make` não é reconhecido (ou "não é um comando")

O Make não está instalado ou o terminal não foi reaberto depois da instalação. Instale (veja a seção 1), feche o terminal e abra de novo.

### `python` não é reconhecido, ou abre a Microsoft Store

No Windows, use o lançador `py`:

```bash
py -3 --version
make PYTHON="py -3" setup
make PYTHON="py -3" up
```

Ou reinstale o Python pelo python.org marcando **Add python.exe to PATH**.

### "Não consegui acessar o Docker"

O Docker Desktop não está aberto. Abra o programa, espere o ícone parar de animar e rode o comando de novo.

### "A porta 3306 já está em uso por outro programa"

Outro MySQL está instalado no seu computador. Abra o arquivo `.env` e troque:

```
MYSQL_PORT=3307
```

Se o contêiner `cantina-mysql` já tiver sido criado antes com a porta 3306, remova só o contêiner (os dados ficam guardados no volume e não se perdem):

```bash
make down
docker rm cantina-mysql
make up
```

### "Senha root incorreta"

O contêiner `cantina-mysql` foi criado antes com outra senha root. No `.env`, coloque em `MYSQL_ROOT_PASSWORD` a senha que foi usada na primeira vez (no `.env.example` do projeto, o padrão é `masterkey`), e rode `make up` de novo.

### Abri o sistema e o catálogo está vazio

Você ainda não criou os dados de demonstração. Rode `make demo` (com o `make up` ligado).

### O login do administrador não funciona

Confira estas coisas, nessa ordem:

1. Rode `make credenciais` e use **exatamente** a senha que aparece ali. Ela fica no `.env` e não muda sozinha.
2. Se você trocou a senha no `.env`, rode `make admin`. Se a mensagem disser que a senha não atende à regra, ela precisa ter **de 8 a 72 caracteres, com pelo menos uma letra e um número**. Enquanto ela não for trocada, a senha anterior continua valendo.
3. Se o navegador já estava logado como cliente, clique em **Sair** antes. Quem já está logado é levado direto para a área do seu perfil (o administrador vai ao painel; o cliente, ao catálogo) quando abre a tela de login.
4. Confira o endereço: use `http://127.0.0.1:5000`.

### Vejo `401` no console do navegador

É normal quando nenhum usuário está logado: a tela pede os dados de quem entrou e recebe "não logado". Não é erro do sistema.

### A porta 5000 já está em uso

Outro programa, ou outra cópia do sistema, está usando a porta. Rode `make status` para ver. Se for uma cópia antiga do sistema, feche o terminal dela com `Ctrl+C`.

### O QR Code não abre no celular

Com o endereço padrão (`127.0.0.1`), o QR Code só abre no próprio computador. Para usar pelo celular, na mesma rede Wi-Fi, edite o `.env`:

```
APP_HOST=0.0.0.0
URL_PUBLICA=http://<IP deste computador>:5000
```

Depois rode `make up` de novo. No Windows, a Firewall pode perguntar se deve liberar o acesso: permita na rede privada.

### Quero recomeçar do zero (apaga tudo)

Os comandos abaixo **apagam todos os dados** do banco. Use só se você tem certeza:

```bash
make down
docker rm cantina-mysql
docker volume rm cantina-mysql-data
make up
make demo
```

Se você fez um backup antes, prefira `make restore` com o arquivo de `backups/`.

---

## Sem Docker (avançado)

Use este caminho só se não for possível usar o Docker. Ele é mais trabalhoso.

1. Instale o **MySQL 8** (versão 8.0.16 ou mais nova) e abra o **MySQL Workbench**.
2. Execute o arquivo `database/schema.sql` (cria o banco `cantina_inteligente` e as tabelas).
3. Execute `database/seeds/produtos_exemplo.sql` para ter produtos no catálogo.
4. No `.env`, informe o usuário e a senha do MySQL que você instalou (`MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_PORT`). Para estudo, pode ser o usuário `root`.
5. Na pasta do projeto, prepare o ambiente Python:
   - Windows (PowerShell): `make setup`
   - macOS/Linux: `make setup` (ou `make PYTHON=python3 setup`)
6. Crie os usuários de demonstração:
   - Windows: `.venv\Scripts\python scripts\criar_demo.py`
   - macOS/Linux: `.venv/bin/python scripts/criar_demo.py`
7. Ligue o servidor:
   - Windows: `.venv\Scripts\python -m flask --app src.backend.app run --debug`
   - macOS/Linux: `.venv/bin/python -m flask --app src.backend.app run --debug`

Depois, use os mesmos endereços da seção 6. Sem Docker, os comandos `make up`, `make down`, `make backup` e `make restore` não funcionam.

---

## Glossário

- **Terminal:** a janela onde você digita os comandos. PowerShell no Windows, Terminal no macOS e no Linux.
- **Make:** programa que executa atalhos guardados no arquivo `Makefile`. Por exemplo, `make up` roda vários comandos de uma vez.
- **Contêiner (Docker):** um "computador virtual" leve que roda o MySQL isolado do resto do seu computador.
- **Volume (Docker):** a pasta onde o contêiner guarda os dados. Por isso os dados sobrevivem quando o contêiner é desligado.
- **Migração:** um arquivo SQL que altera o banco (cria uma tabela, adiciona uma coluna). O `make up` aplica as que faltam, na ordem.
- **`.env`:** arquivo de configuração local, com senhas e endereços. Não vai para o GitHub.
- **Porta:** o "número da porta" por onde um programa recebe conexões. O sistema usa a 5000; o MySQL, a 3306 (ou 3307 no seu caso).
- **Ambiente virtual (`.venv`):** pasta com as bibliotecas Python do projeto, separada das outras instalações do computador.
