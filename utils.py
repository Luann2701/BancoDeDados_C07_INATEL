"""Funções reutilizáveis: leitura validada de entrada, tabela e menus."""
from mysql.connector import Error

from db import mensagem_erro


def ler_texto(msg, obrigatorio=True, max_len=None):
    """Lê texto. Se opcional e vazio, devolve None."""
    while True:
        valor = input(msg).strip()
        if not valor:
            if obrigatorio:
                print("Campo obrigatório.")
                continue
            return None
        if max_len and len(valor) > max_len:
            print(f"Máximo de {max_len} caracteres.")
            continue
        return valor


def ler_int(msg, obrigatorio=True, minimo=None):
    """Lê um inteiro validado. Se opcional e vazio, devolve None."""
    while True:
        valor = input(msg).strip()
        if not valor:
            if obrigatorio:
                print("Campo obrigatório.")
                continue
            return None
        try:
            numero = int(valor)
        except ValueError:
            print("Digite um número inteiro.")
            continue
        if minimo is not None and numero < minimo:
            print(f"O valor mínimo é {minimo}.")
            continue
        return numero


def confirmar(msg):
    return input(f"{msg} (s/N): ").strip().lower() == "s"


def mostrar_tabela(linhas):
    """Imprime uma lista de dicionários como tabela de texto."""
    if not linhas:
        print("\n(nenhum registro encontrado)")
        return
    colunas = list(linhas[0].keys())
    textos = [["-" if l[c] is None else str(l[c]) for c in colunas] for l in linhas]
    larguras = [max(len(c), *(len(t[i]) for t in textos)) for i, c in enumerate(colunas)]

    print()
    print(" | ".join(c.ljust(w) for c, w in zip(colunas, larguras)))
    print("-+-".join("-" * w for w in larguras))
    for t in textos:
        print(" | ".join(v.ljust(w) for v, w in zip(t, larguras)))
    print(f"\n{len(linhas)} registro(s).")


def rodar_menu(titulo, opcoes, rotulo_saida="Voltar"):
    """Executa um menu em loop.

    opcoes: {"1": ("Texto da opção", funcao), ...}
    Erros do banco lançados pelas funções são tratados aqui, em um só lugar.
    """
    while True:
        print(f"\n=== {titulo} ===")
        for chave, (rotulo, _) in opcoes.items():
            print(f"{chave} - {rotulo}")
        print(f"0 - {rotulo_saida}")

        escolha = input("Opção: ").strip()
        if escolha == "0":
            return
        if escolha not in opcoes:
            print("Opção inválida.")
            continue
        try:
            opcoes[escolha][1]()
        except Error as err:
            print(f"\n[ERRO] {mensagem_erro(err)}")
