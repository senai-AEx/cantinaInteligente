# Decisões de projeto para iniciar a AV04

Estas são **decisões iniciais de implementação para o protótipo**, com base no negócio e nas entregas. **A stack ainda depende da decisão do grupo:** Python + Flask, SQLite e HTML/CSS/JavaScript são a proposta inicial, sem confirmação da equipe. Após a votação, alinhar dependências, migração, documentação e issues. Mudanças posteriores devem ser registradas aqui.

| Tema | Decisão | Motivo |
| --- | --- | --- |
| Plataforma | Web responsiva em HTML, CSS e JavaScript; estrutura preparada para PWA. | Uma interface atende celular e desktop como proposto na AV02. Instalação PWA fica após o CRUD, pois exige manifesto, ícones e contexto seguro. |
| Backend | Python com Flask. | API e páginas no mesmo projeto, com integração direta ao banco e pouco código inicial. |
| Banco | SQLite local para a AV04, com migrações SQL. | Banco relacional sem servidor separado, adequado à demonstração e ao custo baixo do projeto. |
| Código do produto | `codigo_produto` único: EAN/GTIN se houver, senão código interno. QR identifica a cantina. | Usa o código já presente nas embalagens e resolve a divergência com `codigo_qr` no DER da AV03. |
| Exclusão | Inativação reversível (`status = INATIVO`). | Preserva referências de compras, estoque e auditoria, em linha com RNF10 da AV03. |
| Preço | Inteiro em centavos no banco. | Evita erro de arredondamento, como prevê RNF05 da AV02. |
| Estoque | Quantidade inicial no produto; mínimo/máximo para alerta/reposição. | Compatibiliza DER da AV03 com RF04 da AV02; movimentos virão em outra etapa. |
| Validade | Menor validade das unidades em estoque, opcional. | Atende à AV03 sem criar controle de lotes agora; AV02 prevê lotes/FEFO para evolução. |
| Foto e selos | Caminho de foto local opcional e dois booleanos para zero lactose/zero açúcar. | Atende à exibição do RF03 sem depender de serviço externo na apresentação. |
| Autoria | CRUD administrativo; registrar autor/origem no log. | AV03 reserva manutenção ao administrador e pede auditoria. Login completo é trabalho posterior; a AV04 deve rodar localmente até haver controle de acesso. |

## Observações de escopo

- O esquema SQL em `database/migrations/001_produtos.sql` é a primeira base concreta; não cria telas, rotas nem autenticação.
- Não publicar o protótipo administrativo sem login e autorização por perfil. As entregas do grupo exigem essa proteção para uso real.
- Se o professor mentor exigir outro campo ou exclusão física, ajustar esta decisão, o esquema e os critérios de aceite antes da implementação.

Fontes de produto: `AV02_Cantina_Inteligente_Solucao_e_Requisitos.pdf` e `AV03_GRUPO_4.pdf`. Referências técnicas: [Flask com SQLite](https://flask.palletsprojects.com/en/stable/tutorial/database/) e [requisitos para instalar uma PWA](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable).
