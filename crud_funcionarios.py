"""CRUD de Funcionario (subclasse de Pessoa - herança 1:1).

Mesma estrutura de crud_cliente.py: Pessoa (dados comuns) + Funcionario
(cargo e salário), com id_funcionario = id_pessoa.
"""
from decimal import Decimal

from db import consultar, executar, transacao
from pessoa_base import (atualizar_pessoa, inserir_pessoa, pedir_alteracoes_pessoa,
                         pedir_dados_pessoa)
from utils import (confirmar, ler_decimal, ler_int, ler_texto, mostrar_tabela,
                   rodar_menu)

SQL_BASE = """
    SELECT f.id_funcionario, p.nome, p.email, p.telefone, f.cargo, f.salario
    FROM Funcionario f
    JOIN Pessoa p ON p.id_pessoa = f.id_funcionario
"""


def listar_todos():
    mostrar_tabela(consultar(SQL_BASE + " ORDER BY f.id_funcionario"))


def buscar_por_id():
    id_ = ler_int("ID do funcionário: ", minimo=1)
    mostrar_tabela(consultar(SQL_BASE + " WHERE f.id_funcionario = %s", (id_,)))


def buscar_por_nome():
    termo = ler_texto("Nome (ou parte do nome): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE p.nome LIKE %s ORDER BY p.nome", (f"%{termo}%",)))


def buscar_por_cargo():
    termo = ler_texto("Cargo (ou parte): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE f.cargo LIKE %s ORDER BY f.cargo, p.nome", (f"%{termo}%",)))


def buscar_por_faixa_salarial():
    minimo = ler_decimal("Salário mínimo (Enter = sem mínimo): ",
                         obrigatorio=False, minimo=Decimal("0"))
    maximo = ler_decimal("Salário máximo (Enter = sem máximo): ",
                         obrigatorio=False, minimo=Decimal("0"))
    if minimo is None and maximo is None:
        print("Informe pelo menos um dos limites.")
        return
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE (%s IS NULL OR f.salario >= %s) "
                   "AND (%s IS NULL OR f.salario <= %s) ORDER BY f.salario",
        (minimo, minimo, maximo, maximo)))


def _pedir_salario(msg, obrigatorio=True):
    return ler_decimal(msg, obrigatorio=obrigatorio,
                       minimo=Decimal("0"), minimo_exclusivo=True)


def inserir():
    id_existente = ler_int(
        "ID de uma Pessoa já cadastrada (Enter = cadastrar nova pessoa): ",
        obrigatorio=False, minimo=1)

    if id_existente is not None:
        pessoa = consultar("SELECT nome FROM Pessoa WHERE id_pessoa = %s", (id_existente,))
        if not pessoa:
            print("Pessoa não encontrada.")
            return
        if consultar("SELECT 1 AS x FROM Funcionario WHERE id_funcionario = %s",
                     (id_existente,)):
            print("Essa pessoa já é funcionária.")
            return
        print(f"Pessoa: {pessoa[0]['nome']}")
        cargo = ler_texto("Cargo: ", max_len=50)
        salario = _pedir_salario("Salário (ex.: 3500.00): ")
        executar("INSERT INTO Funcionario (id_funcionario, cargo, salario) VALUES (%s, %s, %s)",
                 (id_existente, cargo, salario))
        print(f"Papel de funcionário adicionado à pessoa {id_existente}.")
        return
    
    nome, email, telefone, senha_hash = pedir_dados_pessoa()
    cargo = ler_texto("Cargo: ", max_len=50)
    salario = _pedir_salario("Salário (ex.: 3500.00): ")
    with transacao() as cur:
        novo_id = inserir_pessoa(cur, nome, email, telefone, senha_hash)
        cur.execute(
            "INSERT INTO Funcionario (id_funcionario, cargo, salario) VALUES (%s, %s, %s)",
            (novo_id, cargo, salario))
    print(f"Funcionário cadastrado com ID {novo_id}.")


def atualizar():
    """Update COM filtro: um funcionário, escolhido por ID (altera Pessoa e Funcionario)."""
    id_ = ler_int("ID do funcionário a atualizar: ", minimo=1)
    achados = consultar(SQL_BASE + " WHERE f.id_funcionario = %s", (id_,))
    if not achados:
        print("Funcionário não encontrado.")
        return
    atual = achados[0]
    mostrar_tabela(achados)

    nome, email, telefone = pedir_alteracoes_pessoa(atual)
    cargo = ler_texto("Cargo (Enter mantém): ", obrigatorio=False, max_len=50) or atual["cargo"]
    salario = _pedir_salario("Salário (Enter mantém): ", obrigatorio=False)
    if salario is None:
        salario = atual["salario"]

    with transacao() as cur:
        atualizar_pessoa(cur, id_, nome, email, telefone)
        cur.execute(
            "UPDATE Funcionario SET cargo = %s, salario = %s WHERE id_funcionario = %s",
            (cargo, salario, id_))
    print("Funcionário atualizado.")


def excluir():
    """Delete: exige ID, mostra o registro e pede confirmação."""
    id_ = ler_int("ID do funcionário a excluir: ", minimo=1)
    linhas = consultar(SQL_BASE + " WHERE f.id_funcionario = %s", (id_,))
    if not linhas:
        print("Funcionário não encontrado.")
        return
    mostrar_tabela(linhas)
    tambem_cliente = bool(consultar(
        "SELECT 1 AS x FROM Cliente WHERE id_cliente = %s", (id_,)))
    if tambem_cliente:
        print("Esta pessoa também é cliente: só o papel de funcionário será removido.")

    if not confirmar("Confirma a exclusão?"):
        print("Operação cancelada.")
        return

    if tambem_cliente:
        qtd, _ = executar("DELETE FROM Funcionario WHERE id_funcionario = %s", (id_,))
    else:
        qtd, _ = executar("DELETE FROM Pessoa WHERE id_pessoa = %s", (id_,))
    print(f"{qtd} registro(s) excluído(s).")


def menu():
    rodar_menu("FUNCIONÁRIOS", {
        "1": ("Listar todos", listar_todos),
        "2": ("Buscar por ID", buscar_por_id),
        "3": ("Buscar por nome", buscar_por_nome),
        "4": ("Buscar por cargo", buscar_por_cargo),
        "5": ("Buscar por faixa salarial", buscar_por_faixa_salarial),
        "6": ("Inserir", inserir),
        "7": ("Atualizar (por ID)", atualizar),
        "8": ("Excluir (por ID)", excluir),
    })
