-- ============================================================================
--  PROJETO: LOJA VIRTUAL
-- ============================================================================
--  ATIVIDADES
--   1. Inserção de dados (mínimo 5 registros por tabela)
--   2. Comandos de manipulação de dados (DML) e motivo de uso
--   3. Herança
--   4. Dois usuários relacionados por uma ROLE
--   5. Buscas com JOIN (1:1, 1:N e N:M)
--   6. 6.1 Procedure | 6.2 View | 6.3 Trigger | 6.4 Function
--   7. Implementações extras
-- ============================================================================
-- ----------------------------------------------------------------------------
-- 0. Criação das tabelas
-- ----------------------------------------------------------------------------
-- 0.1 Criação e seleção do banco
CREATE DATABASE IF NOT EXISTS LojaVirtual;
USE LojaVirtual;

-- 0.2 Tabelas da herança (ATIVIDADE 3)
-- Pessoa é o supertipo: guarda os atributos comuns a qualquer pessoa.
CREATE TABLE IF NOT EXISTS `Pessoa` (
    `id_pessoa`   INT AUTO_INCREMENT PRIMARY KEY,
    `nome`        VARCHAR(100) NOT NULL,
    `email`       VARCHAR(100) NOT NULL UNIQUE,
    `senha_hash`  VARCHAR(255) NOT NULL,
    `telefone`    VARCHAR(20)
);

