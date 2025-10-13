import pymysql
from pymysql import Connection
from typing import Any
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

def drop_all_tables() -> None:
    """Drop all tables from the database"""
    print("=== Dropando todas as tabelas ===\n")

    conn = get_connection(use_database=False)
    cursor = conn.cursor()

    try:
        cursor.execute("USE futebol_app")

        cursor.execute("DROP TABLE IF EXISTS TIME_USUARIO_JOGADOR")
        print("✓ Tabela TIME_USUARIO_JOGADOR dropada")

        cursor.execute("DROP TABLE IF EXISTS TIME_USUARIO")
        print("✓ Tabela TIME_USUARIO dropada")

        cursor.execute("DROP TABLE IF EXISTS JOGADOR")
        print("✓ Tabela JOGADOR dropada")

        cursor.execute("DROP TABLE IF EXISTS TIME_OFICIAL")
        print("✓ Tabela TIME_OFICIAL dropada")

        cursor.execute("DROP TABLE IF EXISTS USUARIO")
        print("✓ Tabela USUARIO dropada")

        conn.commit()
        print("\n✓ Todas as tabelas foram dropadas com sucesso!")

    except Exception as e:
        print(f"\n✗ Erro ao dropar tabelas: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def main() -> None:
    """Main function"""
    try:
        drop_all_tables()
    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
