from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from typing import List, Tuple, Any, Optional
import sys
from datetime import datetime
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

def get_next_id(db: Database, collection_name: str) -> int:
    """Get next auto-increment ID for a collection"""
    result = db[collection_name].find_one(sort=[("_id", -1)])
    if result:
        return result["_id"] + 1
    return 1

def clear_screen() -> None:
    """Clear terminal screen"""
    print("\n" * 2)

def print_header(title: str) -> None:
    """Print section header"""
    clear_screen()
    print("=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)
    print()

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
    print()

def wait_for_enter() -> None:
    """Wait for user to press enter"""
    input("\nPressione ENTER para continuar...")

def cadastrar_usuario() -> None:
    """Register new user"""
    print_header("Cadastro de Usuário")

    nome = input("Nome completo: ").strip()
    if not nome:
        print("❌ Nome é obrigatório!")
        wait_for_enter()
        return

    email = input("Email: ").strip()
    if not email:
        print("❌ Email é obrigatório!")
        wait_for_enter()
        return

    senha = input("Senha: ").strip()
    if not senha:
        print("❌ Senha é obrigatória!")
        wait_for_enter()
        return

    print("\nSexo:")
    print("1 - Masculino (M)")
    print("2 - Feminino (F)")
    print("3 - Outro (O)")
    sexo_opcao = input("Escolha (1-3): ").strip()
    sexo_map = {"1": "M", "2": "F", "3": "O"}
    sexo = sexo_map.get(sexo_opcao)

    if not sexo:
        print("❌ Opção de sexo inválida!")
        wait_for_enter()
        return

    telefone = input("Telefone (opcional, pressione ENTER para pular): ").strip()
    telefone = telefone if telefone else None

    data_nascimento = input("Data de nascimento (AAAA-MM-DD): ").strip()
    try:
        datetime.strptime(data_nascimento, "%Y-%m-%d")
    except ValueError:
        print("❌ Data inválida! Use o formato AAAA-MM-DD")
        wait_for_enter()
        return

    time_preferido = input("Time preferido (opcional, pressione ENTER para pular): ").strip()
    time_preferido = time_preferido if time_preferido else None

    db = get_database()

    try:
        user_id = get_next_id(db, "usuario")
        usuario = {
            "_id": user_id,
            "nome": nome,
            "email": email,
            "senha": senha,
            "sexo": sexo,
            "telefone": telefone,
            "data_nascimento": data_nascimento,
            "time_preferido": time_preferido
        }
        db.usuario.insert_one(usuario)
        print(f"\n✅ Usuário '{nome}' cadastrado com sucesso! ID: {user_id}")
    except DuplicateKeyError:
        print("\n❌ Erro: Email já cadastrado!")
    except Exception as e:
        print(f"\n❌ Erro ao cadastrar usuário: {e}")

    wait_for_enter()

def cadastrar_time_oficial() -> None:
    """Register official team"""
    print_header("Cadastro de Time Oficial")

    nome = input("Nome do time: ").strip()
    if not nome:
        print("❌ Nome é obrigatório!")
        wait_for_enter()
        return

    sigla = input("Sigla do time (ex: FUR, LOD): ").strip().upper()
    if not sigla:
        print("❌ Sigla é obrigatória!")
        wait_for_enter()
        return

    db = get_database()

    try:
        time_id = get_next_id(db, "time_oficial")
        time_oficial = {
            "_id": time_id,
            "nome": nome,
            "sigla": sigla
        }
        db.time_oficial.insert_one(time_oficial)
        print(f"\n✅ Time '{nome}' cadastrado com sucesso! ID: {time_id}")
    except DuplicateKeyError:
        print(f"\n❌ Erro: Sigla '{sigla}' já cadastrada!")
    except Exception as e:
        print(f"\n❌ Erro ao cadastrar time: {e}")

    wait_for_enter()

def cadastrar_jogador() -> None:
    """Register player"""
    print_header("Cadastro de Jogador")

    db = get_database()

    times = list(db.time_oficial.find({}, {"_id": 1, "nome": 1, "sigla": 1}).sort("nome", ASCENDING))

    if times:
        print("Times disponíveis:")
        for time in times:
            print(f"  {time['_id']} - {time['nome']} ({time['sigla']})")
        print("  0 - Sem time (jogador livre)")
        print()

    nome = input("Nome do jogador: ").strip()
    if not nome:
        print("❌ Nome é obrigatório!")
        wait_for_enter()
        return

    posicao = input("Posição (ex: Atacante, Goleiro, Meio-campo, Defensor): ").strip()
    if not posicao:
        print("❌ Posição é obrigatória!")
        wait_for_enter()
        return

    time_id_input = input("ID do time (0 para jogador livre): ").strip()
    time_id: Optional[int] = None

    if time_id_input and time_id_input != "0":
        try:
            time_id = int(time_id_input)
        except ValueError:
            print("❌ ID inválido!")
            wait_for_enter()
            return

    try:
        jogador_id = get_next_id(db, "jogador")
        jogador = {
            "_id": jogador_id,
            "nome": nome,
            "posicao": posicao,
            "time_id": time_id
        }
        db.jogador.insert_one(jogador)
        print(f"\n✅ Jogador '{nome}' cadastrado com sucesso! ID: {jogador_id}")
    except Exception as e:
        print(f"\n❌ Erro ao cadastrar jogador: {e}")

    wait_for_enter()

def criar_time_usuario() -> None:
    """Create user team"""
    print_header("Criar Time de Usuário")

    db = get_database()

    usuarios = list(db.usuario.find({}, {"_id": 1, "nome": 1, "email": 1}).sort("nome", ASCENDING))

    if not usuarios:
        print("❌ Nenhum usuário cadastrado! Cadastre um usuário primeiro.")
        wait_for_enter()
        return

    print("Usuários disponíveis:")
    for usuario in usuarios:
        print(f"  {usuario['_id']} - {usuario['nome']} ({usuario['email']})")
    print()

    usuario_id_input = input("ID do usuário dono do time: ").strip()
    try:
        usuario_id = int(usuario_id_input)
    except ValueError:
        print("❌ ID inválido!")
        wait_for_enter()
        return

    nome_time = input("Nome do time: ").strip()
    if not nome_time:
        print("❌ Nome é obrigatório!")
        wait_for_enter()
        return

    try:
        # Check if user exists
        if not db.usuario.find_one({"_id": usuario_id}):
            print(f"\n❌ Erro: Usuário ID {usuario_id} não existe!")
        else:
            time_usuario_id = get_next_id(db, "time_usuario")
            time_usuario = {
                "_id": time_usuario_id,
                "nome": nome_time,
                "usuario_id": usuario_id
            }
            db.time_usuario.insert_one(time_usuario)
            print(f"\n✅ Time '{nome_time}' criado com sucesso! ID: {time_usuario_id}")
    except Exception as e:
        print(f"\n❌ Erro ao criar time: {e}")

    wait_for_enter()

def adicionar_jogador_time_usuario() -> None:
    """Add player to user team"""
    print_header("Adicionar Jogador ao Time de Usuário")

    db = get_database()

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
            "$project": {
                "_id": 1,
                "nome": 1,
                "dono": "$usuario.nome"
            }
        },
        {"$sort": {"nome": 1}}
    ]
    times = list(db.time_usuario.aggregate(pipeline))

    if not times:
        print("❌ Nenhum time de usuário cadastrado! Crie um time primeiro.")
        wait_for_enter()
        return

    print("Times de usuário disponíveis:")
    for time in times:
        print(f"  {time['_id']} - {time['nome']} (Dono: {time['dono']})")
    print()

    time_usuario_id_input = input("ID do time de usuário: ").strip()
    try:
        time_usuario_id = int(time_usuario_id_input)
    except ValueError:
        print("❌ ID inválido!")
        wait_for_enter()
        return

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
                "_id": 1,
                "nome": 1,
                "posicao": 1,
                "time_oficial": {"$ifNull": ["$time.nome", None]}
            }
        },
        {"$sort": {"nome": 1}}
    ]
    jogadores = list(db.jogador.aggregate(pipeline))

    if not jogadores:
        print("❌ Nenhum jogador cadastrado!")
        wait_for_enter()
        return

    print("\nJogadores disponíveis:")
    for jogador in jogadores:
        time_nome = jogador['time_oficial'] if jogador['time_oficial'] else "Livre"
        print(f"  {jogador['_id']} - {jogador['nome']} ({jogador['posicao']}) - Time: {time_nome}")
    print()

    jogador_id_input = input("ID do jogador: ").strip()
    try:
        jogador_id = int(jogador_id_input)
    except ValueError:
        print("❌ ID inválido!")
        wait_for_enter()
        return

    # Verify that time_usuario exists
    if not db.time_usuario.find_one({"_id": time_usuario_id}):
        print(f"\n❌ Erro: Time de usuário ID {time_usuario_id} não existe!")
        wait_for_enter()
        return

    # Verify that jogador exists
    if not db.jogador.find_one({"_id": jogador_id}):
        print(f"\n❌ Erro: Jogador ID {jogador_id} não existe!")
        wait_for_enter()
        return

    # Check if the relationship already exists
    existing = db.time_usuario_jogador.find_one({
        "time_usuario_id": time_usuario_id,
        "jogador_id": jogador_id
    })
    if existing:
        print("\n❌ Erro: Este jogador já está neste time!")
        wait_for_enter()
        return

    try:
        tuj_id = get_next_id(db, "time_usuario_jogador")
        tuj = {
            "_id": tuj_id,
            "time_usuario_id": time_usuario_id,
            "jogador_id": jogador_id
        }
        db.time_usuario_jogador.insert_one(tuj)
        print("\n✅ Jogador adicionado ao time com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao adicionar jogador: {e}")

    wait_for_enter()

