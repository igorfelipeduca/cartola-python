from pymongo import MongoClient
from pymongo.database import Database
import sys
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

def get_database() -> Database:
    """Create MongoDB connection and return database"""
    client = MongoClient(MONGODB_URI)
    db_name = MONGODB_URI.split("/")[-1].split("?")[0]
    if not db_name or db_name == "":
        db_name = "futebol_app"
    return client[db_name]

def drop_all_collections() -> None:
    """Drop all collections from the database"""
    print("=== Dropando todas as coleções ===\n")

    db = get_database()

    try:
        db.time_usuario_jogador.drop()
        print("✓ Coleção time_usuario_jogador dropada")

        db.time_usuario.drop()
        print("✓ Coleção time_usuario dropada")

        db.jogador.drop()
        print("✓ Coleção jogador dropada")

        db.time_oficial.drop()
        print("✓ Coleção time_oficial dropada")

        db.usuario.drop()
        print("✓ Coleção usuario dropada")

        print("\n✓ Todas as coleções foram dropadas com sucesso!")

    except Exception as e:
        print(f"\n✗ Erro ao dropar coleções: {e}")
        raise

def main() -> None:
    """Main function"""
    try:
        drop_all_collections()
    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
