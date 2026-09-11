-- =====================================================================
-- LOJA VIRTUAL
-- =====================================================================
CREATE DATABASE IF NOT EXISTS LojaVirtual;
USE LojaVirtual;
-- ---------------------------------------------------------------------
-- Tabela: Pessoa (Superclasse - Herança)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Pessoa` (
    `id_pessoa`   INT AUTO_INCREMENT PRIMARY KEY,
    `nome`        VARCHAR(100) NOT NULL,
    `email`       VARCHAR(100) NOT NULL UNIQUE,
    `senha_hash`  VARCHAR(255) NOT NULL,
    `telefone`    VARCHAR(20)
);

-- ---------------------------------------------------------------------
-- Tabela: Cliente (Subclasse de Pessoa - Relacionamento 1:1)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Cliente` (
    `id_cliente`         INT PRIMARY KEY,
    `endereco_entrega`   VARCHAR(200) NOT NULL,
    `pontos_fidelidade`  INT DEFAULT 0,
    CONSTRAINT `fkClientePessoa`
        FOREIGN KEY (`id_cliente`)
        REFERENCES `Pessoa`(`id_pessoa`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- Tabela: Funcionario (Subclasse de Pessoa - Relacionamento 1:1)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Funcionario` (
    `id_funcionario`  INT PRIMARY KEY,
    `cargo`           VARCHAR(50) NOT NULL,
    `salario`         DECIMAL(10,2) NOT NULL,
    CONSTRAINT `fkFuncionarioPessoa`
        FOREIGN KEY (`id_funcionario`)
        REFERENCES `Pessoa`(`id_pessoa`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- Tabela: Categoria (Relacionamento Recursivo 1:N - Autorrelacionamento)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Categoria` (
    `id_categoria`      INT AUTO_INCREMENT PRIMARY KEY,
    `nome_categoria`    VARCHAR(50) NOT NULL,
    `id_categoria_pai`  INT,
    CONSTRAINT `fkCategoriaCategoriaPai`
        FOREIGN KEY (`id_categoria_pai`)
        REFERENCES `Categoria`(`id_categoria`)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- Tabela: Produto (Relacionamento 1:N com Categoria)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Produto` (
    `id_produto`     INT AUTO_INCREMENT PRIMARY KEY,
    `id_categoria`   INT NOT NULL,
    `nome_produto`   VARCHAR(100) NOT NULL,
    `preco`          DECIMAL(10,2) NOT NULL CHECK (`preco` > 0),
    `estoque_atual`  INT NOT NULL DEFAULT 0 CHECK (`estoque_atual` >= 0),
    CONSTRAINT `fkProdutoCategoria`
        FOREIGN KEY (`id_categoria`)
        REFERENCES `Categoria`(`id_categoria`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- Tabela: Pedido (Relacionamento 1:N com Cliente)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Pedido` (
    `id_pedido`     INT AUTO_INCREMENT PRIMARY KEY,
    `id_cliente`    INT NOT NULL,
    `data_pedido`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `valor_total`   DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    `status_pedido` ENUM('Pendente', 'Enviado', 'Entregue', 'Cancelado') NOT NULL DEFAULT 'Pendente',
    CONSTRAINT `fkPedidoCliente`
        FOREIGN KEY (`id_cliente`)
        REFERENCES `Cliente`(`id_cliente`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- ---------------------------------------------------------------------
-- Tabela: Item_Pedido (Tabela Intermediária N:M entre Pedido e Produto)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Item_Pedido` (
    `id_item`                  INT AUTO_INCREMENT PRIMARY KEY,
    `id_pedido`                INT NOT NULL,
    `id_produto`                INT NOT NULL,
    `quantidade`               INT NOT NULL CHECK (`quantidade` > 0),
    `preco_unitario_praticado` DECIMAL(10,2) NOT NULL,
    CONSTRAINT `fkItemPedidoPedido`
        FOREIGN KEY (`id_pedido`)
        REFERENCES `Pedido`(`id_pedido`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fkItemPedidoProduto`
        FOREIGN KEY (`id_produto`)
        REFERENCES `Produto`(`id_produto`)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    -- Evita que o mesmo produto seja duplicado no mesmo pedido
    UNIQUE (`id_pedido`, `id_produto`)
);

-- SHOW TABLES;
-- SHOW GRANTS FOR CURRENT_USER;