def listar_usuarios() -> None:
    """List all users"""
    print_header("Lista de Usuários")

    db = get_database()

    try:
        usuarios = list(db.usuario.find({}).sort("nome", ASCENDING))
        results = [
            (u["_id"], u["nome"], u["email"], u["sexo"], u.get("telefone"), u["data_nascimento"], u.get("time_preferido"))
            for u in usuarios
        ]
        print_table(["ID", "Nome", "Email", "Sexo", "Telefone", "Nascimento", "Time Preferido"], results)
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")

    wait_for_enter()

def listar_times_oficiais() -> None:
    """List all official teams"""
    print_header("Lista de Times Oficiais")

    db = get_database()

    try:
        times = list(db.time_oficial.find({}).sort("nome", ASCENDING))
        results = [(t["_id"], t["nome"], t["sigla"]) for t in times]
        print_table(["ID", "Nome", "Sigla"], results)
    except Exception as e:
        print(f"❌ Erro ao listar times: {e}")

    wait_for_enter()

def listar_jogadores() -> None:
    """List all players"""
    print_header("Lista de Jogadores")

    db = get_database()

    try:
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
                    "_id": 1,
                    "nome": 1,
                    "posicao": 1,
                    "time_oficial": {"$ifNull": ["$time.nome", None]}
                }
            },
            {"$sort": {"nome": 1}}
        ]
        jogadores = list(db.jogador.aggregate(pipeline))
        results = [(j["_id"], j["nome"], j["posicao"], j["time_oficial"]) for j in jogadores]
        print_table(["ID", "Nome", "Posição", "Time Oficial"], results)
    except Exception as e:
        print(f"❌ Erro ao listar jogadores: {e}")

    wait_for_enter()

