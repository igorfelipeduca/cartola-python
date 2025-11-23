from pymongo import MongoClient
from pymongo.database import Database
from typing import List, Tuple, Any
import sys
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

# Global variables for connection management
_client: MongoClient = None
_database: Database = None

def get_database() -> Database:
    """Get MongoDB database (singleton pattern)"""
    global _client, _database

    if _database is None:
        _client = MongoClient(MONGODB_URI)
        db_name = MONGODB_URI.split("/")[-1].split("?")[0]
        if not db_name or db_name == "":
            db_name = "futebol_app"
        _database = _client[db_name]

    return _database

def close_database() -> None:
    """Close MongoDB connection"""
    global _client, _database

    if _client is not None:
        _client.close()
        _client = None
        _database = None

def execute_ddl() -> None:
    """Drop existing collections and create new ones"""
    print("=== Criando banco de dados e coleções ===\n")

    db = get_database()

    try:
        # Drop collections if they exist
        db.time_usuario_jogador.drop()
        db.time_usuario.drop()
        db.jogador.drop()
        db.time_oficial.drop()
        db.usuario.drop()

        # Create collections (they'll be created automatically on first insert, but we can create them explicitly)
        db.create_collection("usuario")
        db.create_collection("time_oficial")
        db.create_collection("jogador")
        db.create_collection("time_usuario")
        db.create_collection("time_usuario_jogador")

        # Create indexes for unique constraints and performance
        db.usuario.create_index("email", unique=True)
        db.time_oficial.create_index("sigla", unique=True)
        db.time_usuario_jogador.create_index([("time_usuario_id", 1), ("jogador_id", 1)], unique=True)

        print("✓ Banco de dados e coleções criados com sucesso\n")

    except Exception as e:
        print(f"✗ Erro ao criar banco de dados: {e}")
        raise

def insert_test_data() -> None:
    """Insert test data into collections"""
    print("=== Inserindo dados de teste ===\n")

    db = get_database()

    try:
        # Insert usuarios
        usuarios = [
            {
                "_id": 1,
                "nome": "Eduardo Fontes",
                "email": "edu@example.com",
                "senha": "hash_senha",
                "sexo": "M",
                "telefone": "77-99122-9637",
                "data_nascimento": "2000-08-25",
                "time_preferido": "FURIA"
            },
            {
                "_id": 2,
                "nome": "Larissa",
                "email": "lari@example.com",
                "senha": "hash",
                "sexo": "F",
                "telefone": None,
                "data_nascimento": "2001-03-10",
                "time_preferido": "LOUD"
            }
        ]
        db.usuario.insert_many(usuarios)

        # Insert times oficiais
        times_oficiais = [
            {"_id": 1, "nome": "Furia Esports", "sigla": "FUR", "nome_curto": "FURIA"},
            {"_id": 2, "nome": "LOUD", "sigla": "LOD", "nome_curto": "LOUD"}
        ]
        db.time_oficial.insert_many(times_oficiais)

        # Insert jogadores
        jogadores = [
            {"_id": 1, "nome": "Jogador A", "posicao": "Atacante", "time_id": 1},
            {"_id": 2, "nome": "Jogador B", "posicao": "Meio-campo", "time_id": 1},
            {"_id": 3, "nome": "Jogador C", "posicao": "Defensor", "time_id": 2},
            {"_id": 4, "nome": "Jogador D", "posicao": "Goleiro", "time_id": None}
        ]
        db.jogador.insert_many(jogadores)

        # Insert times de usuario
        times_usuario = [
            {"_id": 1, "nome": "Time do Edu", "usuario_id": 1},
            {"_id": 2, "nome": "Time da Lari", "usuario_id": 2}
        ]
        db.time_usuario.insert_many(times_usuario)

        # Insert time_usuario_jogador
        time_usuario_jogadores = [
            {"_id": 1, "time_usuario_id": 1, "jogador_id": 1},
            {"_id": 2, "time_usuario_id": 1, "jogador_id": 2},
            {"_id": 3, "time_usuario_id": 1, "jogador_id": 4},
            {"_id": 4, "time_usuario_id": 2, "jogador_id": 2},
            {"_id": 5, "time_usuario_id": 2, "jogador_id": 3}
        ]
        db.time_usuario_jogador.insert_many(time_usuario_jogadores)

        print("✓ Dados de teste inseridos com sucesso\n")

    except Exception as e:
        print(f"✗ Erro ao inserir dados: {e}")
        raise

