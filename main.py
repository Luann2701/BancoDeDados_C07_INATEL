"""Ponto de entrada: conecta ao banco e abre o menu principal."""
from mysql.connector import Error

import crud_categoria
import crud_cliente
import crud_funcionario
import crud_produto
from db import conectar, desconectar, mensagem_erro
from utils import rodar_menu


def em_desenvolvimento():
    print("\n(Esta entidade ainda será implementada.)")


def main():
    try:
        conectar()
    except Error as err:
        print(f"Falha ao conectar: {mensagem_erro(err)}")
        return

    try:
        rodar_menu("LOJA VIRTUAL", {
            "1": ("Pessoas", em_desenvolvimento),
            "2": ("Clientes", crud_cliente.menu),
            "3": ("Funcionários", crud_funcionario.menu),
            "4": ("Categorias", crud_categoria.menu),
            "5": ("Produtos", crud_produto.menu),
            "6": ("Pedidos", em_desenvolvimento),
            "7": ("Itens de pedido", em_desenvolvimento),
            "8": ("Consultas com JOIN", em_desenvolvimento),
        }, rotulo_saida="Sair")
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado.")
    finally:
        desconectar()


if __name__ == "__main__":
    main()