def listar_times_usuario() -> None:
    """List all user teams with their players"""
    print_header("Times de Usuário e Seus Jogadores")

    db = get_database()

    try:
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
            {
                "$unwind": {
                    "path": "$jogadores_rel",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$lookup": {
                    "from": "jogador",
                    "localField": "jogadores_rel.jogador_id",
                    "foreignField": "_id",
                    "as": "jogador"
                }
            },
            {
                "$unwind": {
                    "path": "$jogador",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$project": {
                    "time_usuario": "$nome",
                    "dono": "$usuario.nome",
                    "jogador": {"$ifNull": ["$jogador.nome", None]},
                    "posicao": {"$ifNull": ["$jogador.posicao", None]}
                }
            },
            {"$sort": {"time_usuario": 1, "jogador": 1}}
        ]
        results_data = list(db.time_usuario.aggregate(pipeline))
        results = [(r["time_usuario"], r["dono"], r["jogador"], r["posicao"]) for r in results_data]
        print_table(["Time do Usuário", "Dono", "Jogador", "Posição"], results)
    except Exception as e:
        print(f"❌ Erro ao listar times de usuário: {e}")

    wait_for_enter()

def consultas_avancadas() -> None:
    """Advanced queries menu"""
    while True:
        print_header("Consultas Avançadas")
        print("1 - Jogadores por posição em cada time oficial")
        print("2 - Jogadores sem time oficial")
        print("3 - Para um usuário específico, quantos jogadores do elenco dele pertencem ao seu 'time preferido'")
        print("0 - Voltar")
        print()

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            consulta_jogadores_por_posicao()
        elif opcao == "2":
            consulta_jogadores_sem_time()
        elif opcao == "3":
            consulta_jogadores_time_preferido()
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida!")
            wait_for_enter()