-- Cliente é um subtipo de Pessoa: a PK é também FK para Pessoa (relação 1:1).
CREATE TABLE IF NOT EXISTS `Cliente` (
    `id_cliente`         INT PRIMARY KEY,
    `endereco_entrega`   VARCHAR(200) NOT NULL,
    `pontos_fidelidade`  INT DEFAULT 0,
    CONSTRAINT `fkClientePessoa`
        FOREIGN KEY (`id_cliente`) REFERENCES `Pessoa`(`id_pessoa`)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- Funcionario é outro subtipo de Pessoa, com a mesma estratégia do Cliente.
CREATE TABLE IF NOT EXISTS `Funcionario` (
    `id_funcionario`  INT PRIMARY KEY,
    `cargo`           VARCHAR(50) NOT NULL,
    `salario`         DECIMAL(10,2) NOT NULL,
    CONSTRAINT `fkFuncionarioPessoa`
        FOREIGN KEY (`id_funcionario`) REFERENCES `Pessoa`(`id_pessoa`)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- 0.3 Tabelas do catálogo
-- Categoria possui autorrelacionamento (id_categoria_pai) para formar a hierarquia.
CREATE TABLE IF NOT EXISTS `Categoria` (
    `id_categoria`      INT AUTO_INCREMENT PRIMARY KEY,
    `nome_categoria`    VARCHAR(50) NOT NULL,
    `id_categoria_pai`  INT,
    CONSTRAINT `fkCategoriaCategoriaPai`
        FOREIGN KEY (`id_categoria_pai`) REFERENCES `Categoria`(`id_categoria`)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS `Produto` (
    `id_produto`     INT AUTO_INCREMENT PRIMARY KEY,
    `id_categoria`   INT NOT NULL,
    `nome_produto`   VARCHAR(100) NOT NULL,
    `preco`          DECIMAL(10,2) NOT NULL CHECK (`preco` > 0),
    `estoque_atual`  INT NOT NULL DEFAULT 0 CHECK (`estoque_atual` >= 0),
    CONSTRAINT `fkProdutoCategoria`
        FOREIGN KEY (`id_categoria`) REFERENCES `Categoria`(`id_categoria`)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 0.4 Tabelas de vendas
CREATE TABLE IF NOT EXISTS `Pedido` (
    `id_pedido`     INT AUTO_INCREMENT PRIMARY KEY,
    `id_cliente`    INT NOT NULL,
    `data_pedido`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `valor_total`   DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `status_pedido` ENUM('Pendente','Enviado','Entregue','Cancelado') NOT NULL DEFAULT 'Pendente',
    CONSTRAINT `fkPedidoCliente`
        FOREIGN KEY (`id_cliente`) REFERENCES `Cliente`(`id_cliente`)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Tabela associativa do relacionamento N:M entre Pedido e Produto.
-- preco_unitario_praticado guarda o preço no momento da venda (histórico).
CREATE TABLE IF NOT EXISTS `Item_Pedido` (
    `id_item`                  INT AUTO_INCREMENT PRIMARY KEY,
    `id_pedido`                INT NOT NULL,
    `id_produto`               INT NOT NULL,
    `quantidade`               INT NOT NULL CHECK (`quantidade` > 0),
    `preco_unitario_praticado` DECIMAL(10,2) NOT NULL,
    CONSTRAINT `fkItemPedidoPedido`
        FOREIGN KEY (`id_pedido`) REFERENCES `Pedido`(`id_pedido`)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fkItemPedidoProduto`
        FOREIGN KEY (`id_produto`) REFERENCES `Produto`(`id_produto`)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    UNIQUE (`id_pedido`, `id_produto`)
);


-- ============================================================================
-- 1. INSERÇÃO DE DADOS (mínimo 5 registros por tabela)
-- ============================================================================

-- 1.1 Pessoa (11 registros: 6 serão clientes e 5 serão funcionários)
INSERT INTO Pessoa (id_pessoa, nome, email, senha_hash, telefone) VALUES
(1,  'Ana Beatriz Souza',    'ana.souza@email.com',       SHA2('senha_ana', 256),    '(35) 99111-0001'),
(2,  'Bruno Carvalho Lima',  'bruno.lima@email.com',      SHA2('senha_bruno', 256),  '(35) 99111-0002'),
(3,  'Camila Ferreira',      'camila.ferreira@email.com', SHA2('senha_camila', 256), '(35) 99111-0003'),
(4,  'Diego Martins',        'diego.martins@email.com',   SHA2('senha_diego', 256),  '(35) 99111-0004'),
(5,  'Elisa Rodrigues',      'elisa.rodrigues@email.com', SHA2('senha_elisa', 256),  '(35) 99111-0005'),
(6,  'Fernando Alves',       'fernando.alves@email.com',  SHA2('senha_fernando', 256), NULL),
(7,  'Gabriela Nunes',       'gabriela.nunes@loja.com',   SHA2('senha_gabriela', 256), '(35) 99222-0007'),
(8,  'Henrique Pires',       'henrique.pires@loja.com',   SHA2('senha_henrique', 256), '(35) 99222-0008'),
(9,  'Isabela Castro',       'isabela.castro@loja.com',   SHA2('senha_isabela', 256),  '(35) 99222-0009'),
(10, 'João Pedro Ribeiro',   'joao.ribeiro@loja.com',     SHA2('senha_joao', 256),     '(35) 99222-0010'),
(11, 'Karina Dias',          'karina.dias@loja.com',      SHA2('senha_karina', 256),   '(35) 99222-0011');

-- 1.2 Cliente (6 registros: subtipo de Pessoa, ids 1 a 6)
INSERT INTO Cliente (id_cliente, endereco_entrega, pontos_fidelidade) VALUES
(1, 'Rua das Flores, 120 - Centro, Santa Rita do Sapucaí/MG',     0),
(2, 'Av. Inconfidentes, 455 - Centro, Pouso Alegre/MG',           0),
(3, 'Rua XV de Novembro, 78 - Vila Nova, Itajubá/MG',             0),
(4, 'Rua Sete de Setembro, 300 - Jardim, Santa Rita do Sapucaí/MG', 0),
(5, 'Av. Brasil, 1020 - Centro, São Paulo/SP',                    0),
(6, 'Rua das Acácias, 15 - Bela Vista, Belo Horizonte/MG',        0);

-- 1.3 Funcionario (5 registros: subtipo de Pessoa, ids 7 a 11)
INSERT INTO Funcionario (id_funcionario, cargo, salario) VALUES
(7,  'Gerente de Loja',      7500.00),
(8,  'Analista de Estoque',  3800.00),
(9,  'Atendente',            2400.00),
(10, 'Auxiliar de Logística', 2600.00),
(11, 'Analista Financeiro',  4500.00);

-- 1.4 Categoria (7 registros: 3 raízes + 4 subcategorias)
-- Raízes primeiro (id_categoria_pai NULL), depois filhas.
INSERT INTO Categoria (id_categoria, nome_categoria, id_categoria_pai) VALUES
(1, 'Eletrônicos',        NULL),
(2, 'Livros',             NULL),
(3, 'Casa e Cozinha',     NULL),
(4, 'Smartphones',        1),
(5, 'Notebooks',          1),
(6, 'Ficção',             2),
(7, 'Eletroportáteis',    3);

-- 1.5 Produto (8 registros)
INSERT INTO Produto (id_produto, id_categoria, nome_produto, preco, estoque_atual) VALUES
(1, 4, 'Smartphone Galaxy A15 128GB',  1499.90, 25),
(2, 4, 'Smartphone Moto G54 256GB',    1299.00, 30),
(3, 5, 'Notebook Dell Inspiron 15',    3899.00, 10),
(4, 5, 'Notebook Lenovo IdeaPad 3',    2999.00, 12),
(5, 6, 'Livro Dom Casmurro',             39.90, 100),
(6, 6, 'Livro 1984',                     49.90, 80),
(7, 7, 'Air Fryer 4L',                  349.90, 40),
(8, 7, 'Liquidificador 900W',           189.90, 35);

-- 1.6 Pedido (6 registros)
-- valor_total não é informado aqui (assume o DEFAULT 0.00); ele é calculado no item 2.1.
INSERT INTO Pedido (id_pedido, id_cliente, data_pedido, status_pedido) VALUES
(1, 1, '2026-09-05 10:15:00', 'Entregue'),
(2, 2, '2026-09-12 16:40:00', 'Entregue'),
(3, 3, '2026-10-01 09:05:00', 'Enviado'),
(4, 1, '2026-10-15 20:30:00', 'Pendente'),
(5, 4, '2026-10-18 11:50:00', 'Cancelado'),
(6, 5, '2026-10-22 14:00:00', 'Pendente');

-- 1.7 Item_Pedido (9 registros)
INSERT INTO Item_Pedido (id_pedido, id_produto, quantidade, preco_unitario_praticado) VALUES
(1, 1, 1, 1499.90),
(1, 5, 2,   39.90),
(2, 3, 1, 3899.00),
(3, 7, 1,  349.90),
(3, 8, 1,  189.90),
(4, 6, 1,   49.90),
(4, 5, 1,   39.90),
(5, 2, 2, 1299.00),
(6, 4, 1, 2999.00);

-- 1.8 Conferência: confirma o mínimo de 5 registros em cada tabela
SELECT 'Pessoa' AS tabela, COUNT(*) AS registros FROM Pessoa
UNION ALL SELECT 'Cliente',     COUNT(*) FROM Cliente
UNION ALL SELECT 'Funcionario', COUNT(*) FROM Funcionario
UNION ALL SELECT 'Categoria',   COUNT(*) FROM Categoria
UNION ALL SELECT 'Produto',     COUNT(*) FROM Produto
UNION ALL SELECT 'Pedido',      COUNT(*) FROM Pedido
UNION ALL SELECT 'Item_Pedido', COUNT(*) FROM Item_Pedido;


-- ============================================================================
-- 2. COMANDOS DML (INSERT, UPDATE, DELETE) E MOTIVO DE USO
-- ============================================================================
-- Os INSERTs do item 1 já são DML (carga inicial). Abaixo estão os demais
-- comandos, cada um com o motivo de ser utilizado.

-- 2.1 UPDATE com subconsulta correlacionada: calcular o valor_total dos pedidos
-- Motivo: os pedidos foram inseridos com valor_total = 0.00. O total é um dado
-- derivado de Item_Pedido (quantidade x preço praticado), então é consolidado
-- com um UPDATE. O "WHERE p.id_pedido > 0" atende ao modo seguro (safe update
-- mode) do MySQL Workbench, que exige um WHERE sobre coluna chave.
UPDATE Pedido p
SET p.valor_total = (
    SELECT SUM(i.quantidade * i.preco_unitario_praticado)
    FROM Item_Pedido i
    WHERE i.id_pedido = p.id_pedido
)
WHERE p.id_pedido > 0;

-- 2.2 TRANSAÇÃO (START TRANSACTION ... COMMIT) com INSERT + UPDATE: nova venda
-- Motivo: registrar uma venda envolve várias operações dependentes entre si.
-- Com a transação, ou todas são gravadas ou nenhuma (atomicidade).
-- Fluxo: (a) cria o Pedido; (b) guarda o id gerado em @novo_pedido; (c) insere
-- os itens com o preço atual do produto (subconsulta); (d) dá baixa no estoque;
-- (e) calcula o valor_total do pedido.
START TRANSACTION;

INSERT INTO Pedido (id_cliente, data_pedido, status_pedido)
VALUES (6, '2026-10-26 15:20:00', 'Pendente');
SET @novo_pedido = LAST_INSERT_ID();

INSERT INTO Item_Pedido (id_pedido, id_produto, quantidade, preco_unitario_praticado)
VALUES (@novo_pedido, 7, 2, (SELECT preco FROM Produto WHERE id_produto = 7)),
       (@novo_pedido, 6, 1, (SELECT preco FROM Produto WHERE id_produto = 6));

UPDATE Produto SET estoque_atual = estoque_atual - 2 WHERE id_produto = 7;
UPDATE Produto SET estoque_atual = estoque_atual - 1 WHERE id_produto = 6;

UPDATE Pedido
SET valor_total = (SELECT SUM(quantidade * preco_unitario_praticado)
                   FROM Item_Pedido WHERE id_pedido = @novo_pedido)
WHERE id_pedido = @novo_pedido;

COMMIT;

-- 2.3 UPDATE simples: atualizar o status dos pedidos
-- Motivo: refletir o andamento do pedido (Pendente -> Enviado -> Entregue).
UPDATE Pedido SET status_pedido = 'Enviado'  WHERE id_pedido = 4;
UPDATE Pedido SET status_pedido = 'Entregue' WHERE id_pedido = 3;

-- 2.4 UPDATE com JOIN: creditar pontos de fidelidade
-- Motivo: o benefício do cliente depende do valor do pedido, que está em outra
-- tabela. O JOIN permite atualizar Cliente usando dados de Pedido.
-- Regra aplicada: 1 ponto a cada R$ 10,00 (FLOOR descarta a parte fracionária).
-- Aplicado aos pedidos 1 e 2, que já foram entregues.
UPDATE Cliente c
JOIN Pedido p ON p.id_cliente = c.id_cliente
SET c.pontos_fidelidade = c.pontos_fidelidade + FLOOR(p.valor_total / 10)
WHERE p.id_pedido = 1;

UPDATE Cliente c
JOIN Pedido p ON p.id_cliente = c.id_cliente
SET c.pontos_fidelidade = c.pontos_fidelidade + FLOOR(p.valor_total / 10)
WHERE p.id_pedido = 2;

-- 2.5 UPDATE em massa: reajuste de 5% nos Smartphones (categoria 4)
-- Motivo: aplicar um reajuste a vários produtos de uma vez, em vez de um a um.
-- Os pedidos antigos não mudam, pois o preço da venda fica salvo em
-- Item_Pedido.preco_unitario_praticado.
UPDATE Produto SET preco = ROUND(preco * 1.05, 2) WHERE id_categoria = 4;

-- 2.6 UPDATE de correção cadastral (uma e várias colunas)
-- Motivo: manter os dados atualizados. O telefone pertence ao supertipo (Pessoa)
-- e cargo/salário pertencem ao subtipo (Funcionario).
UPDATE Pessoa      SET telefone = '(35) 99111-0006' WHERE id_pessoa = 6;
UPDATE Funcionario SET cargo = 'Supervisor de Atendimento', salario = 3200.00 WHERE id_funcionario = 9;

-- 2.7 DELETE condicional: remover pedido cancelado
-- Motivo: eliminar um registro que não tem mais utilidade. A condição
-- "status_pedido = 'Cancelado'" é uma trava de segurança para não apagar um
-- pedido válido por engano. Os itens são removidos junto, por causa do
-- ON DELETE CASCADE em Item_Pedido.
DELETE FROM Pedido WHERE id_pedido = 5 AND status_pedido = 'Cancelado';


-- ============================================================================
-- 3. HERANÇA (Pessoa -> Cliente / Funcionario)
-- ============================================================================

-- 3.1 Inserção em supertipo e subtipo na mesma transação
START TRANSACTION;
INSERT INTO Pessoa (nome, email, senha_hash, telefone)
VALUES ('Larissa Monteiro', 'larissa.monteiro@email.com', SHA2('senha_larissa', 256), '(35) 99111-0012');
INSERT INTO Cliente (id_cliente, endereco_entrega)
VALUES (LAST_INSERT_ID(), 'Rua Projetada, 50 - Centro, Santa Rita do Sapucaí/MG');
COMMIT;

-- 3.2 Exclusão em cascata: supertipo -> subtipo
INSERT INTO Pessoa (id_pessoa, nome, email, senha_hash)
VALUES (99, 'Funcionário Temporário', 'temp@loja.com', SHA2('temp', 256));
INSERT INTO Funcionario (id_funcionario, cargo, salario) VALUES (99, 'Estagiário', 1500.00);

DELETE FROM Pessoa WHERE id_pessoa = 99;


-- ============================================================================
-- 4. DOIS USUÁRIOS RELACIONADOS POR MEIO DE UMA ROLE (parte 1)
-- ============================================================================
-- 4.1 Criar a role
CREATE ROLE IF NOT EXISTS 'role_atendimento';

-- 4.2 Criar os dois usuários
CREATE USER IF NOT EXISTS 'atendente1'@'localhost' IDENTIFIED BY 'Atend1#LojaVirtual26';
CREATE USER IF NOT EXISTS 'atendente2'@'localhost' IDENTIFIED BY 'Atend2#LojaVirtual26';

-- 4.3 Relacionar os usuários à role e ativá-la por padrão no login
GRANT 'role_atendimento' TO 'atendente1'@'localhost', 'atendente2'@'localhost';

SET DEFAULT ROLE 'role_atendimento' TO 'atendente1'@'localhost', 'atendente2'@'localhost';

-- 4.4 Privilégios da role sobre tabelas (as tabelas já existem)
GRANT SELECT  ON LojaVirtual.Produto                     TO 'role_atendimento';
GRANT SELECT  ON LojaVirtual.Categoria                   TO 'role_atendimento';

-- Os privilégios sobre views, procedures e function estão nos itens 4.5 a 4.7,
-- logo após o item 6, porque esses objetos ainda não existem neste ponto.

-- ============================================================================
-- 5. BUSCAS COM JOIN (relacionamentos 1:1, 1:N e N:M)
-- ============================================================================
-- ----------------------------------------------------------------------------
-- 5.1 JOIN 1:1
-- ----------------------------------------------------------------------------
SELECT pe.id_pessoa, pe.nome,
       CASE WHEN c.id_cliente      IS NOT NULL THEN 'Cliente'
            WHEN f.id_funcionario  IS NOT NULL THEN 'Funcionário'
            ELSE 'Sem papel' END      AS papel,
       c.pontos_fidelidade,
       f.cargo
FROM Pessoa pe
LEFT JOIN Cliente     c ON c.id_cliente     = pe.id_pessoa
LEFT JOIN Funcionario f ON f.id_funcionario = pe.id_pessoa
ORDER BY pe.id_pessoa;

-- ----------------------------------------------------------------------------
-- 5.2 JOIN 1:N
-- ----------------------------------------------------------------------------
-- 5.2.1 INNER JOIN: lista cada pedido com o nome do cliente.
SELECT p.id_pedido, pe.nome AS cliente, p.data_pedido, p.status_pedido, p.valor_total
FROM Pedido p
JOIN Cliente c  ON c.id_cliente = p.id_cliente
JOIN Pessoa pe  ON pe.id_pessoa = c.id_cliente
ORDER BY p.id_pedido;

-- 5.2.2 LEFT JOIN + agregação: resumo de compras por cliente
SELECT pe.id_pessoa AS id_cliente, pe.nome,
       COUNT(p.id_pedido)              AS qtd_pedidos,
       COALESCE(SUM(p.valor_total), 0) AS total_gasto,
       MAX(p.data_pedido)              AS ultimo_pedido
FROM Pessoa pe
JOIN Cliente c      ON c.id_cliente = pe.id_pessoa
LEFT JOIN Pedido p  ON p.id_cliente = c.id_cliente
                   AND p.status_pedido <> 'Cancelado'
GROUP BY pe.id_pessoa, pe.nome
ORDER BY total_gasto DESC;

-- ----------------------------------------------------------------------------
-- 5.3 JOIN N:M
-- ----------------------------------------------------------------------------
-- 5.3.1 Itens de cada pedido, comparando o preço praticado com o preço atual
SELECT i.id_pedido, pr.nome_produto, i.quantidade,
       i.preco_unitario_praticado, pr.preco AS preco_atual
FROM Item_Pedido i
JOIN Produto pr ON pr.id_produto = i.id_produto
ORDER BY i.id_pedido, pr.nome_produto;

-- 5.3.2 Produtos mais vendidos (JOIN de 4 tabelas, GROUP BY e HAVING)
SELECT pr.id_produto, pr.nome_produto, cat.nome_categoria,
       SUM(i.quantidade)                          AS unidades_vendidas,
       SUM(i.quantidade * i.preco_unitario_praticado) AS receita,
       COUNT(DISTINCT p.id_cliente)               AS clientes_distintos
FROM Produto pr
JOIN Categoria cat ON cat.id_categoria = pr.id_categoria
JOIN Item_Pedido i ON i.id_produto     = pr.id_produto
JOIN Pedido p      ON p.id_pedido      = i.id_pedido
WHERE p.status_pedido <> 'Cancelado'
GROUP BY pr.id_produto, pr.nome_produto, cat.nome_categoria
HAVING SUM(i.quantidade * i.preco_unitario_praticado) > 100
ORDER BY receita DESC;

-- 5.3.3 Produtos que nunca foram vendidos (LEFT JOIN + IS NULL)
SELECT pr.id_produto, pr.nome_produto, pr.estoque_atual
FROM Produto pr
LEFT JOIN Item_Pedido i ON i.id_produto = pr.id_produto
WHERE i.id_item IS NULL;

-- ----------------------------------------------------------------------------
-- 5.4 Consulta integrada: 1:1 + 1:N + N:M + hierarquia de categorias
-- ----------------------------------------------------------------------------
SELECT pe.nome                               AS cliente,
       p.id_pedido,
       p.status_pedido,
       pr.nome_produto,
       cat.nome_categoria                    AS categoria,
       COALESCE(pai.nome_categoria, '(raiz)') AS categoria_pai,
       i.quantidade,
       i.preco_unitario_praticado,
       i.quantidade * i.preco_unitario_praticado AS subtotal
FROM Pedido p
JOIN Cliente c          ON c.id_cliente   = p.id_cliente           -- 1:N
JOIN Pessoa pe          ON pe.id_pessoa   = c.id_cliente           -- 1:1
JOIN Item_Pedido i      ON i.id_pedido    = p.id_pedido            -- N:M (lado Pedido)
JOIN Produto pr         ON pr.id_produto  = i.id_produto           -- N:M (lado Produto)
JOIN Categoria cat      ON cat.id_categoria = pr.id_categoria      -- 1:N
LEFT JOIN Categoria pai ON pai.id_categoria = cat.id_categoria_pai -- recursivo
ORDER BY p.id_pedido, pr.nome_produto;


-- ============================================================================
-- 6. PROCEDURE, VIEW, TRIGGER E FUNCTION
-- ============================================================================
-- ----------------------------------------------------------------------------
-- 6.1 PROCEDURES
-- ----------------------------------------------------------------------------
-- 6.1.1 sp_cadastrar_cliente
-- Cadastra o cliente em Pessoa (supertipo) e Cliente (subtipo) de forma
-- atômica. Se qualquer INSERT falhar, o handler faz ROLLBACK e repassa o erro
-- (RESIGNAL). Devolve o id criado no parâmetro OUT.
DROP PROCEDURE IF EXISTS sp_cadastrar_cliente;
DELIMITER $$
CREATE PROCEDURE sp_cadastrar_cliente(
    IN  p_nome        VARCHAR(100),
    IN  p_email       VARCHAR(100),
    IN  p_senha_hash  VARCHAR(255),
    IN  p_telefone    VARCHAR(20),
    IN  p_endereco    VARCHAR(200),
    OUT p_id_cliente  INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    INSERT INTO Pessoa (nome, email, senha_hash, telefone)
    VALUES (p_nome, p_email, p_senha_hash, p_telefone);

    SET p_id_cliente = LAST_INSERT_ID();

    INSERT INTO Cliente (id_cliente, endereco_entrega)
    VALUES (p_id_cliente, p_endereco);

    COMMIT;
END$$
DELIMITER ;

-- 6.1.2 sp_criar_pedido
-- Abre um pedido vazio para o cliente (status Pendente pelo DEFAULT) e devolve
-- o id gerado, para ser usado ao adicionar os itens.
DROP PROCEDURE IF EXISTS sp_criar_pedido;
DELIMITER $$
CREATE PROCEDURE sp_criar_pedido(
    IN  p_id_cliente INT,
    OUT p_id_pedido  INT
)
BEGIN
    INSERT INTO Pedido (id_cliente) VALUES (p_id_cliente);
    SET p_id_pedido = LAST_INSERT_ID();
END$$
DELIMITER ;

-- 6.1.3 sp_adicionar_item_pedido
-- Concentra as regras de negócio da venda:
--   - valida a quantidade (> 0), a existência e o status do pedido (só Pendente),
--     a existência do produto e o estoque disponível (SIGNAL SQLSTATE '45000');
--   - trava as linhas do pedido e do produto (FOR UPDATE) para evitar que duas
--     vendas simultâneas usem o mesmo estoque;
--   - grava o preço atual em preco_unitario_praticado;
--   - se o produto já estiver no pedido, soma a quantidade (ON DUPLICATE KEY);
--   - dá baixa no estoque;
--   - tudo em transação, com ROLLBACK em caso de erro.
DROP PROCEDURE IF EXISTS sp_adicionar_item_pedido;
DELIMITER $$
CREATE PROCEDURE sp_adicionar_item_pedido(
    IN p_id_pedido  INT,
    IN p_id_produto INT,
    IN p_quantidade INT
)
BEGIN
    DECLARE v_status  VARCHAR(20)   DEFAULT NULL;
    DECLARE v_preco   DECIMAL(10,2) DEFAULT NULL;
    DECLARE v_estoque INT           DEFAULT NULL;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_quantidade IS NULL OR p_quantidade <= 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Quantidade deve ser maior que zero.';
    END IF;

    START TRANSACTION;

    SELECT status_pedido INTO v_status
      FROM Pedido WHERE id_pedido = p_id_pedido FOR UPDATE;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Pedido inexistente.';
    ELSEIF v_status <> 'Pendente' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Só é possível adicionar itens a pedidos Pendentes.';
    END IF;

    SELECT preco, estoque_atual INTO v_preco, v_estoque
      FROM Produto WHERE id_produto = p_id_produto FOR UPDATE;

    IF v_preco IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Produto inexistente.';
    ELSEIF v_estoque < p_quantidade THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Estoque insuficiente.';
    END IF;

    -- Se o produto já está no pedido, soma a quantidade (UNIQUE id_pedido+id_produto)
    INSERT INTO Item_Pedido (id_pedido, id_produto, quantidade, preco_unitario_praticado)
    VALUES (p_id_pedido, p_id_produto, p_quantidade, v_preco)
    ON DUPLICATE KEY UPDATE quantidade = quantidade + p_quantidade;

    UPDATE Produto
       SET estoque_atual = estoque_atual - p_quantidade
     WHERE id_produto = p_id_produto;

    COMMIT;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------------
-- 6.2 VIEWS
-- ----------------------------------------------------------------------------
-- Guardar consultas com JOIN prontas, simplificando o uso, e
-- expor só as colunas necessárias (as views não mostram senha_hash). Também
-- servem para dar acesso controlado a quem não pode ler as tabelas base.

-- 6.2.1 vw_cliente_completo: junta supertipo e subtipo (herança) dos clientes
CREATE OR REPLACE VIEW vw_cliente_completo AS
SELECT pe.id_pessoa AS id_cliente, pe.nome, pe.email, pe.telefone,
       c.endereco_entrega, c.pontos_fidelidade
FROM Pessoa pe
JOIN Cliente c ON c.id_cliente = pe.id_pessoa;

-- 6.2.2 vw_funcionario_completo: o mesmo para os funcionários
CREATE OR REPLACE VIEW vw_funcionario_completo AS
SELECT pe.id_pessoa AS id_funcionario, pe.nome, pe.email, pe.telefone,
       f.cargo, f.salario
FROM Pessoa pe
JOIN Funcionario f ON f.id_funcionario = pe.id_pessoa;

-- 6.2.3 vw_resumo_pedidos: visão consolidada de cada pedido (cliente, endereço,
-- status, quantidade de linhas e de unidades, valor total). Usa LEFT JOIN para
-- listar também pedidos que ainda não têm itens.
CREATE OR REPLACE VIEW vw_resumo_pedidos AS
SELECT p.id_pedido,
       pe.nome                        AS cliente,
       pe.email,
       c.endereco_entrega,
       p.data_pedido,
       p.status_pedido,
       COUNT(i.id_item)               AS linhas_de_item,
       COALESCE(SUM(i.quantidade), 0) AS unidades,
       p.valor_total
FROM Pedido p
JOIN Cliente c            ON c.id_cliente = p.id_cliente
JOIN Pessoa pe            ON pe.id_pessoa = c.id_cliente
LEFT JOIN Item_Pedido i   ON i.id_pedido  = p.id_pedido
GROUP BY p.id_pedido, pe.nome, pe.email, c.endereco_entrega,
         p.data_pedido, p.status_pedido, p.valor_total;

-- ----------------------------------------------------------------------------
-- 6.3 TRIGGERS (tabela Item_Pedido)
-- ----------------------------------------------------------------------------
-- Pedido.valor_total é um dado derivado dos itens. Com triggers
-- ele é recalculado automaticamente a cada INSERT, UPDATE ou DELETE em
-- Item_Pedido, seja por procedure, seja por comando manual. Assim o total
-- nunca fica desatualizado e nenhuma aplicação precisa lembrar de recalculá-lo.
-- Os triggers usam fn_total_pedido, é executado, então ela pode ser criada logo depois.
DROP TRIGGER IF EXISTS trg_item_pedido_ai;
DROP TRIGGER IF EXISTS trg_item_pedido_au;
DROP TRIGGER IF EXISTS trg_item_pedido_ad;

DELIMITER $$
-- 6.3.1 AFTER INSERT: novo item -> recalcula o total do pedido
CREATE TRIGGER trg_item_pedido_ai
AFTER INSERT ON Item_Pedido
FOR EACH ROW
BEGIN
    UPDATE Pedido
       SET valor_total = fn_total_pedido(NEW.id_pedido)
     WHERE id_pedido = NEW.id_pedido;
END$$

-- 6.3.2 AFTER UPDATE: item alterado -> recalcula o total do pedido
CREATE TRIGGER trg_item_pedido_au
AFTER UPDATE ON Item_Pedido
FOR EACH ROW
BEGIN
    UPDATE Pedido
       SET valor_total = fn_total_pedido(NEW.id_pedido)
     WHERE id_pedido = NEW.id_pedido;

    -- Se o item foi movido para outro pedido, recalcula o pedido antigo também
    IF OLD.id_pedido <> NEW.id_pedido THEN
        UPDATE Pedido
           SET valor_total = fn_total_pedido(OLD.id_pedido)
         WHERE id_pedido = OLD.id_pedido;
    END IF;
END$$

-- 6.3.3 AFTER DELETE: item removido -> recalcula o total do pedido
CREATE TRIGGER trg_item_pedido_ad
AFTER DELETE ON Item_Pedido
FOR EACH ROW
BEGIN
    UPDATE Pedido
       SET valor_total = fn_total_pedido(OLD.id_pedido)
     WHERE id_pedido = OLD.id_pedido;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------------
-- 6.4 FUNCTION
-- ----------------------------------------------------------------------------
-- fn_total_pedido: devolve a soma dos itens de
-- um pedido, ou 0 se ele não tiver itens (COALESCE).
-- Por que criar: centraliza a regra de cálculo em um só lugar, usada pelos
-- triggers e também em consultas de conferência.
-- A função só lê dados, não altera nada.
DROP FUNCTION IF EXISTS fn_total_pedido;
DELIMITER $$
CREATE FUNCTION fn_total_pedido(p_id_pedido INT)
RETURNS DECIMAL(10,2)
READS SQL DATA
BEGIN
    DECLARE v_total DECIMAL(10,2);

    SELECT COALESCE(SUM(quantidade * preco_unitario_praticado), 0)
      INTO v_total
      FROM Item_Pedido
     WHERE id_pedido = p_id_pedido;

    RETURN v_total;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------------
-- 6.5 TESTES DOS OBJETOS DO ITEM 6
-- ----------------------------------------------------------------------------
-- 6.5.1 Procedures (6.1): cadastra um cliente, abre um pedido e adiciona itens.
CALL sp_cadastrar_cliente('Marcos Teixeira', 'marcos.teixeira@email.com',
     SHA2('senha_marcos', 256), '(35) 99111-0013',
     'Rua das Palmeiras, 10 - Centro, Santa Rita do Sapucaí/MG', @id_cli);
CALL sp_criar_pedido(@id_cli, @id_ped);
CALL sp_adicionar_item_pedido(@id_ped, 8, 2);
CALL sp_adicionar_item_pedido(@id_ped, 5, 3);

SELECT id_pedido, status_pedido, valor_total FROM Pedido WHERE id_pedido = @id_ped;

-- 6.5.2 Triggers (6.3): alterar e remover itens deve atualizar o total sozinho
UPDATE Item_Pedido SET quantidade = 4 WHERE id_pedido = @id_ped AND id_produto = 5;
SELECT id_pedido, valor_total FROM Pedido WHERE id_pedido = @id_ped;

-- AFTER DELETE. Esperado: 379.80 (só restam os 2 x 189.90)
DELETE FROM Item_Pedido WHERE id_pedido = @id_ped AND id_produto = 5;
SELECT id_pedido, valor_total FROM Pedido WHERE id_pedido = @id_ped;

-- 6.5.3 Function (6.4): lista pedidos cujo valor_total difere do calculado.
-- Nenhuma linha (todos os totais estão consistentes).
SELECT id_pedido, valor_total, fn_total_pedido(id_pedido) AS total_calculado
FROM Pedido
WHERE valor_total <> fn_total_pedido(id_pedido);

-- 6.5.4 Views (6.2)
SELECT * FROM vw_resumo_pedidos ORDER BY id_pedido;
SELECT * FROM vw_cliente_completo;
SELECT * FROM vw_funcionario_completo;

-- 6.5.5 Erros esperados das regras da procedure (descomente um por vez)
-- CALL sp_adicionar_item_pedido(@id_ped, 3, 999);  -- Estoque insuficiente.
-- CALL sp_adicionar_item_pedido(@id_ped, 999, 1);  -- Produto inexistente.
-- CALL sp_adicionar_item_pedido(1, 5, 1);          -- Só é possível adicionar itens a pedidos Pendentes.
-- CALL sp_adicionar_item_pedido(@id_ped, 5, 0);    -- Quantidade deve ser maior que zero.

-- ============================================================================
-- 4. DOIS USUÁRIOS RELACIONADOS POR MEIO DE UMA ROLE (parte 2 - continuação)
-- ============================================================================
-- 4.5 Privilégios da role sobre views, procedures e function
GRANT SELECT  ON LojaVirtual.vw_resumo_pedidos           TO 'role_atendimento';
GRANT SELECT  ON LojaVirtual.vw_cliente_completo         TO 'role_atendimento';
GRANT EXECUTE ON PROCEDURE LojaVirtual.sp_cadastrar_cliente     TO 'role_atendimento';
GRANT EXECUTE ON PROCEDURE LojaVirtual.sp_criar_pedido          TO 'role_atendimento';
GRANT EXECUTE ON PROCEDURE LojaVirtual.sp_adicionar_item_pedido TO 'role_atendimento';
GRANT EXECUTE ON FUNCTION  LojaVirtual.fn_total_pedido          TO 'role_atendimento';

-- 4.6 Verificação: privilégios da role e vínculo entre a role e os usuários
SHOW GRANTS FOR 'role_atendimento';
SHOW GRANTS FOR 'atendente1'@'localhost' USING 'role_atendimento';
SELECT FROM_USER AS role, TO_USER AS usuario FROM mysql.role_edges
WHERE FROM_USER = 'role_atendimento';

-- 4.7 Teste de permissão: abra uma conexão como atendente1 (ou atendente2)
--   SELECT CURRENT_ROLE();                         -- deve listar role_atendimento
--   SELECT * FROM vw_resumo_pedidos;               -- permitido
--   CALL sp_criar_pedido(1, @p);                   -- permitido
--   SELECT * FROM Pessoa;                          -- negado (erro 1142)
--   SELECT * FROM vw_funcionario_completo;         -- negado (erro 1142)
--   DELETE FROM Produto WHERE id_produto = 1;      -- negado (erro 1142)

-- ============================================================================
-- 7. IMPLEMENTAÇÕES EXTRAS (para detalhar na documentação)
-- ============================================================================
-- 7.1 Autorrelacionamento: subcategoria x categoria pai (self JOIN)
SELECT f.nome_categoria AS subcategoria, COALESCE(pai.nome_categoria, '(raiz)') AS categoria_pai
FROM Categoria f
LEFT JOIN Categoria pai ON pai.id_categoria = f.id_categoria_pai
ORDER BY categoria_pai, subcategoria;

-- 7.2 Auditoria: pedidos cujo valor_total difere da soma dos itens.
SELECT p.id_pedido, p.valor_total, SUM(i.quantidade * i.preco_unitario_praticado) AS soma_itens
FROM Pedido p
JOIN Item_Pedido i ON i.id_pedido = p.id_pedido
GROUP BY p.id_pedido, p.valor_total
HAVING p.valor_total <> soma_itens;
