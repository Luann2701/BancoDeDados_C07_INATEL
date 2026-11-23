"""CRUD de Categoria - modelo para as demais entidades."""
from db import consultar, executar
from utils import confirmar, ler_int, ler_texto, mostrar_tabela, rodar_menu

# SELECT base: traz também o nome da categoria pai (autorrelacionamento).
SQL_BASE = """
    SELECT c.id_categoria, c.nome_categoria, p.nome_categoria AS categoria_pai
    FROM Categoria c
    LEFT JOIN Categoria p ON p.id_categoria = c.id_categoria_pai
"""


def listar_todas():
    """Busca geral: todos os registros."""
    mostrar_tabela(consultar(SQL_BASE + " ORDER BY c.id_categoria"))


def buscar_por_id():
    """Busca por filtro (ID)."""
    id_ = ler_int("ID da categoria: ", minimo=1)
    mostrar_tabela(consultar(SQL_BASE + " WHERE c.id_categoria = %s", (id_,)))


def buscar_por_nome():
    """Busca por filtro (parte do nome)."""
    termo = ler_texto("Nome (ou parte do nome): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE c.nome_categoria LIKE %s ORDER BY c.nome_categoria",
        (f"%{termo}%",),
    ))


def inserir():
    nome = ler_texto("Nome da categoria: ", max_len=50)
    pai = ler_int("ID da categoria pai (Enter = categoria raiz): ",
                  obrigatorio=False, minimo=1)
    _, novo_id = executar(
        "INSERT INTO Categoria (nome_categoria, id_categoria_pai) VALUES (%s, %s)",
        (nome, pai),
    )
    print(f"Categoria criada com ID {novo_id}.")


def atualizar():
    """Update COM filtro: altera um único registro, escolhido por ID."""
    id_ = ler_int("ID da categoria a atualizar: ", minimo=1)
    achados = consultar("SELECT * FROM Categoria WHERE id_categoria = %s", (id_,))
    if not achados:
        print("Categoria não encontrada.")
        return
    atual = achados[0]
    print(f"Nome atual: {atual['nome_categoria']} | ID do pai atual: {atual['id_categoria_pai']}")

    novo_nome = ler_texto("Novo nome (Enter mantém): ", obrigatorio=False, max_len=50)
    entrada_pai = ler_int("Novo ID do pai (Enter mantém, 0 = tornar raiz): ",
                          obrigatorio=False, minimo=0)

    nome = novo_nome or atual["nome_categoria"]
    if entrada_pai is None:
        pai = atual["id_categoria_pai"]
    elif entrada_pai == 0:
        pai = None
    else:
        pai = entrada_pai
    if pai == id_:
        print("Uma categoria não pode ser pai de si mesma.")
        return

    executar(
        "UPDATE Categoria SET nome_categoria = %s, id_categoria_pai = %s "
        "WHERE id_categoria = %s",
        (nome, pai, id_),
    )
    print("Categoria atualizada.")


def excluir():
    """Delete: exige ID (filtro), mostra o registro e pede confirmação."""
    id_ = ler_int("ID da categoria a excluir: ", minimo=1)
    linhas = consultar(SQL_BASE + " WHERE c.id_categoria = %s", (id_,))
    if not linhas:
        print("Categoria não encontrada.")
        return
    mostrar_tabela(linhas)

    # A FK de autorrelacionamento é ON DELETE SET NULL: avisar o efeito.
    filhas = consultar(
        "SELECT COUNT(*) AS n FROM Categoria WHERE id_categoria_pai = %s", (id_,)
    )[0]["n"]
    if filhas:
        print(f"ATENÇÃO: {filhas} subcategoria(s) ficarão sem pai (viram raiz).")

    if not confirmar("Confirma a exclusão?"):
        print("Operação cancelada.")
        return
    qtd, _ = executar("DELETE FROM Categoria WHERE id_categoria = %s", (id_,))
    print(f"{qtd} registro(s) excluído(s).")


def menu():
    rodar_menu("CATEGORIAS", {
        "1": ("Listar todas", listar_todas),
        "2": ("Buscar por ID", buscar_por_id),
        "3": ("Buscar por nome", buscar_por_nome),
        "4": ("Inserir", inserir),
        "5": ("Atualizar (por ID)", atualizar),
        "6": ("Excluir (por ID)", excluir),
    })
