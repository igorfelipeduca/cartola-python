import pymysql
from pymysql import Connection
from typing import List, Tuple, Any
import sys
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

def parse_database_url(url: str) -> dict[str, Any]:
    """Parse MySQL connection URL"""
    url = url.replace("mysql://", "")

    auth, host_port_db = url.split("@")
    user, password = auth.split(":")

    host_port, database = host_port_db.rsplit("/", 1)
    host, port = host_port.split(":")

    return {
        "host": host,
        "port": int(port),
        "user": user,
        "password": password,
        "database": database
    }

def get_connection(use_database: bool = True) -> Connection:
    """Create MySQL connection"""
    config = parse_database_url(DATABASE_URL)

    if not use_database:
        config.pop("database")

    return pymysql.connect(**config)

def execute_ddl() -> None:
    """Execute DDL statements to create database and tables"""
    print("=== Criando banco de dados e tabelas ===\n")

    conn = get_connection(use_database=False)
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS futebol_app DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci")
        cursor.execute("USE futebol_app")

        cursor.execute("DROP TABLE IF EXISTS TIME_USUARIO_JOGADOR")
        cursor.execute("DROP TABLE IF EXISTS TIME_USUARIO")
        cursor.execute("DROP TABLE IF EXISTS JOGADOR")
        cursor.execute("DROP TABLE IF EXISTS TIME_OFICIAL")
        cursor.execute("DROP TABLE IF EXISTS USUARIO")

        cursor.execute("""
            CREATE TABLE USUARIO (
              id              INT AUTO_INCREMENT PRIMARY KEY,
              nome            VARCHAR(120)        NOT NULL,
              email           VARCHAR(160)        NOT NULL UNIQUE,
              senha           VARCHAR(255)        NOT NULL,
              sexo            ENUM('M','F','O')   NOT NULL,
              telefone        VARCHAR(20),
              data_nascimento DATE                NOT NULL,
              time_preferido  VARCHAR(80)
            )
        """)

        cursor.execute("""
            CREATE TABLE TIME_OFICIAL (
              id     INT AUTO_INCREMENT PRIMARY KEY,
              nome   VARCHAR(120) NOT NULL,
              sigla  VARCHAR(10)  NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE JOGADOR (
              id      INT AUTO_INCREMENT PRIMARY KEY,
              nome    VARCHAR(120) NOT NULL,
              posicao VARCHAR(40)  NOT NULL,
              time_id INT,
              CONSTRAINT fk_jog_time
                FOREIGN KEY (time_id) REFERENCES TIME_OFICIAL(id)
                ON UPDATE CASCADE ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE TIME_USUARIO (
              id         INT AUTO_INCREMENT PRIMARY KEY,
              nome       VARCHAR(120) NOT NULL,
              usuario_id INT          NOT NULL,
              CONSTRAINT fk_timeuser_user
                FOREIGN KEY (usuario_id) REFERENCES USUARIO(id)
                ON UPDATE CASCADE ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE TIME_USUARIO_JOGADOR (
              id              INT AUTO_INCREMENT PRIMARY KEY,
              time_usuario_id INT NOT NULL,
              jogador_id      INT NOT NULL,
              CONSTRAINT fk_tuj_timeuser FOREIGN KEY (time_usuario_id) REFERENCES TIME_USUARIO(id)
                ON UPDATE CASCADE ON DELETE CASCADE,
              CONSTRAINT fk_tuj_jog FOREIGN KEY (jogador_id) REFERENCES JOGADOR(id)
                ON UPDATE CASCADE ON DELETE CASCADE,
              CONSTRAINT uq_tuj UNIQUE (time_usuario_id, jogador_id)
            )
        """)

        conn.commit()
        print("✓ Banco de dados e tabelas criados com sucesso\n")

    except Exception as e:
        print(f"✗ Erro ao criar banco de dados: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def insert_test_data() -> None:
    """Insert test data into tables"""
    print("=== Inserindo dados de teste ===\n")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("USE futebol_app")

        cursor.executemany("""
            INSERT INTO USUARIO (nome, email, senha, sexo, telefone, data_nascimento, time_preferido)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, [
            ('Eduardo Fontes', 'edu@example.com', 'hash_senha', 'M', '77-99122-9637', '2000-08-25', 'FURIA'),
            ('Larissa', 'lari@example.com', 'hash', 'F', None, '2001-03-10', 'LOUD')
        ])

        cursor.executemany("""
            INSERT INTO TIME_OFICIAL (nome, sigla) VALUES (%s, %s)
        """, [
            ('Furia Esports', 'FUR'),
            ('LOUD', 'LOD')
        ])

        cursor.executemany("""
            INSERT INTO JOGADOR (nome, posicao, time_id) VALUES (%s, %s, %s)
        """, [
            ('Jogador A', 'Atacante', 1),
            ('Jogador B', 'Meio-campo', 1),
            ('Jogador C', 'Defensor', 2),
            ('Jogador D', 'Goleiro', None)
        ])

        cursor.executemany("""
            INSERT INTO TIME_USUARIO (nome, usuario_id) VALUES (%s, %s)
        """, [
            ('Time do Edu', 1),
            ('Time da Lari', 2)
        ])

        cursor.executemany("""
            INSERT INTO TIME_USUARIO_JOGADOR (time_usuario_id, jogador_id) VALUES (%s, %s)
        """, [
            (1, 1), (1, 2), (1, 4),
            (2, 2), (2, 3)
        ])

        conn.commit()
        print("✓ Dados de teste inseridos com sucesso\n")

    except Exception as e:
        print(f"✗ Erro ao inserir dados: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def execute_queries() -> None:
    """Execute 5 read queries from script.sql"""
    print("=== Executando consultas ===\n")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("USE futebol_app")

        print("Q1: Listar todos os jogadores com seus times oficiais\n")
        cursor.execute("""
            SELECT j.id, j.nome, j.posicao, t.nome AS time_oficial
            FROM JOGADOR j
            LEFT JOIN TIME_OFICIAL t ON t.id = j.time_id
            ORDER BY t.nome IS NULL, t.nome, j.nome
        """)
        results = cursor.fetchall()
        print_table(["ID", "Nome", "Posição", "Time Oficial"], results)

        print("\n" + "="*80 + "\n")
        print("Q2: Listar times de usuários com seus jogadores\n")
        cursor.execute("""
            SELECT tu.nome AS time_usuario, u.nome AS dono, j.nome AS jogador, j.posicao
            FROM TIME_USUARIO tu
            JOIN USUARIO u ON u.id = tu.usuario_id
            JOIN TIME_USUARIO_JOGADOR tuj ON tuj.time_usuario_id = tu.id
            JOIN JOGADOR j ON j.id = tuj.jogador_id
            ORDER BY time_usuario, jogador
        """)
        results = cursor.fetchall()
        print_table(["Time do Usuário", "Dono", "Jogador", "Posição"], results)

        print("\n" + "="*80 + "\n")
        print("Q3: Contar jogadores por posição em cada time oficial\n")
        cursor.execute("""
            SELECT t.nome AS time_oficial, j.posicao, COUNT(*) AS qtd
            FROM JOGADOR j
            JOIN TIME_OFICIAL t ON t.id = j.time_id
            GROUP BY t.nome, j.posicao
            ORDER BY t.nome, qtd DESC
        """)
        results = cursor.fetchall()
        print_table(["Time Oficial", "Posição", "Quantidade"], results)

        print("\n" + "="*80 + "\n")
        print("Q4: Listar jogadores sem time oficial\n")
        cursor.execute("""
            SELECT j.id, j.nome, j.posicao
            FROM JOGADOR j
            WHERE j.time_id IS NULL
        """)
        results = cursor.fetchall()
        print_table(["ID", "Nome", "Posição"], results)

        print("\n" + "="*80 + "\n")
        print("Q5: Para um usuário específico, quantos jogadores do elenco dele pertencem ao seu 'time preferido'\n")
        cursor.execute("""
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
            GROUP BY u.id, u.time_preferido
        """)
        results = cursor.fetchall()
        print_table(["Usuário", "Time Preferido", "Jogadores do Time Preferido"], results)

    except Exception as e:
        print(f"✗ Erro ao executar consultas: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def print_table(headers: List[str], rows: List[Tuple[Any, ...]]) -> None:
    """Print query results in a formatted table"""
    if not rows:
        print("Nenhum resultado encontrado.")
        return

    col_widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else "NULL"
            col_widths[i] = max(col_widths[i], len(cell_str))

    header_row = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * w for w in col_widths)

    print(header_row)
    print(separator)

    for row in rows:
        row_str = " | ".join(
            (str(cell) if cell is not None else "NULL").ljust(col_widths[i])
            for i, cell in enumerate(row)
        )
        print(row_str)

def main() -> None:
    """Main function"""
    try:
        execute_ddl()
        insert_test_data()
        execute_queries()
        print("\n✓ Todas as operações concluídas com sucesso!")

    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
