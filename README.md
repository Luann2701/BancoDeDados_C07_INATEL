# BancoDeDados_C07_INATEL

## Integrantes do Grupo

- Luann Aparecido De Almeida Rangel
- Esthéfano Venícius Rosa

## Tema Escolhido

**Sistema de Gestão de E-commerce / Loja (LojaVirtual)**

Este projeto modela o banco de dados de uma plataforma de e-commerce, voltada para o gerenciamento de clientes, funcionários, catálogo de produtos organizados por categorias hierárquicas, pedidos e itens comprados.

### Explicação Simples

Imagine uma loja virtual: pessoas se cadastram no sistema (podendo ser **clientes**, que compram produtos, ou **funcionários**, que trabalham na loja). Os **produtos** são organizados em **categorias**, que podem ter subcategorias (por exemplo, "Eletrônicos" contém "Smartphones"). Quando um cliente compra algo, é gerado um **pedido**, que pode conter vários produtos diferentes — essa relação entre pedidos e produtos é controlada por uma tabela chamada **Item_Pedido**, que guarda a quantidade e o preço de cada produto no momento da compra.

### Estrutura do Banco de Dados

O modelo é composto por 6 entidades principais, organizadas em 3 camadas:

| Camada | Entidades |
| Usuários / Atores | `Pessoa`, `Cliente`, `Funcionario` |
| Catálogo | `Categoria`, `Produto` |
| Transações / Vendas | `Pedido`, `Item_Pedido` (tabela intermediária) |

**Principais relacionamentos:**

- **Herança (1:1):** `Pessoa` é a superclasse de `Cliente` e `Funcionario`.
- **Recursivo (1:N):** `Categoria` pode ter subcategorias, apontando para si mesma através de `id_categoria_pai`.
- **1:N:** Uma `Categoria` possui vários `Produto`s; um `Cliente` pode realizar vários `Pedido`s.
- **N:M:** Um `Pedido` pode conter vários `Produto`s, e um `Produto` pode estar em vários `Pedido`s, resolvido pela tabela intermediária `Item_Pedido`.

## Conteúdo do Repositório

- **`lojavirtual_ddl.sql`** — Script SQL com os comandos DDL (`CREATE TABLE`) para criação de todas as tabelas do banco, incluindo chaves primárias, chaves estrangeiras e restrições de integridade.
- **`lojavirtual.mwb`** — Arquivo de modelagem do MySQL Workbench, contendo o diagrama Entidade-Relacionamento (EER) do banco de dados.