def execute_queries() -> None:
    """Execute 5 read queries"""
    print("=== Executando consultas ===\n")

    db = get_database()

    try:
        print("Q1: Listar todos os jogadores com seus times oficiais\n")
        pipeline = [
            {
                "$lookup": {
                    "from": "time_oficial",
                    "localField": "time_id",
                    "foreignField": "_id",
                    "as": "time"
                }
            },
            {
                "$unwind": {
                    "path": "$time",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "id": "$_id",
                    "nome": 1,
                    "posicao": 1,
                    "time_oficial": {"$ifNull": ["$time.nome", None]}
                }
            },
            {
                "$sort": {"time_oficial": 1, "nome": 1}
            }
        ]
        results = list(db.jogador.aggregate(pipeline))
        formatted_results = [(r["id"], r["nome"], r["posicao"], r["time_oficial"]) for r in results]
        print_table(["ID", "Nome", "Posição", "Time Oficial"], formatted_results)

        print("\n" + "="*80 + "\n")
        print("Q2: Listar times de usuários com seus jogadores\n")
        pipeline = [
            {
                "$lookup": {
                    "from": "usuario",
                    "localField": "usuario_id",
                    "foreignField": "_id",
                    "as": "usuario"
                }
            },
            {"$unwind": "$usuario"},
            {
                "$lookup": {
                    "from": "time_usuario_jogador",
                    "localField": "_id",
                    "foreignField": "time_usuario_id",
                    "as": "jogadores_rel"
                }
            },
            {"$unwind": "$jogadores_rel"},
            {
                "$lookup": {
                    "from": "jogador",
                    "localField": "jogadores_rel.jogador_id",
                    "foreignField": "_id",
                    "as": "jogador"
                }
            },
            {"$unwind": "$jogador"},
            {
                "$project": {
                    "time_usuario": "$nome",
                    "dono": "$usuario.nome",
                    "jogador": "$jogador.nome",
                    "posicao": "$jogador.posicao"
                }
            },
            {
                "$sort": {"time_usuario": 1, "jogador": 1}
            }
        ]
        results = list(db.time_usuario.aggregate(pipeline))
        formatted_results = [(r["time_usuario"], r["dono"], r["jogador"], r["posicao"]) for r in results]
        print_table(["Time do Usuário", "Dono", "Jogador", "Posição"], formatted_results)

        print("\n" + "="*80 + "\n")
        print("Q3: Contar jogadores por posição em cada time oficial\n")
        pipeline = [
            {
                "$match": {"time_id": {"$ne": None}}
            },
            {
                "$lookup": {
                    "from": "time_oficial",
                    "localField": "time_id",
                    "foreignField": "_id",
                    "as": "time"
                }
            },
            {"$unwind": "$time"},
            {
                "$group": {
                    "_id": {
                        "time_oficial": "$time.nome",
                        "posicao": "$posicao"
                    },
                    "qtd": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "time_oficial": "$_id.time_oficial",
                    "posicao": "$_id.posicao",
                    "qtd": 1
                }
            },
            {
                "$sort": {"time_oficial": 1, "qtd": -1}
            }
        ]
        results = list(db.jogador.aggregate(pipeline))
        formatted_results = [(r["time_oficial"], r["posicao"], r["qtd"]) for r in results]
        print_table(["Time Oficial", "Posição", "Quantidade"], formatted_results)

        print("\n" + "="*80 + "\n")
        print("Q4: Listar jogadores sem time oficial\n")
        results = list(db.jogador.find({"time_id": None}, {"_id": 1, "nome": 1, "posicao": 1}))
        formatted_results = [(r["_id"], r["nome"], r["posicao"]) for r in results]
        print_table(["ID", "Nome", "Posição"], formatted_results)

        print("\n" + "="*80 + "\n")
        print("Q5: Para um usuário específico, quantos jogadores do elenco dele pertencem ao seu 'time preferido'\n")
        pipeline = [
            {
                "$lookup": {
                    "from": "time_usuario",
                    "localField": "_id",
                    "foreignField": "usuario_id",
                    "as": "times"
                }
            },
            {"$unwind": "$times"},
            {
                "$lookup": {
                    "from": "time_usuario_jogador",
                    "localField": "times._id",
                    "foreignField": "time_usuario_id",
                    "as": "jogadores_rel"
                }
            },
            {"$unwind": "$jogadores_rel"},
            {
                "$lookup": {
                    "from": "jogador",
                    "localField": "jogadores_rel.jogador_id",
                    "foreignField": "_id",
                    "as": "jogador"
                }
            },
            {"$unwind": "$jogador"},
            {
                "$lookup": {
                    "from": "time_oficial",
                    "localField": "jogador.time_id",
                    "foreignField": "_id",
                    "as": "time_oficial"
                }
            },
            {"$unwind": "$time_oficial"},
            {
                "$lookup": {
                    "from": "time_oficial",
                    "localField": "time_preferido",
                    "foreignField": "nome_curto",
                    "as": "time_preferido_obj"
                }
            },
            {
                "$unwind": {
                    "path": "$time_preferido_obj",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$match": {
                    "$expr": {"$eq": ["$time_oficial.sigla", "$time_preferido_obj.sigla"]}
                }
            },
            {
                "$group": {
                    "_id": {
                        "usuario": "$nome",
                        "time_preferido": "$time_preferido"
                    },
                    "jogadores_do_time_preferido": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "usuario": "$_id.usuario",
                    "time_preferido": "$_id.time_preferido",
                    "jogadores_do_time_preferido": 1
                }
            }
        ]
        results = list(db.usuario.aggregate(pipeline))
        formatted_results = [(r["usuario"], r["time_preferido"], r["jogadores_do_time_preferido"]) for r in results]
        print_table(["Usuário", "Time Preferido", "Jogadores do Time Preferido"], formatted_results)

    except Exception as e:
        print(f"✗ Erro ao executar consultas: {e}")
        raise

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
    finally:
        close_database()

if __name__ == "__main__":
    main()