def consulta_jogadores_por_posicao() -> None:
    """Query players by position in each official team"""
    print_header("Jogadores por Posição em Cada Time Oficial")

    db = get_database()

    try:
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
        results_data = list(db.jogador.aggregate(pipeline))
        results = [(r["time_oficial"], r["posicao"], r["qtd"]) for r in results_data]
        print_table(["Time Oficial", "Posição", "Quantidade"], results)
    except Exception as e:
        print(f"❌ Erro ao executar consulta: {e}")

    wait_for_enter()

def consulta_jogadores_sem_time() -> None:
    """Query players without an official team"""
    print_header("Jogadores Sem Time Oficial")

    db = get_database()

    try:
        jogadores = list(db.jogador.find({"time_id": None}, {"_id": 1, "nome": 1, "posicao": 1}))
        results = [(j["_id"], j["nome"], j["posicao"]) for j in jogadores]
        print_table(["ID", "Nome", "Posição"], results)
    except Exception as e:
        print(f"❌ Erro ao executar consulta: {e}")

    wait_for_enter()

def consulta_jogadores_time_preferido() -> None:
    """Query players from preferred team in user teams"""
    print_header("Para um usuário específico, quantos jogadores do elenco dele pertencem ao seu 'time preferido'")

    db = get_database()

    try:
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
                "$addFields": {
                    "sigla_preferida": {
                        "$switch": {
                            "branches": [
                                {"case": {"$eq": ["$time_preferido", "FURIA"]}, "then": "FUR"},
                                {"case": {"$eq": ["$time_preferido", "LOUD"]}, "then": "LOD"}
                            ],
                            "default": "$time_oficial.sigla"
                        }
                    }
                }
            },
            {
                "$match": {
                    "$expr": {"$eq": ["$time_oficial.sigla", "$sigla_preferida"]}
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
        results_data = list(db.usuario.aggregate(pipeline))
        results = [(r["usuario"], r["time_preferido"], r["jogadores_do_time_preferido"]) for r in results_data]
        print_table(["Usuário", "Time Preferido", "Jogadores do Time Preferido"], results)
    except Exception as e:
        print(f"❌ Erro ao executar consulta: {e}")

    wait_for_enter()

def menu_cadastros() -> None:
    """Registration menu"""
    while True:
        print_header("Menu de Cadastros")
        print("1 - Cadastrar Usuário")
        print("2 - Cadastrar Time Oficial")
        print("3 - Cadastrar Jogador")
        print("4 - Criar Time de Usuário")
        print("5 - Adicionar Jogador ao Time de Usuário")
        print("0 - Voltar")
        print()

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_usuario()
        elif opcao == "2":
            cadastrar_time_oficial()
        elif opcao == "3":
            cadastrar_jogador()
        elif opcao == "4":
            criar_time_usuario()
        elif opcao == "5":
            adicionar_jogador_time_usuario()
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida!")
            wait_for_enter()

def menu_consultas() -> None:
    """Query menu"""
    while True:
        print_header("Menu de Consultas")
        print("1 - Listar Usuários")
        print("2 - Listar Times Oficiais")
        print("3 - Listar Jogadores")
        print("4 - Listar Times de Usuário e Seus Jogadores")
        print("5 - Jogadores por posição em cada time oficial")
        print("0 - Voltar")
        print()

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            listar_usuarios()
        elif opcao == "2":
            listar_times_oficiais()
        elif opcao == "3":
            listar_jogadores()
        elif opcao == "4":
            listar_times_usuario()
        elif opcao == "5":
            consulta_jogadores_por_posicao()
        elif opcao == "0":
            break
        else:
            print("❌ Opção inválida!")
            wait_for_enter()

def menu_principal() -> None:
    """Main menu"""
    while True:
        print_header("Futebol App - Sistema de Gerenciamento")
        print("1 - Cadastros")
        print("2 - Consultas")
        print("0 - Sair")
        print()

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            menu_cadastros()
        elif opcao == "2":
            menu_consultas()
        elif opcao == "0":
            print("\n👋 Até logo!")
            close_database()
            sys.exit(0)
        else:
            print("❌ Opção inválida!")
            wait_for_enter()

def main() -> None:
    """Main function"""
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Até logo!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)
    finally:
        close_database()

if __name__ == "__main__":
    main()
