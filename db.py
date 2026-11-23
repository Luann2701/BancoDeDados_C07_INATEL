"""Conexão com o MySQL e funções auxiliares de acesso ao banco."""
import os
from getpass import getpass

import mysql.connector
from mysql.connector import Error

# Configuração lida de variáveis de ambiente (com valores padrão).
# A senha NUNCA fica no código: vem de DB_PASSWORD ou é digitada na hora.
CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "database": os.getenv("DB_NAME", "LojaVirtual"),
}

_conn = None


def conectar():
    """Abre a conexão única usada por toda a aplicação."""
    global _conn
    senha = os.getenv("DB_PASSWORD")
    if senha is None:
        senha = getpass(f"Senha do MySQL para '{CONFIG['user']}': ")
    _conn = mysql.connector.connect(password=senha, **CONFIG)


def desconectar():
    if _conn is not None and _conn.is_connected():
        _conn.close()


def consultar(sql, params=()):
    """Executa um SELECT e devolve uma lista de dicionários.

    Os valores do usuário vão SEMPRE em 'params' (%s), nunca concatenados
    no texto do SQL, para evitar injeção de SQL.
    """
    cur = _conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        linhas = cur.fetchall()
        _conn.commit()  # encerra a transação de leitura (evita dados "velhos")
        return linhas
    except Error:
        _conn.rollback()
        raise
    finally:
        cur.close()


def executar(sql, params=()):
    """Executa INSERT/UPDATE/DELETE com commit.

    Retorna (linhas_afetadas, ultimo_id_gerado). Em caso de erro faz
    rollback e repassa a exceção para quem chamou tratar.
    """
    cur = _conn.cursor()
    try:
        cur.execute(sql, params)
        _conn.commit()
        return cur.rowcount, cur.lastrowid
    except Error:
        _conn.rollback()
        raise
    finally:
        cur.close()


def mensagem_erro(err):
    """Traduz erros do MySQL (pelo número) para mensagens claras."""
    errno = getattr(err, "errno", None)
    mensagens = {
        1045: "Usuário ou senha incorretos.",
        1049: "O banco de dados informado não existe.",
        2003: "Não foi possível alcançar o servidor MySQL (ele está ligado?).",
        1048: "Um campo obrigatório ficou vazio.",
        1062: "Valor duplicado: já existe um registro com esse valor único.",
        # FK ao excluir/alterar o "pai": 1451 (root) ou 1217 (usuário comum,
        # mesma falha com mensagem sem detalhes). Tratar os dois.
        1451: "Não é possível excluir/alterar: existem registros que dependem deste.",
        1217: "Não é possível excluir/alterar: existem registros que dependem deste.",
        # FK ao inserir/alterar o "filho": 1452 (root) ou 1216 (usuário comum).
        1452: "Referência inválida: o registro relacionado não existe.",
        1216: "Referência inválida: o registro relacionado não existe.",
        3819: "O valor informado viola uma regra (CHECK) da tabela.",
        1644: getattr(err, "msg", str(err)),  # mensagens das procedures (SIGNAL)
    }
    return mensagens.get(errno, f"Erro do banco ({errno}): {err}")
