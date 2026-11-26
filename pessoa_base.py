from utils import ler_texto


def pedir_dados_pessoa():
    """
    Coleta os dados de uma nova pessoa.
    Retorna:
    (nome, email, telefone, senha_hash)
    """

    nome = ler_texto(
        "Nome: ",
        max_len=100
    )

    email = ler_texto(
        "E-mail: ",
        max_len=100
    )

    telefone = ler_texto(
        "Telefone (Enter = vazio): ",
        obrigatorio=False,
        max_len=20
    )

    senha_hash = ler_texto(
        "Senha: ",
        max_len=255
    )

    return nome, email, telefone, senha_hash


def pedir_alteracoes_pessoa(atual):
    """
    Lê alterações para uma pessoa existente.
    """

    nome = (
        ler_texto(
            "Nome (Enter mantém): ",
            obrigatorio=False,
            max_len=100
        )
        or atual["nome"]
    )

    email = (
        ler_texto(
            "E-mail (Enter mantém): ",
            obrigatorio=False,
            max_len=100
        )
        or atual["email"]
    )

    telefone = ler_texto(
        "Telefone (Enter mantém): ",
        obrigatorio=False,
        max_len=20
    )

    if telefone is None:
        telefone = atual["telefone"]

    return nome, email, telefone


def inserir_pessoa(
    cur,
    nome,
    email,
    telefone,
    senha_hash
):
    """
    Insere uma pessoa usando cursor de transação.
    Retorna o ID gerado.
    """

    cur.execute(
        """
        INSERT INTO Pessoa
        (
            nome,
            email,
            telefone,
            senha_hash
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            nome,
            email,
            telefone,
            senha_hash
        )
    )

    return cur.lastrowid


def atualizar_pessoa(
    cur,
    id_pessoa,
    nome,
    email,
    telefone
):
    """
    Atualiza os dados básicos de uma pessoa.
    """

    cur.execute(
        """
        UPDATE Pessoa
        SET
            nome = %s,
            email = %s,
            telefone = %s
        WHERE id_pessoa = %s
        """,
        (
            nome,
            email,
            telefone,
            id_pessoa
        )
    )