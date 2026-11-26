"""CRUD de Produto (relacionamento 1:N com Categoria)."""
from decimal import Decimal

from db import consultar, executar
from utils import (confirmar, confirmar_digitando, ler_decimal, ler_int, ler_texto,
                   mostrar_tabela, rodar_menu)

SQL_BASE = """
    SELECT p.id_produto, p.nome_produto, c.nome_categoria AS categoria,
           p.preco, p.estoque_atual
    FROM Produto p
    JOIN Categoria c ON c.id_categoria = p.id_categoria
    LEFT JOIN Categoria pai ON pai.id_categoria = c.id_categoria_pai
"""
FILTRO_CATEGORIA = (
    "(%s IS NULL OR id_categoria = %s OR id_categoria IN "
    "(SELECT id_categoria FROM Categoria WHERE id_categoria_pai = %s))"
)


def _listar_categorias():
    mostrar_tabela(consultar(
        "SELECT id_categoria, nome_categoria FROM Categoria ORDER BY nome_categoria"))


def _categoria_existe(id_categoria):
    return bool(consultar("SELECT 1 AS x FROM Categoria WHERE id_categoria = %s",
                          (id_categoria,)))


def listar_todos():
    mostrar_tabela(consultar(SQL_BASE + " ORDER BY p.id_produto"))


def buscar_por_id():
    id_ = ler_int("ID do produto: ", minimo=1)
    mostrar_tabela(consultar(SQL_BASE + " WHERE p.id_produto = %s", (id_,)))


def buscar_por_nome():
    termo = ler_texto("Nome (ou parte do nome): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE p.nome_produto LIKE %s ORDER BY p.nome_produto",
        (f"%{termo}%",)))


def buscar_por_categoria():
    """Casa com o nome da categoria OU da categoria pai (ex.: 'Eletr' traz Smartphones)."""
    termo = ler_texto("Nome da categoria (ou parte): ")
    like = f"%{termo}%"
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE c.nome_categoria LIKE %s OR pai.nome_categoria LIKE %s "
                   "ORDER BY c.nome_categoria, p.nome_produto",
        (like, like)))


def buscar_por_faixa_de_preco():
    minimo = ler_decimal("Preço mínimo (Enter = sem mínimo): ",
                         obrigatorio=False, minimo=Decimal("0"))
    maximo = ler_decimal("Preço máximo (Enter = sem máximo): ",
                         obrigatorio=False, minimo=Decimal("0"))
    if minimo is None and maximo is None:
        print("Informe pelo menos um dos limites.")
        return
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE (%s IS NULL OR p.preco >= %s) "
                   "AND (%s IS NULL OR p.preco <= %s) ORDER BY p.preco",
        (minimo, minimo, maximo, maximo)))


def buscar_estoque_baixo():
    limite = ler_int("Mostrar produtos com estoque até: ", minimo=0)
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE p.estoque_atual <= %s ORDER BY p.estoque_atual", (limite,)))


def inserir():
    nome = ler_texto("Nome do produto: ", max_len=100)
    _listar_categorias()
    id_cat = ler_int("ID da categoria: ", minimo=1)
    if not _categoria_existe(id_cat):
        print("Categoria não encontrada.")
        return
    preco = ler_decimal("Preço (ex.: 199.90): ", minimo=Decimal("0"), minimo_exclusivo=True)
    estoque = ler_int("Estoque inicial: ", minimo=0)

    _, novo_id = executar(
        "INSERT INTO Produto (id_categoria, nome_produto, preco, estoque_atual) "
        "VALUES (%s, %s, %s, %s)",
        (id_cat, nome, preco, estoque))
    print(f"Produto criado com ID {novo_id}.")


def atualizar():
    """Update COM filtro: um produto, escolhido por ID."""
    id_ = ler_int("ID do produto a atualizar: ", minimo=1)
    achados = consultar("SELECT * FROM Produto WHERE id_produto = %s", (id_,))
    if not achados:
        print("Produto não encontrado.")
        return
    atual = achados[0]
    mostrar_tabela(consultar(SQL_BASE + " WHERE p.id_produto = %s", (id_,)))

    nome = ler_texto("Novo nome (Enter mantém): ", obrigatorio=False,
                     max_len=100) or atual["nome_produto"]

    entrada_cat = ler_int("Novo ID de categoria (Enter mantém): ",
                          obrigatorio=False, minimo=1)
    if entrada_cat is not None and not _categoria_existe(entrada_cat):
        print("Categoria não encontrada.")
        return
    id_cat = atual["id_categoria"] if entrada_cat is None else entrada_cat

    preco = ler_decimal("Novo preço (Enter mantém): ", obrigatorio=False,
                        minimo=Decimal("0"), minimo_exclusivo=True)
    if preco is None:
        preco = atual["preco"]

    estoque = ler_int("Novo estoque (Enter mantém): ", obrigatorio=False, minimo=0)
    if estoque is None:
        estoque = atual["estoque_atual"]

    executar(
        "UPDATE Produto SET nome_produto = %s, id_categoria = %s, preco = %s, "
        "estoque_atual = %s WHERE id_produto = %s",
        (nome, id_cat, preco, estoque, id_))
    print("Produto atualizado.")


