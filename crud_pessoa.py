"""CRUD de Pessoa (supertipo da herança Pessoa -> Cliente / Funcionario).

Pessoa guarda os dados comuns. Uma pessoa pode ser cliente, funcionária,
as duas coisas ou nenhuma. A coluna "papel" é calculada com LEFT JOIN nos
dois subtipos. Para cadastrar já com papel, use os menus de Clientes ou
Funcionários; aqui é possível cadastrar uma pessoa sem papel.
"""
from db import consultar, executar, transacao
from pessoa_base import (atualizar_pessoa, inserir_pessoa, pedir_alteracoes_pessoa,
                         pedir_dados_pessoa)
from utils import confirmar, ler_int, ler_texto, mostrar_tabela, rodar_menu

SQL_BASE = """
    SELECT p.id_pessoa, p.nome, p.email, p.telefone,
           CASE
               WHEN c.id_cliente IS NOT NULL AND f.id_funcionario IS NOT NULL
                    THEN 'Cliente e Funcionário'
               WHEN c.id_cliente IS NOT NULL THEN 'Cliente'
               WHEN f.id_funcionario IS NOT NULL THEN 'Funcionário'
               ELSE 'Sem papel'
           END AS papel
    FROM Pessoa p
    LEFT JOIN Cliente c     ON c.id_cliente     = p.id_pessoa
    LEFT JOIN Funcionario f ON f.id_funcionario = p.id_pessoa
"""


def listar_todas():
    """Busca geral: todos os registros."""
    mostrar_tabela(consultar(SQL_BASE + " ORDER BY p.id_pessoa"))


def buscar_por_id():
    id_ = ler_int("ID da pessoa: ", minimo=1)
    mostrar_tabela(consultar(SQL_BASE + " WHERE p.id_pessoa = %s", (id_,)))


def buscar_por_nome():
    termo = ler_texto("Nome (ou parte do nome): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE p.nome LIKE %s ORDER BY p.nome", (f"%{termo}%",)))


def buscar_por_email():
    termo = ler_texto("E-mail (ou parte): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE p.email LIKE %s ORDER BY p.email", (f"%{termo}%",)))


def buscar_por_papel():
    print("\n1 - Cliente\n2 - Funcionário\n3 - Cliente e Funcionário\n4 - Sem papel")
    filtros = {
        "1": "c.id_cliente IS NOT NULL",
        "2": "f.id_funcionario IS NOT NULL",
        "3": "c.id_cliente IS NOT NULL AND f.id_funcionario IS NOT NULL",
        "4": "c.id_cliente IS NULL AND f.id_funcionario IS NULL",
    }
    opcao = input("Escolha: ").strip()
    if opcao not in filtros:
        print("Opção inválida.")
        return
    # O texto do filtro vem do dicionário acima (fixo), nunca do usuário.
    mostrar_tabela(consultar(SQL_BASE + f" WHERE {filtros[opcao]} ORDER BY p.nome"))


def inserir():
    """Cadastra uma pessoa sem papel (depois ela pode virar cliente/funcionária)."""
    print("(Para cadastrar já como cliente ou funcionário, use os menus próprios.)")
    nome, email, telefone, senha_hash = pedir_dados_pessoa()
    with transacao() as cur:
        novo_id = inserir_pessoa(cur, nome, email, telefone, senha_hash)
    print(f"Pessoa cadastrada com ID {novo_id}.")


def atualizar():
    """Update COM filtro: uma pessoa, escolhida por ID."""
    id_ = ler_int("ID da pessoa a atualizar: ", minimo=1)
    achados = consultar(SQL_BASE + " WHERE p.id_pessoa = %s", (id_,))
    if not achados:
        print("Pessoa não encontrada.")
        return
    mostrar_tabela(achados)

    nome, email, telefone = pedir_alteracoes_pessoa(achados[0])
    with transacao() as cur:
        atualizar_pessoa(cur, id_, nome, email, telefone)
    print("Pessoa atualizada.")


def excluir():
    """Delete: exige ID, mostra o registro, avisa o efeito do CASCADE e confirma."""
    id_ = ler_int("ID da pessoa a excluir: ", minimo=1)
    linhas = consultar(SQL_BASE + " WHERE p.id_pessoa = %s", (id_,))
    if not linhas:
        print("Pessoa não encontrada.")
        return
    mostrar_tabela(linhas)

    # Pedido -> Cliente é ON DELETE RESTRICT: o histórico de vendas é preservado.
    pedidos = consultar("SELECT COUNT(*) AS n FROM Pedido WHERE id_cliente = %s",
                        (id_,))[0]["n"]
    if pedidos:
        print(f"Não é possível excluir: a pessoa tem {pedidos} pedido(s) como cliente.")
        return

    papel = linhas[0]["papel"]
    if papel != "Sem papel":
        print(f"ATENÇÃO: o cadastro de {papel} também será apagado (ON DELETE CASCADE).")

    if not confirmar("Confirma a exclusão?"):
        print("Operação cancelada.")
        return
    qtd, _ = executar("DELETE FROM Pessoa WHERE id_pessoa = %s", (id_,))
    print(f"{qtd} registro(s) excluído(s).")


def menu():
    rodar_menu("PESSOAS", {
        "1": ("Listar todas", listar_todas),
        "2": ("Buscar por ID", buscar_por_id),
        "3": ("Buscar por nome", buscar_por_nome),
        "4": ("Buscar por e-mail", buscar_por_email),
        "5": ("Buscar por papel", buscar_por_papel),
        "6": ("Inserir (pessoa sem papel)", inserir),
        "7": ("Atualizar (por ID)", atualizar),
        "8": ("Excluir (por ID)", excluir),
    })
