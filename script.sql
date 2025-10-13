-- script.sql — Banco MySQL + dados + 5 consultas
-- Ajuste apenas se quiser trocar nomes/posições.
CREATE DATABASE IF NOT EXISTS futebol_app
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE futebol_app;

DROP TABLE IF EXISTS TIME_USUARIO_JOGADOR;
DROP TABLE IF EXISTS TIME_USUARIO;
DROP TABLE IF EXISTS JOGADOR;
DROP TABLE IF EXISTS TIME_OFICIAL;
DROP TABLE IF EXISTS USUARIO;

CREATE TABLE USUARIO (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nome            VARCHAR(120)        NOT NULL,
  email           VARCHAR(160)        NOT NULL UNIQUE,
  senha           VARCHAR(255)        NOT NULL,
  sexo            ENUM('M','F','O')   NOT NULL,
  telefone        VARCHAR(20),
  data_nascimento DATE                NOT NULL,
  time_preferido  VARCHAR(80)
);

CREATE TABLE TIME_OFICIAL (
  id     INT AUTO_INCREMENT PRIMARY KEY,
  nome   VARCHAR(120) NOT NULL,
  sigla  VARCHAR(10)  NOT NULL UNIQUE
);

CREATE TABLE JOGADOR (
  id      INT AUTO_INCREMENT PRIMARY KEY,
  nome    VARCHAR(120) NOT NULL,
  posicao VARCHAR(40)  NOT NULL,
  time_id INT,
  CONSTRAINT fk_jog_time
    FOREIGN KEY (time_id) REFERENCES TIME_OFICIAL(id)
    ON UPDATE CASCADE ON DELETE SET NULL
);

CREATE TABLE TIME_USUARIO (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  nome       VARCHAR(120) NOT NULL,
  usuario_id INT          NOT NULL,
  CONSTRAINT fk_timeuser_user
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE TIME_USUARIO_JOGADOR (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  time_usuario_id INT NOT NULL,
  jogador_id      INT NOT NULL,
  CONSTRAINT fk_tuj_timeuser FOREIGN KEY (time_usuario_id) REFERENCES TIME_USUARIO(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_tuj_jog FOREIGN KEY (jogador_id) REFERENCES JOGADOR(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT uq_tuj UNIQUE (time_usuario_id, jogador_id)
);

-- Dados exemplo
INSERT INTO USUARIO (nome,email,senha,sexo,telefone,data_nascimento,time_preferido) VALUES
 ('Eduardo Fontes','edu@example.com','hash_senha','M','77-99122-9637','2000-08-25','FURIA'),
 ('Larissa','lari@example.com','hash','F',NULL,'2001-03-10','LOUD');

INSERT INTO TIME_OFICIAL (nome,sigla) VALUES
 ('Furia Esports','FUR'),
 ('LOUD','LOD');

INSERT INTO JOGADOR (nome,posicao,time_id) VALUES
 ('Jogador A','Atacante',1),
 ('Jogador B','Meio-campo',1),
 ('Jogador C','Defensor',2),
 ('Jogador D','Goleiro',NULL);

INSERT INTO TIME_USUARIO (nome,usuario_id) VALUES
 ('Time do Edu',1),
 ('Time da Lari',2);

INSERT INTO TIME_USUARIO_JOGADOR (time_usuario_id,jogador_id) VALUES
 (1,1),(1,2),(1,4),
 (2,2),(2,3);

-- CONSULTAS (Q1–Q5)

-- Q1
SELECT j.id, j.nome, j.posicao, t.nome AS time_oficial
FROM JOGADOR j
LEFT JOIN TIME_OFICIAL t ON t.id = j.time_id
ORDER BY t.nome IS NULL, t.nome, j.nome;

-- Q2
SELECT tu.nome AS time_usuario, u.nome AS dono, j.nome AS jogador, j.posicao
FROM TIME_USUARIO tu
JOIN USUARIO u ON u.id = tu.usuario_id
JOIN TIME_USUARIO_JOGADOR tuj ON tuj.time_usuario_id = tu.id
JOIN JOGADOR j ON j.id = tuj.jogador_id
ORDER BY time_usuario, jogador;

-- Q3
SELECT t.nome AS time_oficial, j.posicao, COUNT(*) AS qtd
FROM JOGADOR j
JOIN TIME_OFICIAL t ON t.id = j.time_id
GROUP BY t.nome, j.posicao
ORDER BY t.nome, qtd DESC;

-- Q4
SELECT j.id, j.nome, j.posicao
FROM JOGADOR j
WHERE j.time_id IS NULL;

-- Q5
SELECT u.nome AS usuario,
       u.time_preferido,
       COUNT(*) AS jogadores_do_time_preferido
FROM USUARIO u
JOIN TIME_USUARIO tu           ON tu.usuario_id = u.id
JOIN TIME_USUARIO_JOGADOR tuj  ON tuj.time_usuario_id = tu.id
JOIN JOGADOR j                 ON j.id = tuj.jogador_id
JOIN TIME_OFICIAL tofc         ON tofc.id = j.time_id
WHERE tofc.sigla = CASE
                     WHEN u.time_preferido='FURIA' THEN 'FUR'
                     WHEN u.time_preferido='LOUD'  THEN 'LOD'
                     ELSE tofc.sigla
                   END
GROUP BY u.id, u.time_preferido;