def reajustar_precos():
    """Update em MASSA: sem filtro (todos os produtos) ou filtrado por categoria.

    Os pedidos antigos não mudam: Item_Pedido guarda o preço da época em
    preco_unitario_praticado.
    """
    _listar_categorias()
    cat = ler_int("ID da categoria a reajustar, com suas subcategorias "
                  "(Enter = TODOS os produtos): ", obrigatorio=False, minimo=1)
    if cat is not None and not _categoria_existe(cat):
        print("Categoria não encontrada.")
        return

    pct = ler_decimal("Percentual (ex.: 5 = aumento de 5%, -10 = desconto de 10%): ",
                      minimo=Decimal("-99.99"), maximo=Decimal("1000"))
    params_filtro = (cat, cat, cat)

    afetados = consultar(
        "SELECT COUNT(*) AS n FROM Produto WHERE " + FILTRO_CATEGORIA, params_filtro)[0]["n"]
    if afetados == 0:
        print("Nenhum produto encontrado para esse filtro.")
        return

    # Evita que o arredondamento gere preço zero (violaria a regra preco > 0).
    zerados = consultar(
        "SELECT COUNT(*) AS n FROM Produto WHERE " + FILTRO_CATEGORIA +
        " AND ROUND(preco * (1 + %s / 100), 2) <= 0", params_filtro + (pct,))[0]["n"]
    if zerados:
        print(f"Operação recusada: {zerados} produto(s) ficariam com preço zero ou negativo.")
        return

    escopo = "TODOS os produtos" if cat is None else f"categoria {cat} e subcategorias"
    print(f"\nReajuste de {pct}%. Escopo: {escopo}. {afetados} produto(s) serão alterados.")
    if cat is None:
        confirmado = confirmar_digitando("CONFIRMAR")   # sem filtro: confirmação forte
    else:
        confirmado = confirmar("Confirma?")
    if not confirmado:
        print("Operação cancelada.")
        return

    qtd, _ = executar(
        "UPDATE Produto SET preco = ROUND(preco * (1 + %s / 100), 2) WHERE " + FILTRO_CATEGORIA,
        (pct,) + params_filtro)
    print(f"{qtd} produto(s) reajustado(s).")


def excluir():
    """Delete: exige ID, mostra o registro, bloqueia se já foi vendido e confirma."""
    id_ = ler_int("ID do produto a excluir: ", minimo=1)
    linhas = consultar(SQL_BASE + " WHERE p.id_produto = %s", (id_,))
    if not linhas:
        print("Produto não encontrado.")
        return
    mostrar_tabela(linhas)

    usos = consultar("SELECT COUNT(*) AS n FROM Item_Pedido WHERE id_produto = %s",
                     (id_,))[0]["n"]
    if usos:
        print(f"Não é possível excluir: o produto consta em {usos} item(ns) de pedido.")
        return

    if not confirmar("Confirma a exclusão?"):
        print("Operação cancelada.")
        return
    qtd, _ = executar("DELETE FROM Produto WHERE id_produto = %s", (id_,))
    print(f"{qtd} registro(s) excluído(s).")


def menu():
    rodar_menu("PRODUTOS", {
        "1": ("Listar todos", listar_todos),
        "2": ("Buscar por ID", buscar_por_id),
        "3": ("Buscar por nome", buscar_por_nome),
        "4": ("Buscar por categoria", buscar_por_categoria),
        "5": ("Buscar por faixa de preço", buscar_por_faixa_de_preco),
        "6": ("Buscar por estoque baixo", buscar_estoque_baixo),
        "7": ("Inserir", inserir),
        "8": ("Atualizar (por ID)", atualizar),
        "9": ("Reajustar preços (todos ou por categoria)", reajustar_precos),
        "10": ("Excluir (por ID)", excluir),
    })