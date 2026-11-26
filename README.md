# BancoDeDados_C07_INATEL

## Integrantes do Grupo

- Luann Aparecido De Almeida Rangel
- Esthéfano Venícius Rosa
- Guilherme Ferreira Silva

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
- **`tabelaloja.mwb`** — Arquivo de modelagem do MySQL Workbench, contendo o diagrama Entidade-Relacionamento (EER) do banco de dados.

- **`DML.txt`** — Explicação dos comandos DML usados e o motivo de cada um.
- **Código Python** — Aplicação de terminal com menu interativo (CRUD de todas as entidades e consultas com JOIN), descrita abaixo.

## Aplicação Python (Entrega Final)

### Como rodar

1. Rodar o script `lojavirtual_ddl.sql` no MySQL (cria o banco `LojaVirtual`, as tabelas, os dados, as procedures, a function, os triggers e as views — a aplicação usa esses objetos).
2. Ativar a venv:

```
venv\Scripts\Activate
```

3. Instalar as dependências:

```
python -m pip install -r requirements.txt
```

4. Rodar o `main.py`:

```
python main.py
```

A senha do MySQL é pedida ao iniciar (ou pode ser definida na variável de ambiente `DB_PASSWORD`). Host, porta, usuário e banco também podem ser alterados pelas variáveis `DB_HOST`, `DB_PORT`, `DB_USER` e `DB_NAME` (padrão: `localhost`, `3306`, `root`, `LojaVirtual`).

### Menu principal

| Opção | Módulo | O que faz |
|---|---|---|
| 1 - Pessoas | `crud_pessoa.py` | CRUD do supertipo, com o papel de cada pessoa (cliente/funcionário) |
| 2 - Clientes | `crud_clientes.py` | CRUD do subtipo Cliente (grava em Pessoa + Cliente na mesma transação) |
| 3 - Funcionários | `crud_funcionarios.py` | CRUD do subtipo Funcionario |
| 4 - Categorias | `crud_categoria.py` | CRUD com categoria pai (autorrelacionamento) |
| 5 - Produtos | `crud_produto.py` | CRUD + reajuste de preços em massa |
| 6 - Pedidos | `crud_pedido.py` | CRUD de pedidos e alteração de status |
| 7 - Itens de pedido | `crud_item_pedido.py` | Adiciona/altera/remove produtos de um pedido (tabela N:M) |
| 8 - Consultas com JOIN | `consultas_join.py` | Consultas 1:1, 1:N e N:M |

### Atendimento aos requisitos

- **Manipulação de todas as entidades:** cada tabela tem seu menu com inserir, buscar, atualizar e excluir.
- **Busca geral e por filtro:** todo menu tem "Listar todos" e buscas por atributos (ID, nome, e-mail, cargo, faixa de preço/salário, status, papel etc.).
- **Joins (menu 8):**
  - **1:1** — `Pessoa` x `Cliente` / `Funcionario` (herança): cada pessoa e seu papel.
  - **1:N** — `Cliente` x `Pedido`: pedidos com o nome do cliente e resumo de compras por cliente.
  - **N:M** — `Pedido` x `Produto` via `Item_Pedido`: produtos de cada pedido e produtos mais vendidos.
  - Consulta integrada com os três tipos + autorrelacionamento de `Categoria`.
- **Update com e sem filtro:** atualizações por ID em todas as entidades; atualização em massa no reajuste de preços de Produtos (todos os produtos ou filtrado por categoria, com confirmação forte quando não há filtro).
- **Delete sempre com filtro:** toda exclusão exige o ID, mostra o registro antes, pede confirmação e verifica dependências (ex.: não exclui cliente com pedidos nem produto já vendido).

### Detalhes técnicos

- Todas as consultas usam parâmetros (`%s`), evitando injeção de SQL.
- Operações que mexem em mais de uma tabela usam transação (`db.transacao()`): ou tudo é gravado, ou nada.
- Adicionar item a um pedido chama a procedure `sp_adicionar_item_pedido`, que valida estoque e status do pedido. O `valor_total` do pedido é recalculado automaticamente pelos triggers de `Item_Pedido`.
- Itens só podem ser alterados/removidos em pedidos Pendentes; o estoque é ajustado/devolvido na mesma transação.
