# Contrato inicial do CRUD de produtos

Este contrato orienta a implementação; **as rotas ainda não existem**.

| Operação | Rota sugerida | Resultado esperado |
| --- | --- | --- |
| Listar/buscar | `GET /api/produtos?q=&status=` | Lista com filtros; por padrão, incluir ativos e inativos na área administrativa. |
| Consultar um | `GET /api/produtos/{id}` | Detalhes do produto ou 404. |
| Incluir | `POST /api/produtos` | Valida, insere e audita; responde 201. |
| Alterar | `PUT /api/produtos/{id}` | Valida, atualiza e audita; responde 200 ou 404. |
| Inativar | `DELETE /api/produtos/{id}` | Muda `status` para `INATIVO`, audita e responde 200 ou 404. |
| Reativar | `PATCH /api/produtos/{id}/reativar` | Muda para `ATIVO`, audita e responde 200 ou 404. |

Erros de validação devem responder **422** com mensagens por campo. Código duplicado, preço não positivo, estoque negativo, data inválida e máximo menor que mínimo são casos essenciais. A interface deve mostrar a mensagem no campo correspondente e impedir perda dos dados já digitados.

Telas mínimas: **lista/consulta** (busca, filtro de situação e ações), **formulário de inclusão/edição** (campos e mensagens de erro) e **confirmação de inativação**. O botão de reativar aparece em produtos inativos. A visão de catálogo usa apenas produtos `ATIVO`, com estoque positivo e validade vigente ou não informada.

Todas as operações administrativas devem exigir perfil Administrador quando houver autenticação. Para a AV04 local, não expor essas rotas em rede pública sem essa camada.
