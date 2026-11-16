from flask import Blueprint

from backend.produtos import controller as produto_controller

# Blueprint para criar o agrupador de rotas.
rotas = Blueprint("rotas", __name__)

# ---------- rotas ----------
# Adicionando rotas no agrupamento de rotas.

# Página inicial
@rotas.route("/")
def pagina_inicial():
    return "Bem vindo!!"

# PRODUTOS!
# Produtos GET
@rotas.get("/api/produtos/")
def listar_produtos():
    return produto_controller.listar_produtos()

# Produtos GET
@rotas.get("/api/produtos/<int:id_produto>")
def consultar_produto(id_produto):
    return produto_controller.consultar_produto(id_produto)

# Produtos POST
@rotas.post("/api/produtos/")
def incluir_produto():
    return "Produto inserido"

# Alterar produto PUT
@rotas.put("/api/produtos/<int:id_produto>")
def alterar_produto(id_produto):
    return "Consultar produto"

# Excluir produto DELETE
@rotas.delete("/api/produtos/<int:id_produto>")
def excluir_produto(id_produto):
    return "Excluir produto"

# Altera o status do produto PATCH
@rotas.patch("/api/produtos/<int:id_produto>/inativar")
def inativar_produto(id_produto):
    return "INATIVO ou INATIVAR"

# Altera o status do produto PATCH
@rotas.patch("/api/produtos/<int:id_produto>/reativar")
def reativar_produto(id_produto):
    return "ATIVO ou REATIVAR"

# Consulta produto para auditoria GET
@rotas.get("/api/produtos/<int:id_produto>/auditoria")
def listar_auditoria(id_produto):
    return "Auditoria de produto"


# PRODUTOS! UPLOADS
@rotas.post("/api/uploads/produtos")
def enviar_foto_produto():
    return "Produto inserido"