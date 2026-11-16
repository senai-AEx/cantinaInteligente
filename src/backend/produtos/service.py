from . import repository as produto_repository
from flask import jsonify

# Listar todos os produtos
def listar_produtos(termo, status):
    return produto_repository.listar_produtos(termo, status)

# Consultar um produto
def consultar_produto(id_produto):
    return produto_repository.consultar_produto(id_produto)
