"""CRUD de Cliente (subclasse de Pessoa - herança 1:1).

Um cliente existe em DUAS tabelas: Pessoa (dados comuns) e Cliente (dados
próprios, com id_cliente = id_pessoa). Por isso inserir e atualizar gravam
nas duas dentro de uma transação, e a leitura usa JOIN.
"""
from db import consultar, executar, transacao
from pessoa_base import (atualizar_pessoa, inserir_pessoa, pedir_alteracoes_pessoa,
                         pedir_dados_pessoa)
from utils import confirmar, ler_int, ler_texto, mostrar_tabela, rodar_menu

SQL_BASE = """
    SELECT c.id_cliente, p.nome, p.email, p.telefone,
           c.endereco_entrega, c.pontos_fidelidade
    FROM Cliente c
    JOIN Pessoa p ON p.id_pessoa = c.id_cliente
"""


def listar_todos():
    mostrar_tabela(consultar(SQL_BASE + " ORDER BY c.id_cliente"))


def buscar_por_id():
    id_ = ler_int("ID do cliente: ", minimo=1)
    mostrar_tabela(consultar(SQL_BASE + " WHERE c.id_cliente = %s", (id_,)))


def buscar_por_nome():
    termo = ler_texto("Nome (ou parte do nome): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE p.nome LIKE %s ORDER BY p.nome", (f"%{termo}%",)))


def buscar_por_email():
    termo = ler_texto("E-mail (ou parte): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE p.email LIKE %s ORDER BY p.email", (f"%{termo}%",)))


def inserir():
    id_existente = ler_int(
        "ID de uma Pessoa já cadastrada (Enter = cadastrar nova pessoa): ",
        obrigatorio=False, minimo=1)

    # Caso 1: a pessoa já existe (ex.: é funcionária) e ganha o papel de cliente.
    if id_existente is not None:
        pessoa = consultar("SELECT nome FROM Pessoa WHERE id_pessoa = %s", (id_existente,))
        if not pessoa:
            print("Pessoa não encontrada.")
            return
        if consultar("SELECT 1 AS x FROM Cliente WHERE id_cliente = %s", (id_existente,)):
            print("Essa pessoa já é cliente.")
            return
        print(f"Pessoa: {pessoa[0]['nome']}")
        endereco = ler_texto("Endereço de entrega: ", max_len=200)
        executar("INSERT INTO Cliente (id_cliente, endereco_entrega) VALUES (%s, %s)",
                 (id_existente, endereco))
        print(f"Papel de cliente adicionado à pessoa {id_existente}.")
        return

    # Caso 2: pessoa nova -> Pessoa + Cliente na MESMA transação.
    nome, email, telefone, senha_hash = pedir_dados_pessoa()
    endereco = ler_texto("Endereço de entrega: ", max_len=200)
    with transacao() as cur:
        novo_id = inserir_pessoa(cur, nome, email, telefone, senha_hash)
        cur.execute("INSERT INTO Cliente (id_cliente, endereco_entrega) VALUES (%s, %s)",
                    (novo_id, endereco))
    print(f"Cliente cadastrado com ID {novo_id}.")


def atualizar():
    """Update COM filtro: um cliente, escolhido por ID (altera Pessoa e Cliente)."""
    id_ = ler_int("ID do cliente a atualizar: ", minimo=1)
    achados = consultar(SQL_BASE + " WHERE c.id_cliente = %s", (id_,))
    if not achados:
        print("Cliente não encontrado.")
        return
    atual = achados[0]
    mostrar_tabela(achados)

    nome, email, telefone = pedir_alteracoes_pessoa(atual)
    endereco = ler_texto("Endereço de entrega (Enter mantém): ",
                         obrigatorio=False, max_len=200) or atual["endereco_entrega"]
    pontos = ler_int("Pontos de fidelidade (Enter mantém): ", obrigatorio=False, minimo=0)
    if pontos is None:
        pontos = atual["pontos_fidelidade"]

    with transacao() as cur:
        atualizar_pessoa(cur, id_, nome, email, telefone)
        cur.execute(
            "UPDATE Cliente SET endereco_entrega = %s, pontos_fidelidade = %s "
            "WHERE id_cliente = %s", (endereco, pontos, id_))
    print("Cliente atualizado.")


def excluir():
    """Delete: exige ID, mostra o registro, bloqueia se houver pedidos e confirma."""
    id_ = ler_int("ID do cliente a excluir: ", minimo=1)
    linhas = consultar(SQL_BASE + " WHERE c.id_cliente = %s", (id_,))
    if not linhas:
        print("Cliente não encontrado.")
        return
    mostrar_tabela(linhas)

    pedidos = consultar("SELECT COUNT(*) AS n FROM Pedido WHERE id_cliente = %s", (id_,))[0]["n"]
    if pedidos:
        print(f"Não é possível excluir: o cliente tem {pedidos} pedido(s) "
              "(o histórico de vendas é preservado).")
        return
    tambem_funcionario = bool(consultar(
        "SELECT 1 AS x FROM Funcionario WHERE id_funcionario = %s", (id_,)))
    if tambem_funcionario:
        print("Esta pessoa também é funcionária: só o papel de cliente será removido.")

    if not confirmar("Confirma a exclusão?"):
        print("Operação cancelada.")
        return

    if tambem_funcionario:
        qtd, _ = executar("DELETE FROM Cliente WHERE id_cliente = %s", (id_,))
    else:
        # Apaga a Pessoa; o ON DELETE CASCADE remove a linha de Cliente.
        qtd, _ = executar("DELETE FROM Pessoa WHERE id_pessoa = %s", (id_,))
    print(f"{qtd} registro(s) excluído(s).")


def menu():
    rodar_menu("CLIENTES", {
        "1": ("Listar todos", listar_todos),
        "2": ("Buscar por ID", buscar_por_id),
        "3": ("Buscar por nome", buscar_por_nome),
        "4": ("Buscar por e-mail", buscar_por_email),
        "5": ("Inserir", inserir),
        "6": ("Atualizar (por ID)", atualizar),
        "7": ("Excluir (por ID)", excluir),
    })
