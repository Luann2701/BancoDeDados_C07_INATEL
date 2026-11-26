"""Consultas com JOIN, uma para cada tipo de relacionamento (1:1, 1:N e N:M).

As consultas são as mesmas da seção 5 do lojavirtual_ddl.sql.
"""
from db import consultar
from utils import mostrar_tabela, rodar_menu


def join_1_1_pessoa_papel():
    """1:1 — Pessoa x Cliente / Funcionario (herança: PK do subtipo = PK de Pessoa)."""
    print("\n[1:1] Cada pessoa e seu papel (Pessoa x Cliente / Funcionario)")
    mostrar_tabela(consultar("""
        SELECT pe.id_pessoa, pe.nome,
               CASE WHEN c.id_cliente     IS NOT NULL THEN 'Cliente'
                    WHEN f.id_funcionario IS NOT NULL THEN 'Funcionário'
                    ELSE 'Sem papel' END AS papel,
               c.pontos_fidelidade,
               f.cargo
        FROM Pessoa pe
        LEFT JOIN Cliente     c ON c.id_cliente     = pe.id_pessoa
        LEFT JOIN Funcionario f ON f.id_funcionario = pe.id_pessoa
        ORDER BY pe.id_pessoa
    """))


def join_1_n_pedidos_cliente():
    """1:N — um Cliente faz vários Pedidos."""
    print("\n[1:N] Pedidos com o nome do cliente (Cliente -> Pedido)")
    mostrar_tabela(consultar("""
        SELECT p.id_pedido, pe.nome AS cliente, p.data_pedido,
               p.status_pedido, p.valor_total
        FROM Pedido p
        JOIN Cliente c ON c.id_cliente = p.id_cliente
        JOIN Pessoa pe ON pe.id_pessoa = c.id_cliente
        ORDER BY p.id_pedido
    """))


def join_1_n_resumo_cliente():
    """1:N com LEFT JOIN + agregação: inclui clientes sem pedidos."""
    print("\n[1:N] Resumo de compras por cliente (pedidos cancelados não contam)")
    mostrar_tabela(consultar("""
        SELECT pe.id_pessoa AS id_cliente, pe.nome,
               COUNT(p.id_pedido)              AS qtd_pedidos,
               COALESCE(SUM(p.valor_total), 0) AS total_gasto,
               MAX(p.data_pedido)              AS ultimo_pedido
        FROM Pessoa pe
        JOIN Cliente c     ON c.id_cliente = pe.id_pessoa
        LEFT JOIN Pedido p ON p.id_cliente = c.id_cliente
                          AND p.status_pedido <> 'Cancelado'
        GROUP BY pe.id_pessoa, pe.nome
        ORDER BY total_gasto DESC
    """))


def join_n_m_itens_pedido():
    """N:M — Pedido x Produto, resolvido pela tabela Item_Pedido."""
    print("\n[N:M] Produtos de cada pedido (Pedido <-> Item_Pedido <-> Produto)")
    mostrar_tabela(consultar("""
        SELECT p.id_pedido, p.status_pedido, pr.nome_produto, i.quantidade,
               i.preco_unitario_praticado, pr.preco AS preco_atual
        FROM Pedido p
        JOIN Item_Pedido i ON i.id_pedido  = p.id_pedido
        JOIN Produto pr    ON pr.id_produto = i.id_produto
        ORDER BY p.id_pedido, pr.nome_produto
    """))


def join_n_m_mais_vendidos():
    """N:M com agregação: produtos mais vendidos."""
    print("\n[N:M] Produtos mais vendidos (pedidos cancelados não contam)")
    mostrar_tabela(consultar("""
        SELECT pr.id_produto, pr.nome_produto, cat.nome_categoria AS categoria,
               SUM(i.quantidade)                              AS unidades_vendidas,
               SUM(i.quantidade * i.preco_unitario_praticado) AS receita,
               COUNT(DISTINCT p.id_cliente)                   AS clientes_distintos
        FROM Produto pr
        JOIN Categoria cat ON cat.id_categoria = pr.id_categoria
        JOIN Item_Pedido i ON i.id_produto     = pr.id_produto
        JOIN Pedido p      ON p.id_pedido      = i.id_pedido
        WHERE p.status_pedido <> 'Cancelado'
        GROUP BY pr.id_produto, pr.nome_produto, cat.nome_categoria
        ORDER BY receita DESC
    """))


def join_integrado():
    """1:1 + 1:N + N:M + autorrelacionamento de Categoria em uma só consulta."""
    print("\n[1:1 + 1:N + N:M] Consulta integrada: cliente, pedido, produto e categorias")
    mostrar_tabela(consultar("""
        SELECT pe.nome AS cliente, p.id_pedido, p.status_pedido,
               pr.nome_produto, cat.nome_categoria AS categoria,
               COALESCE(pai.nome_categoria, '(raiz)') AS categoria_pai,
               i.quantidade,
               i.quantidade * i.preco_unitario_praticado AS subtotal
        FROM Pedido p
        JOIN Cliente c          ON c.id_cliente     = p.id_cliente
        JOIN Pessoa pe          ON pe.id_pessoa     = c.id_cliente
        JOIN Item_Pedido i      ON i.id_pedido      = p.id_pedido
        JOIN Produto pr         ON pr.id_produto    = i.id_produto
        JOIN Categoria cat      ON cat.id_categoria = pr.id_categoria
        LEFT JOIN Categoria pai ON pai.id_categoria = cat.id_categoria_pai
        ORDER BY p.id_pedido, pr.nome_produto
    """))


def menu():
    rodar_menu("CONSULTAS COM JOIN", {
        "1": ("[1:1] Pessoas e seus papéis (Cliente/Funcionário)", join_1_1_pessoa_papel),
        "2": ("[1:N] Pedidos com o nome do cliente", join_1_n_pedidos_cliente),
        "3": ("[1:N] Resumo de compras por cliente", join_1_n_resumo_cliente),
        "4": ("[N:M] Produtos de cada pedido", join_n_m_itens_pedido),
        "5": ("[N:M] Produtos mais vendidos", join_n_m_mais_vendidos),
        "6": ("[Todos] Consulta integrada", join_integrado),
    })
