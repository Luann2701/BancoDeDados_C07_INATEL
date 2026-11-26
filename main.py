"""Ponto de entrada: conecta ao banco e abre o menu principal."""
from mysql.connector import Error

import consultas_join
import crud_categoria
import crud_clientes
import crud_funcionarios
import crud_item_pedido
import crud_pessoa
import crud_produto
import crud_pedido
from db import conectar, desconectar, mensagem_erro
from utils import rodar_menu


def main():
    try:
        conectar()
    except Error as err:
        print(f"Falha ao conectar: {mensagem_erro(err)}")
        return

    try:
        rodar_menu("LOJA VIRTUAL", {
            "1": ("Pessoas", crud_pessoa.menu),
            "2": ("Clientes", crud_clientes.menu),
            "3": ("Funcionários", crud_funcionarios.menu),
            "4": ("Categorias", crud_categoria.menu),
            "5": ("Produtos", crud_produto.menu),
            "6": ("Pedidos", crud_pedido.menu),
            "7": ("Itens de pedido", crud_item_pedido.menu),
            "8": ("Consultas com JOIN", consultas_join.menu),
        }, rotulo_saida="Sair")
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado.")
    finally:
        desconectar()


if __name__ == "__main__":
    main()