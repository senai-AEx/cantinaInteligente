# Contrato do CRUD de Produtos

A stack definida pelo grupo é Python + Flask + MySQL. Nesta branch, as rotas de saúde e a listagem inicial foram preparadas. As operações de escrita e a interface ainda serão implementadas nas issues seguintes.

| Operação | Rota | Resultado esperado |
| --- | --- | --- |
| Saúde da API | `GET /api/health` | `200` e `{"status":"ok"}`. |
| Saúde do banco | `GET /api/health/db` | `200` e confirma `SELECT 1`; `503` se o MySQL estiver indisponível. |
| Listar/buscar | `GET /api/produtos?q=&status=` | Lista com filtros; por padrão, inclui ativos e inativos na área administrativa. |
| Consultar um | `GET /api/produtos/{id}` | Detalhes do produto ou 404. |
| Incluir | `POST /api/produtos` | Valida, insere e audita; responde 201. |
| Alterar | `PUT /api/produtos/{id}` | Valida, atualiza e audita; responde 200 ou 404. |
| Inativar | `DELETE /api/produtos/{id}` | Define `status = INATIVO`, audita e responde 200 ou 404. |
| Reativar | `PATCH /api/produtos/{id}/reativar` | Define `status = ATIVO`, audita e responde 200 ou 404. |

Erros de validação devem responder **422** com mensagens por campo. Código duplicado, preço não positivo, estoque negativo, data inválida e máximo menor que mínimo são casos essenciais.

As escritas devem usar transações MySQL: o produto e seu registro de auditoria são confirmados em conjunto ou revertidos juntos. A lista administrativa inclui produtos inativos; o catálogo disponível mostra somente produtos ativos, com estoque positivo e validade vigente ou não informada.

Todas as operações administrativas devem exigir perfil Administrador quando houver autenticação. Durante a AV04, execute localmente e não exponha essas rotas numa rede pública sem autorização por perfil.