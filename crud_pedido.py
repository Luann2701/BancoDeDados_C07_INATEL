from db import consultar, executar
from utils import (
    confirmar,
    ler_int,
    mostrar_tabela,
    rodar_menu
)

SQL_BASE = """
    SELECT
        p.id_pedido,
        pe.nome AS cliente,
        p.data_pedido,
        p.valor_total,
        p.status_pedido
    FROM Pedido p
    JOIN Cliente c
        ON c.id_cliente = p.id_cliente
    JOIN Pessoa pe
        ON pe.id_pessoa = c.id_cliente
"""


def listar_todos():
    """Busca geral."""
    mostrar_tabela(
        consultar(
            SQL_BASE +
            " ORDER BY p.id_pedido"
        )
    )


def buscar_por_id():
    """Busca por filtro (ID)."""
    id_ = ler_int(
        "ID do pedido: ",
        minimo=1
    )

    mostrar_tabela(
        consultar(
            SQL_BASE +
            " WHERE p.id_pedido = %s",
            (id_,)
        )
    )


def buscar_por_cliente():
    """Busca por nome do cliente."""
    nome = input("Nome (ou parte do nome): ").strip()

    mostrar_tabela(
        consultar(
            SQL_BASE +
            " WHERE pe.nome LIKE %s "
            " ORDER BY pe.nome",
            (f"%{nome}%",)
        )
    )


def buscar_por_status():
    """Busca por status."""
    print("\nStatus disponíveis:")
    print("1 - Pendente")
    print("2 - Enviado")
    print("3 - Entregue")
    print("4 - Cancelado")

    opcao = input("Escolha: ").strip()

    mapa = {
        "1": "Pendente",
        "2": "Enviado",
        "3": "Entregue",
        "4": "Cancelado"
    }

    if opcao not in mapa:
        print("Status inválido.")
        return

    mostrar_tabela(
        consultar(
            SQL_BASE +
            " WHERE p.status_pedido = %s "
            " ORDER BY p.id_pedido",
            (mapa[opcao],)
        )
    )


def inserir():
    """Inserir novo pedido."""
    clientes = consultar("""
        SELECT
            c.id_cliente,
            p.nome
        FROM Cliente c
        JOIN Pessoa p
            ON p.id_pessoa = c.id_cliente
        ORDER BY p.nome
    """)

    print("\nClientes cadastrados:")
    mostrar_tabela(clientes)

    id_cliente = ler_int(
        "ID do cliente: ",
        minimo=1
    )

    existe = consultar(
        """
        SELECT id_cliente
        FROM Cliente
        WHERE id_cliente = %s
        """,
        (id_cliente,)
    )

    if not existe:
        print("Cliente não encontrado.")
        return

    _, novo_id = executar(
        """
        INSERT INTO Pedido (id_cliente)
        VALUES (%s)
        """,
        (id_cliente,)
    )

    print(f"Pedido criado com ID {novo_id}.")


def atualizar():
    """Atualiza o status de um pedido."""
    id_ = ler_int(
        "ID do pedido: ",
        minimo=1
    )

    pedido = consultar(
        """
        SELECT *
        FROM Pedido
        WHERE id_pedido = %s
        """,
        (id_,)
    )

    if not pedido:
        print("Pedido não encontrado.")
        return

    mostrar_tabela(
        consultar(
            SQL_BASE +
            " WHERE p.id_pedido = %s",
            (id_,)
        )
    )

    print("\nNovo status:")
    print("1 - Pendente")
    print("2 - Enviado")
    print("3 - Entregue")
    print("4 - Cancelado")

    opcao = input("Escolha: ").strip()

    mapa = {
        "1": "Pendente",
        "2": "Enviado",
        "3": "Entregue",
        "4": "Cancelado"
    }

    if opcao not in mapa:
        print("Status inválido.")
        return

    executar(
        """
        UPDATE Pedido
        SET status_pedido = %s
        WHERE id_pedido = %s
        """,
        (
            mapa[opcao],
            id_
        )
    )

    print("Pedido atualizado.")


def excluir():
    """Delete com filtro obrigatório."""
    id_ = ler_int(
        "ID do pedido a excluir: ",
        minimo=1
    )

    linhas = consultar(
        SQL_BASE +
        " WHERE p.id_pedido = %s",
        (id_,)
    )

    if not linhas:
        print("Pedido não encontrado.")
        return

    mostrar_tabela(linhas)

    if not confirmar(
        "Confirma a exclusão?"
    ):
        print("Operação cancelada.")
        return

    qtd, _ = executar(
        """
        DELETE FROM Pedido
        WHERE id_pedido = %s
        """,
        (id_,)
    )

    print(f"{qtd} registro(s) excluído(s).")


def menu():
    rodar_menu("PEDIDOS", {
        "1": ("Listar todos", listar_todos),
        "2": ("Buscar por ID", buscar_por_id),
        "3": ("Buscar por cliente", buscar_por_cliente),
        "4": ("Buscar por status", buscar_por_status),
        "5": ("Inserir", inserir),
        "6": ("Atualizar status", atualizar),
        "7": ("Excluir (por ID)", excluir),
    })