import pymysql
from pymysql import Connection
from typing import List, Tuple, Any, Optional
import sys
from datetime import datetime
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

def get_connection() -> Connection:
    """Create MySQL connection"""
    config = parse_database_url(DATABASE_URL)
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    cursor.execute("USE futebol_app")
    cursor.close()
    return conn

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

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO USUARIO (nome, email, senha, sexo, telefone, data_nascimento, time_preferido)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nome, email, senha, sexo, telefone, data_nascimento, time_preferido))
        conn.commit()
        print(f"\n✅ Usuário '{nome}' cadastrado com sucesso! ID: {cursor.lastrowid}")
    except pymysql.IntegrityError as e:
        print(f"\n❌ Erro: Email já cadastrado!")
    except Exception as e:
        print(f"\n❌ Erro ao cadastrar usuário: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

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

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO TIME_OFICIAL (nome, sigla)
            VALUES (%s, %s)
        """, (nome, sigla))
        conn.commit()
        print(f"\n✅ Time '{nome}' cadastrado com sucesso! ID: {cursor.lastrowid}")
    except pymysql.IntegrityError:
        print(f"\n❌ Erro: Sigla '{sigla}' já cadastrada!")
    except Exception as e:
        print(f"\n❌ Erro ao cadastrar time: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def cadastrar_jogador() -> None:
    """Register player"""
    print_header("Cadastro de Jogador")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, sigla FROM TIME_OFICIAL ORDER BY nome")
    times = cursor.fetchall()

    if times:
        print("Times disponíveis:")
        for time in times:
            print(f"  {time[0]} - {time[1]} ({time[2]})")
        print("  0 - Sem time (jogador livre)")
        print()

    nome = input("Nome do jogador: ").strip()
    if not nome:
        print("❌ Nome é obrigatório!")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    posicao = input("Posição (ex: Atacante, Goleiro, Meio-campo, Defensor): ").strip()
    if not posicao:
        print("❌ Posição é obrigatória!")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    time_id_input = input("ID do time (0 para jogador livre): ").strip()
    time_id: Optional[int] = None

    if time_id_input and time_id_input != "0":
        try:
            time_id = int(time_id_input)
        except ValueError:
            print("❌ ID inválido!")
            cursor.close()
            conn.close()
            wait_for_enter()
            return

    try:
        cursor.execute("""
            INSERT INTO JOGADOR (nome, posicao, time_id)
            VALUES (%s, %s, %s)
        """, (nome, posicao, time_id))
        conn.commit()
        print(f"\n✅ Jogador '{nome}' cadastrado com sucesso! ID: {cursor.lastrowid}")
    except Exception as e:
        print(f"\n❌ Erro ao cadastrar jogador: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def criar_time_usuario() -> None:
    """Create user team"""
    print_header("Criar Time de Usuário")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nome, email FROM USUARIO ORDER BY nome")
    usuarios = cursor.fetchall()

    if not usuarios:
        print("❌ Nenhum usuário cadastrado! Cadastre um usuário primeiro.")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    print("Usuários disponíveis:")
    for usuario in usuarios:
        print(f"  {usuario[0]} - {usuario[1]} ({usuario[2]})")
    print()

    usuario_id_input = input("ID do usuário dono do time: ").strip()
    try:
        usuario_id = int(usuario_id_input)
    except ValueError:
        print("❌ ID inválido!")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    nome_time = input("Nome do time: ").strip()
    if not nome_time:
        print("❌ Nome é obrigatório!")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    try:
        cursor.execute("""
            INSERT INTO TIME_USUARIO (nome, usuario_id)
            VALUES (%s, %s)
        """, (nome_time, usuario_id))
        conn.commit()
        print(f"\n✅ Time '{nome_time}' criado com sucesso! ID: {cursor.lastrowid}")
    except pymysql.IntegrityError:
        print(f"\n❌ Erro: Usuário ID {usuario_id} não existe!")
    except Exception as e:
        print(f"\n❌ Erro ao criar time: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def adicionar_jogador_time_usuario() -> None:
    """Add player to user team"""
    print_header("Adicionar Jogador ao Time de Usuário")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tu.id, tu.nome, u.nome
        FROM TIME_USUARIO tu
        JOIN USUARIO u ON u.id = tu.usuario_id
        ORDER BY tu.nome
    """)
    times = cursor.fetchall()

    if not times:
        print("❌ Nenhum time de usuário cadastrado! Crie um time primeiro.")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    print("Times de usuário disponíveis:")
    for time in times:
        print(f"  {time[0]} - {time[1]} (Dono: {time[2]})")
    print()

    time_usuario_id_input = input("ID do time de usuário: ").strip()
    try:
        time_usuario_id = int(time_usuario_id_input)
    except ValueError:
        print("❌ ID inválido!")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    cursor.execute("""
        SELECT j.id, j.nome, j.posicao, t.nome AS time_oficial
        FROM JOGADOR j
        LEFT JOIN TIME_OFICIAL t ON t.id = j.time_id
        ORDER BY j.nome
    """)
    jogadores = cursor.fetchall()

    if not jogadores:
        print("❌ Nenhum jogador cadastrado!")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    print("\nJogadores disponíveis:")
    for jogador in jogadores:
        time_nome = jogador[3] if jogador[3] else "Livre"
        print(f"  {jogador[0]} - {jogador[1]} ({jogador[2]}) - Time: {time_nome}")
    print()

    jogador_id_input = input("ID do jogador: ").strip()
    try:
        jogador_id = int(jogador_id_input)
    except ValueError:
        print("❌ ID inválido!")
        cursor.close()
        conn.close()
        wait_for_enter()
        return

    try:
        cursor.execute("""
            INSERT INTO TIME_USUARIO_JOGADOR (time_usuario_id, jogador_id)
            VALUES (%s, %s)
        """, (time_usuario_id, jogador_id))
        conn.commit()
        print(f"\n✅ Jogador adicionado ao time com sucesso!")
    except pymysql.IntegrityError:
        print(f"\n❌ Erro: Jogador já está neste time ou IDs inválidos!")
    except Exception as e:
        print(f"\n❌ Erro ao adicionar jogador: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def listar_usuarios() -> None:
    """List all users"""
    print_header("Lista de Usuários")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, nome, email, sexo, telefone, data_nascimento, time_preferido
            FROM USUARIO
            ORDER BY nome
        """)
        results = cursor.fetchall()
        print_table(["ID", "Nome", "Email", "Sexo", "Telefone", "Nascimento", "Time Preferido"], results)
    except Exception as e:
        print(f"❌ Erro ao listar usuários: {e}")
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def listar_times_oficiais() -> None:
    """List all official teams"""
    print_header("Lista de Times Oficiais")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, nome, sigla
            FROM TIME_OFICIAL
            ORDER BY nome
        """)
        results = cursor.fetchall()
        print_table(["ID", "Nome", "Sigla"], results)
    except Exception as e:
        print(f"❌ Erro ao listar times: {e}")
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def listar_jogadores() -> None:
    """List all players"""
    print_header("Lista de Jogadores")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT j.id, j.nome, j.posicao, t.nome AS time_oficial
            FROM JOGADOR j
            LEFT JOIN TIME_OFICIAL t ON t.id = j.time_id
            ORDER BY j.nome
        """)
        results = cursor.fetchall()
        print_table(["ID", "Nome", "Posição", "Time Oficial"], results)
    except Exception as e:
        print(f"❌ Erro ao listar jogadores: {e}")
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def listar_times_usuario() -> None:
    """List all user teams with their players"""
    print_header("Times de Usuário e Seus Jogadores")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT tu.nome AS time_usuario, u.nome AS dono, j.nome AS jogador, j.posicao
            FROM TIME_USUARIO tu
            JOIN USUARIO u ON u.id = tu.usuario_id
            LEFT JOIN TIME_USUARIO_JOGADOR tuj ON tuj.time_usuario_id = tu.id
            LEFT JOIN JOGADOR j ON j.id = tuj.jogador_id
            ORDER BY tu.nome, j.nome
        """)
        results = cursor.fetchall()
        print_table(["Time do Usuário", "Dono", "Jogador", "Posição"], results)
    except Exception as e:
        print(f"❌ Erro ao listar times de usuário: {e}")
    finally:
        cursor.close()
        conn.close()

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

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT t.nome AS time_oficial, j.posicao, COUNT(*) AS qtd
            FROM JOGADOR j
            JOIN TIME_OFICIAL t ON t.id = j.time_id
            GROUP BY t.nome, j.posicao
            ORDER BY t.nome, qtd DESC
        """)
        results = cursor.fetchall()
        print_table(["Time Oficial", "Posição", "Quantidade"], results)
    except Exception as e:
        print(f"❌ Erro ao executar consulta: {e}")
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def consulta_jogadores_sem_time() -> None:
    """Query players without an official team"""
    print_header("Jogadores Sem Time Oficial")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT j.id, j.nome, j.posicao
            FROM JOGADOR j
            WHERE j.time_id IS NULL
        """)
        results = cursor.fetchall()
        print_table(["ID", "Nome", "Posição"], results)
    except Exception as e:
        print(f"❌ Erro ao executar consulta: {e}")
    finally:
        cursor.close()
        conn.close()

    wait_for_enter()

def consulta_jogadores_time_preferido() -> None:
    """Query players from preferred team in user teams"""
    print_header("Para um usuário específico, quantos jogadores do elenco dele pertencem ao seu 'time preferido'")

    conn = get_connection()
    cursor = conn.cursor()

    try:
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
        print(f"❌ Erro ao executar consulta: {e}")
    finally:
        cursor.close()
        conn.close()

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

if __name__ == "__main__":
    main()
