# Como rodar o projeto

Este guia leva você do zero até o sistema funcionando no seu computador. Leia uma etapa de cada vez e confira o "Você deve ver" antes de seguir.

Tempo estimado: 30 a 40 minutos na primeira vez (a maior parte é download e instalação). Nas próximas vezes, basta ligar o MySQL e rodar `python iniciar.py`.

> Se algo der errado, vá direto para [Problemas comuns](#problemas-comuns). Quase todos os erros que aparecem estão lá.

**Resumo:** você instala o Python e o MySQL uma vez. Depois baixa o projeto e roda `python instalar.py` (também uma vez só). Para usar o sistema, roda `python iniciar.py`. Este projeto não usa Docker, e o programa Make é opcional.

---

## 1. O que você precisa instalar

| Programa | Para que serve | Como verificar |
| --- | --- | --- |
| **Python 3** (versão 3.10 ou mais nova) | Roda o servidor do sistema e os scripts de instalação | `python --version` ou `py -3 --version` |
| **MySQL 8** (8.0.16 ou mais nova) | Guarda os dados do sistema (produtos, usuários, saldos e compras) | Veja se o serviço do MySQL está ligado (instruções abaixo) |
| **Git** | Baixa o projeto do GitHub | `git --version` |

Nos exemplos deste guia usamos `python`. No macOS e no Linux, use `python3`. No Windows, se `python` abrir a Microsoft Store, use `py -3` (veja [Problemas comuns](#problemas-comuns)).

### Windows

1. **Python:** baixe em [python.org](https://www.python.org/downloads/) e, na primeira tela do instalador, **marque "Add python.exe to PATH"** antes de clicar em Install.
   - Se o comando `python` abrir a Microsoft Store, desative o atalho em *Configurações → Aplicativos → Configurações avançadas de aplicativos → Aliases de execução de aplicativo* ou use `py -3` no lugar de `python`.
2. **MySQL 8:** baixe o **MySQL Installer** em [dev.mysql.com](https://dev.mysql.com) (procure por "MySQL Installer for Windows").
   - Escolha **Server only** ou **Developer Default**.
   - Na configuração, defina a senha do usuário **root** e **anote**. Você vai digitá-la no `python instalar.py`.
   - Mantenha a porta **3306** (é a padrão).
   - Ao final, o serviço fica com o nome **MySQL80** (ou **MySQL84**).

   > Alternativa pelo terminal: `winget install Oracle.MySQL`. Esse comando instala só o servidor. A senha do root e a criação do serviço não ficam prontas sozinhas: confira se o MySQL foi instalado com senha de root e se o serviço está ligado antes de seguir. [CONFIRMAR: testar `winget install Oracle.MySQL` em um Windows limpo e anotar se o assistente pede a senha root e cria o serviço MySQL80.]

3. **Git:** baixe em [git-scm.com](https://git-scm.com/downloads).

**Como ligar o MySQL no Windows:** abra **Serviços** (digite `services.msc` na busca do Windows), clique com o botão direito em **MySQL80** (ou MySQL84) e escolha **Iniciar**. Você deve ver o status **Em execução**.

### macOS

1. **Python 3:** confirme com `python3 --version`. Se faltar, instale pelo python.org ou pelo Homebrew.
2. **MySQL 8:** com o [Homebrew](https://brew.sh) instalado, rode no Terminal:

   ```sh
   brew install mysql
   brew services start mysql
   ```

   Depois, defina a senha do usuário root com `mysql_secure_installation` e anote. [CONFIRMAR: testar em um macOS real; a forma de entrar como root no MySQL do Homebrew pode variar conforme a instalação.]

3. **Git:** `xcode-select --install` já traz o Git.

### Linux (Ubuntu ou Debian)

1. **Python 3:** confirme com `python3 --version`. Se faltar: `sudo apt install python3`. [CONFIRMAR: em Ubuntu/Debian pode ser preciso instalar também `python3-venv` (`sudo apt install python3-venv`) para o `instalar.py` criar o ambiente `.venv`.]
2. **MySQL 8:**

   ```sh
   sudo apt install mysql-server
   sudo mysql_secure_installation
   ```

   Defina a senha do usuário root e anote. Para ligar o MySQL: `sudo systemctl start mysql`.
3. **Git:** `sudo apt install git`.

### Porta do MySQL

A porta padrão do MySQL é a **3306**. Se você já tem outro MySQL no computador usando essa porta, configure o MySQL novo para a porta **3307** e veja o item [Problemas comuns](#problemas-comuns).

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

## 3. Instalar o sistema (só na primeira vez)

Confirme que o MySQL está ligado. Depois, dentro da pasta `cantinaInteligente`, rode:

```bash
python instalar.py
```

O comando faz tudo sozinho, em 4 etapas:

| Etapa | O que acontece |
| --- | --- |
| **1/4** | Cria o arquivo `.env` (as configurações do seu computador) e gera as senhas e a chave de segurança que faltam. |
| **2/4** | Cria a pasta `.venv` (o ambiente Python do projeto) e instala as bibliotecas. |
| **3/4** | Confere o MySQL, pede a senha do root, cria o banco `cantina_inteligente` e o usuário do sistema, cria as tabelas e insere os produtos de exemplo (só se a tabela de produtos estiver vazia). |
| **4/4** | Cria os usuários de demonstração: um administrador e um cliente com R$ 50,00 de crédito. |

Na etapa 3/4, o programa pede a senha do root (a que você anotou ao instalar o MySQL):

```
Senha do usuário 'root' do MySQL (a que você criou ao instalar o MySQL):
```

Quando você digita a senha, **nada aparece na tela**, nem asteriscos. É normal. Digite a senha e aperte Enter.

Você deve ver no final:

```
Tudo pronto!
Para ligar o sistema, rode:
    python iniciar.py
```

> Você pode rodar `python instalar.py` de novo quando quiser. O que já estiver pronto é conferido e mantido. Ele vai pedir a senha do root outra vez.

### O arquivo `.env`

O `.env` fica na raiz do projeto e é criado pelo `instalar.py`. Ele guarda as configurações do seu computador: endereço e porta do MySQL, senhas e a chave de segurança. Para o uso normal, você não precisa editá-lo. Ele não vai para o GitHub, então suas senhas ficam só no seu computador. Não o compartilhe nem coloque os dados dele em trabalhos entregues.

---

## 4. Ligar o sistema

Com o MySQL ligado, rode, dentro da pasta do projeto:

```bash
python iniciar.py
```

O que acontece:

1. confere a conexão com o MySQL;
2. aplica as migrações que faltam (alterações no banco, feitas em ordem);
3. liga o servidor do sistema e abre o navegador.

Você deve ver algo parecido com:

```
Banco conectado (MySQL 8.x.x).
Sistema ligado!
  Início:          http://127.0.0.1:5000/
  Catálogo:        http://127.0.0.1:5000/html/catalogo_produtos.html
  Administração:   http://127.0.0.1:5000/html/catalogo_produtos_adm.html

Para parar, aperte Ctrl+C.
```

**Deixe este terminal aberto.** Ele é o servidor. Para desligar o sistema, aperte `Ctrl+C` nele. O MySQL continua ligado.

Para ligar sem abrir o navegador, use `python iniciar.py --sem-navegador`.

---

## 5. Dados de demonstração

O `instalar.py` já criou os usuários de demonstração. Para ver a matrícula, o e-mail, o CPF e a senha de cada um, rode:

```bash
python scripts/credenciais.py
```

Você deve ver dois blocos, **Administrador** e **Cliente**, com matrícula, e-mail, CPF e senha. O login aceita matrícula, e-mail ou CPF.

Esses dados ficam só no seu `.env`. Não os compartilhe nem os coloque em trabalhos entregues.

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

Use os dados que apareceram em `python scripts/credenciais.py`.

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

Todos são rodados dentro da pasta do projeto. Você não precisa ativar o `.venv`: os scripts usam o ambiente sozinhos.

| Comando | Quando usar |
| --- | --- |
| `python iniciar.py` | Para ligar o sistema (com o MySQL ligado). |
| `Ctrl+C` no terminal do `iniciar.py` | Para desligar o sistema. O MySQL continua ligado. |
| `python scripts/credenciais.py` | Para ver matrícula e senha dos usuários de demonstração. |
| `python scripts/criar_admin.py` | Para criar ou trocar a senha do administrador (veja o bloco abaixo). |
| `python scripts/banco.py testar` | Para conferir se o sistema consegue falar com o MySQL. |
| `python scripts/banco.py migrar` | Para aplicar as migrações que faltam (o `iniciar.py` já faz isso). |
| `python scripts/banco.py semear` | Para inserir os produtos de exemplo, se a tabela de produtos estiver vazia. |
| `python scripts/banco.py backup` | Para guardar uma cópia do banco em `backups/`. |
| `python scripts/banco.py restaurar backups/ARQUIVO.sql` | Para voltar o banco a uma cópia. **Substitui os dados atuais.** |
| `python scripts/testes.py` | Para rodar os testes automatizados. |

### Atalhos com make (opcional)

Se o seu computador tiver o programa **Make**, os atalhos abaixo funcionam. Eles são opcionais: os comandos `python` fazem o mesmo.

| Atalho | Comando equivalente |
| --- | --- |
| `make setup` | `python instalar.py` |
| `make up` | `python iniciar.py` |
| `make demo` | `python scripts/banco.py semear` e depois `python scripts/criar_demo.py` |
| `make admin` | `python scripts/criar_admin.py` |
| `make credenciais` | `python scripts/credenciais.py` |
| `make migrate` | `python scripts/banco.py migrar` |
| `make seed` | `python scripts/banco.py semear` |
| `make backup` | `python scripts/banco.py backup` |
| `make restore ARQUIVO=backups/arquivo.sql` | `python scripts/banco.py restaurar backups/arquivo.sql` |
| `make test` | `python scripts/testes.py` |

Os comandos `make down`, `make status`, `make db-up`, `make api` e `make web` não existem mais. Se você viu algum deles em outro material, ignore.

---

## Trocar a senha do administrador

1. Abra o arquivo `.env` (na pasta do projeto) com um editor de texto.
2. Troque o valor de `ADMIN_SENHA` pela senha nova: ela precisa ter **8 ou mais caracteres, com pelo menos uma letra e um número**. Salve o arquivo.
3. No terminal, dentro da pasta do projeto, rode:

   ```bash
   python scripts/criar_admin.py
   ```

4. Você deve ver: `Administrador atualizado: ...` seguido de `A senha é a que está em ADMIN_SENHA no seu arquivo .env.`

Se a senha não atender à regra, o comando diz o motivo e **nada é alterado**: a senha anterior continua valendo. Se o navegador estiver logado como cliente, clique em **Sair** antes de entrar como administrador.

---

## Problemas comuns

As mensagens abaixo são as que os scripts mostram. Procure o texto que aparece no seu terminal.

### "Não encontrei o MySQL em 127.0.0.1:3306"

A mensagem completa é:

```
Não encontrei o MySQL em 127.0.0.1:3306.
  Confira se o MySQL está instalado e ligado:
    Windows: abra 'Serviços' (services.msc) e inicie o serviço MySQL80 (ou MySQL84).
    macOS: rode 'brew services start mysql'.
    Linux: rode 'sudo systemctl start mysql'.
  Se o MySQL usa outra porta, ajuste MYSQL_PORT no .env.
```

Significa que o MySQL está **desligado** ou que o sistema procura em **outra porta**. Ligue o serviço (veja a seção 1) e rode o comando de novo. Se o seu MySQL usa outra porta, abra o `.env` e ajuste `MYSQL_PORT` (por exemplo, `MYSQL_PORT=3307`).

### "A senha do usuário root do MySQL está errada"

A mensagem completa é:

```
A senha do usuário root do MySQL está errada. Rode 'python instalar.py' de novo e digite a senha que você criou ao instalar o MySQL.
```

Rode `python instalar.py` de novo e digite a senha do root com atenção (lembre que nada aparece enquanto você digita). Se você não lembra a senha, [CONFIRMAR: procedimento para redefinir a senha do root no MySQL instalado em um computador de aluno.]

### Outro MySQL já usa a porta 3306

Se já existe outro MySQL no computador usando a porta 3306:

1. configure o MySQL novo para a porta **3307**;
2. no arquivo `.env`, troque `MYSQL_PORT=3306` por `MYSQL_PORT=3307`;
3. rode o comando de novo.

Sem a porta certa, o sistema pode falar com o outro MySQL, e a mensagem pode ser a da senha do root errada. [CONFIRMAR: mensagem exata que aparece quando a porta 3306 está ocupada por outro programa.]

### "O ambiente do projeto ainda não existe. Rode primeiro: python instalar.py"

Você rodou um comando antes da instalação. Rode `python instalar.py` (primeira vez) e depois o comando que deu erro.

### "Este projeto precisa de Python 3.10 ou mais novo. Você usou a versão X."

A mensagem completa é:

```
Este projeto precisa de Python 3.10 ou mais novo. Você usou a versão X.
Instale uma versão mais nova em python.org e rode de novo.
```

Instale o Python 3.10 ou mais novo pelo python.org (no Windows, marque **Add python.exe to PATH**), abra um terminal novo e rode o comando de novo.

### "`python` não é reconhecido", ou o terminal abre a Microsoft Store

No Windows, use o lançador `py` no lugar de `python`:

```bash
py -3 --version
py -3 instalar.py
py -3 iniciar.py
```

Ou reinstale o Python pelo python.org marcando **Add python.exe to PATH**.

### "O banco 'cantina_inteligente' ainda não existe" ou "O usuário 'cantina_app' do sistema não consegue entrar no banco"

As mensagens completas dizem para rodar `python instalar.py`. Rode o comando. Ele cria o banco e o usuário do sistema de novo, sem apagar dados que já existirem.

### "Preencha no .env (ou rode python instalar.py): ..."

Algum dado de acesso está vazio no `.env`. Rode `python instalar.py`, que preenche o que falta. Se você apagou um valor de propósito, coloque-o de volta.

### "Gerei os valores que faltavam: ..."

Não é erro. O `instalar.py` mostra essa mensagem quando preencheu sozinho o `.env` (senhas e chave de segurança). Você não precisa fazer nada.

### Abri o sistema e o catálogo está vazio

Você ainda não tem produtos no banco. Rode:

```bash
python scripts/banco.py semear
```

O comando insere os produtos de exemplo só se a tabela de produtos estiver vazia. Se ele disser `O banco já tem N produto(s); nenhum exemplo foi inserido.`, a tabela já tinha produtos e nada foi alterado. Atualize a página do catálogo.

### O login do administrador não funciona

Confira estas coisas, nessa ordem:

1. Rode `python scripts/credenciais.py` e use **exatamente** a senha que aparece ali. Ela fica no `.env` e não muda sozinha.
2. Se você trocou a senha no `.env`, rode `python scripts/criar_admin.py`. Se a mensagem disser que a senha não atende à regra, ela precisa ter **de 8 a 72 caracteres, com pelo menos uma letra e um número**. Enquanto ela não for trocada, a senha anterior continua valendo.
3. Se o navegador já estava logado como cliente, clique em **Sair** antes. Quem já está logado é levado direto para a área do seu perfil (o administrador vai ao painel; o cliente, ao catálogo) quando abre a tela de login.
4. Confira o endereço: use `http://127.0.0.1:5000`.

### Vejo `401` no console do navegador

É normal quando nenhum usuário está logado: a tela pede os dados de quem entrou e recebe "não logado". Não é erro do sistema.

### A porta 5000 já está em uso

Outro programa, ou outra cópia do sistema, está usando a porta 5000. Se for uma cópia antiga do sistema, feche o terminal dela com `Ctrl+C`. Depois rode `python iniciar.py` de novo. [CONFIRMAR: mensagem exata que o Python mostra nesse caso, no Windows e no macOS/Linux.]

### O QR Code não abre no celular

Com o endereço padrão (`127.0.0.1`), o QR Code só abre no próprio computador. Para usar pelo celular, na mesma rede Wi-Fi, edite o `.env`:

```
APP_HOST=0.0.0.0
URL_PUBLICA=http://<IP deste computador>:5000
```

Depois rode `python iniciar.py` de novo. No Windows, a Firewall pode perguntar se deve liberar o acesso: permita na rede privada.

### Login cai ao reiniciar o servidor

Falta a `SECRET_KEY` no `.env`. Rode `python instalar.py`: ele gera a chave que falta.

### Quero recomeçar do zero (apaga tudo)

**Atenção: estes procedimentos apagam os dados do sistema** (produtos, usuários, saldos, compras e histórico). Antes de começar, faça um backup com `python scripts/banco.py backup`.

**Opção 1: voltar a uma cópia (recomendado).** Se você tem um arquivo de `backups/`, rode, na pasta do projeto:

```bash
python scripts/banco.py restaurar backups/cantina-AAAAMMDD-HHMMSS.sql
```

Use o nome do seu arquivo. O comando mostra o aviso "Isso apaga os dados atuais do banco" e pede para digitar **SIM**. Só então ele substitui os dados. Você deve ver: `Banco restaurado a partir de ...`.

**Opção 2: apagar o banco e começar vazio.** Feche o `iniciar.py` (`Ctrl+C`). No MySQL Workbench, conecte com o usuário root e rode:

```sql
DROP DATABASE cantina_inteligente;
```

Esse comando **apaga todo o banco** `cantina_inteligente`, sem volta. Se o seu `.env` usa outro nome em `MYSQL_DATABASE`, use esse nome. Depois, na pasta do projeto, rode `python instalar.py` para criar tudo de novo.

Os backups ficam na pasta `backups/`. Eles contêm dados dos usuários, por isso não os envie para o GitHub: a pasta já está no `.gitignore`.

---

## Glossário

- **Terminal:** a janela onde você digita os comandos. PowerShell no Windows, Terminal no macOS e no Linux.
- **MySQL:** o programa que guarda os dados do sistema (o banco de dados). Fica instalado no seu computador e roda em segundo plano, como um serviço.
- **Serviço:** programa que roda em segundo plano. No Windows, o MySQL aparece em **Serviços**.
- **Migração:** um arquivo SQL que altera o banco (cria uma tabela, adiciona uma coluna). O `iniciar.py` aplica as que faltam, na ordem.
- **Backup:** uma cópia do banco em um arquivo `.sql`, guardada na pasta `backups/`.
- **`.env`:** arquivo de configuração local, com endereços, senhas e a chave de segurança. Não vai para o GitHub.
- **Porta:** o "número da porta" por onde um programa recebe conexões. O sistema usa a 5000; o MySQL, a 3306 (ou 3307, se a 3306 já estiver ocupada).
- **Ambiente virtual (`.venv`):** pasta com as bibliotecas Python do projeto, separada das outras instalações do computador. Quem cria é o `instalar.py`.
- **Make (opcional):** programa que executa atalhos. Não é obrigatório: os comandos `python` fazem o mesmo.
