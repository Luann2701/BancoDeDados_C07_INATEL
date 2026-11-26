"""CRUD de Item_Pedido (tabela associativa do relacionamento N:M Pedido x Produto).

Regras:
- Adicionar item usa a procedure sp_adicionar_item_pedido, que valida pedido,
  produto, estoque e status, grava o preço atual e dá baixa no estoque.
- Itens só podem ser alterados/removidos em pedidos Pendentes (mesma regra da
  procedure). Ao alterar ou remover, o estoque é ajustado na mesma transação.
- O valor_total do pedido é recalculado sozinho pelos triggers de Item_Pedido.
"""
from db import consultar, executar, transacao
from utils import confirmar, ler_int, ler_texto, mostrar_tabela, rodar_menu

SQL_BASE = """
    SELECT i.id_item, i.id_pedido, pe.nome AS cliente, p.status_pedido,
           pr.id_produto, pr.nome_produto, i.quantidade,
           i.preco_unitario_praticado,
           i.quantidade * i.preco_unitario_praticado AS subtotal
    FROM Item_Pedido i
    JOIN Pedido p   ON p.id_pedido   = i.id_pedido
    JOIN Pessoa pe  ON pe.id_pessoa  = p.id_cliente
    JOIN Produto pr ON pr.id_produto = i.id_produto
"""


def listar_todos():
    """Busca geral: todos os itens de todos os pedidos."""
    mostrar_tabela(consultar(SQL_BASE + " ORDER BY i.id_pedido, i.id_item"))


def buscar_por_id():
    id_ = ler_int("ID do item: ", minimo=1)
    mostrar_tabela(consultar(SQL_BASE + " WHERE i.id_item = %s", (id_,)))


def buscar_por_pedido():
    id_pedido = ler_int("ID do pedido: ", minimo=1)
    linhas = consultar(SQL_BASE + " WHERE i.id_pedido = %s ORDER BY i.id_item",
                       (id_pedido,))
    mostrar_tabela(linhas)
    if linhas:
        total = consultar("SELECT valor_total FROM Pedido WHERE id_pedido = %s",
                          (id_pedido,))[0]["valor_total"]
        print(f"Valor total do pedido: R$ {total}")


def buscar_por_produto():
    termo = ler_texto("Nome do produto (ou parte): ")
    mostrar_tabela(consultar(
        SQL_BASE + " WHERE pr.nome_produto LIKE %s ORDER BY pr.nome_produto, i.id_pedido",
        (f"%{termo}%",)))


def inserir():
    """Adiciona um produto a um pedido Pendente (via procedure)."""
    print("\nPedidos pendentes:")
    mostrar_tabela(consultar("""
        SELECT p.id_pedido, pe.nome AS cliente, p.data_pedido, p.valor_total
        FROM Pedido p
        JOIN Pessoa pe ON pe.id_pessoa = p.id_cliente
        WHERE p.status_pedido = 'Pendente'
        ORDER BY p.id_pedido
    """))
    id_pedido = ler_int("ID do pedido: ", minimo=1)

    print("\nProdutos com estoque:")
    mostrar_tabela(consultar("""
        SELECT id_produto, nome_produto, preco, estoque_atual
        FROM Produto WHERE estoque_atual > 0 ORDER BY nome_produto
    """))
    id_produto = ler_int("ID do produto: ", minimo=1)
    quantidade = ler_int("Quantidade: ", minimo=1)

    # A procedure valida tudo e lança erro (SIGNAL) com mensagem clara,
    # que é exibida pelo tratamento de erros do rodar_menu.
    executar("CALL sp_adicionar_item_pedido(%s, %s, %s)",
             (id_pedido, id_produto, quantidade))
    print("Item adicionado. Itens atuais do pedido:")
    mostrar_tabela(consultar(SQL_BASE + " WHERE i.id_pedido = %s ORDER BY i.id_item",
                             (id_pedido,)))


def _buscar_item(id_item):
    """Mostra o item e devolve seus dados, ou None se não existir/não for editável."""
    linhas = consultar(SQL_BASE + " WHERE i.id_item = %s", (id_item,))
    if not linhas:
        print("Item não encontrado.")
        return None
    mostrar_tabela(linhas)
    if linhas[0]["status_pedido"] != "Pendente":
        print("Só é possível alterar itens de pedidos Pendentes.")
        return None
    return linhas[0]


def atualizar():
    """Update COM filtro: altera a quantidade de um item (por ID) e ajusta o estoque."""
    id_ = ler_int("ID do item a atualizar: ", minimo=1)
    item = _buscar_item(id_)
    if item is None:
        return

    nova_qtd = ler_int(f"Nova quantidade (atual {item['quantidade']}): ", minimo=1)
    diferenca = nova_qtd - item["quantidade"]
    if diferenca == 0:
        print("Nada a alterar.")
        return

    with transacao() as cur:
        # Trava a linha do produto para o estoque não ser usado por outra venda.
        cur.execute("SELECT estoque_atual FROM Produto WHERE id_produto = %s FOR UPDATE",
                    (item["id_produto"],))
        estoque = cur.fetchone()[0]
        if diferenca > estoque:
            print(f"Estoque insuficiente: só há {estoque} unidade(s) disponíveis.")
            return  # sai do with sem erro -> commit sem alterações
        cur.execute("UPDATE Item_Pedido SET quantidade = %s WHERE id_item = %s",
                    (nova_qtd, id_))
        cur.execute("UPDATE Produto SET estoque_atual = estoque_atual - %s "
                    "WHERE id_produto = %s", (diferenca, item["id_produto"]))
    print("Item atualizado (estoque e valor total do pedido ajustados).")


def excluir():
    """Delete: exige ID do item, só em pedido Pendente, devolve o estoque."""
    id_ = ler_int("ID do item a excluir: ", minimo=1)
    item = _buscar_item(id_)
    if item is None:
        return
    if not confirmar("Confirma a exclusão?"):
        print("Operação cancelada.")
        return

    with transacao() as cur:
        cur.execute("DELETE FROM Item_Pedido WHERE id_item = %s", (id_,))
        cur.execute("UPDATE Produto SET estoque_atual = estoque_atual + %s "
                    "WHERE id_produto = %s", (item["quantidade"], item["id_produto"]))
    print("Item excluído e estoque devolvido.")


def menu():
    rodar_menu("ITENS DE PEDIDO", {
        "1": ("Listar todos", listar_todos),
        "2": ("Buscar por ID do item", buscar_por_id),
        "3": ("Buscar itens de um pedido", buscar_por_pedido),
        "4": ("Buscar por produto", buscar_por_produto),
        "5": ("Adicionar item a um pedido", inserir),
        "6": ("Atualizar quantidade (por ID)", atualizar),
        "7": ("Excluir item (por ID)", excluir),
    })
