"""
Laboratório Educacional de SQL Injection e Consultas Parametrizadas
DIO Agent Security - Desafio de Projeto da DIO

Este módulo fornece um banco SQLite local em memória para demonstrar:
1. Mecanismo de falha de injeção de SQL via concatenação direta de strings.
2. Defesa estrutural via Prepared Statements (consultas parametrizadas).
3. Preservação de integridade para entradas legítimas com caracteres especiais.
"""

import sqlite3
from typing import Optional, List, Dict, Any


def get_connection() -> sqlite3.Connection:
    """Cria e inicializa um banco de dados SQLite em memória com dados de exemplo."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Criação das tabelas
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # Popula dados de teste
    users_data = [
        ("admin", "pbkdf2:sha256:admin_secret_hash_9981", "ADMIN", "admin@lab.dio.me"),
        ("mariasilva", "pbkdf2:sha256:user_hash_2021", "USER", "maria@lab.dio.me"),
        ("joaodev", "pbkdf2:sha256:user_hash_4044", "USER", "joao@lab.dio.me")
    ]
    cursor.executemany(
        "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)",
        users_data
    )

    products_data = [
        ("Curso Python Fundamentos", "Educacional", 0.0),
        ("Formação Cibersegurança Defensiva", "Educacional", 199.90),
        ("Mentoria DevSecOps Prática", "Mentoria", 99.00)
    ]
    cursor.executemany(
        "INSERT INTO products (name, category, price) VALUES (?, ?, ?)",
        products_data
    )

    conn.commit()
    return conn


# ==============================================================================
# 1. AUTENTICAÇÃO
# ==============================================================================

def authenticate_vulnerable(conn: sqlite3.Connection, username: str, password_hash: str) -> Optional[Dict[str, Any]]:
    """
    [VULNERÁVEL] Autentica o usuário concatenando strings diretamente na consulta SQL.
    Falha: CWE-89 (SQL Injection). O input do usuário altera a sintaxe lógica da query.
    """
    cursor = conn.cursor()
    # Padrão inseguro: interpolação direta de parâmetros não confiáveis
    query = f"SELECT id, username, role, email FROM users WHERE username = '{username}' AND password_hash = '{password_hash}'"
    cursor.execute(query)
    row = cursor.fetchone()
    if row:
        return {"id": row[0], "username": row[1], "role": row[2], "email": row[3]}
    return None


def authenticate_secure(conn: sqlite3.Connection, username: str, password_hash: str) -> Optional[Dict[str, Any]]:
    """
    [SEGURO] Autentica o usuário usando Prepared Statement / Consulta Parametrizada.
    Mitigação: Os marcadores '?' instruem o motor SQLite a tratar o input estritamente como dado literal.
    """
    cursor = conn.cursor()
    # Padrão seguro: parâmetros isolados da estrutura do comando SQL
    query = "SELECT id, username, role, email FROM users WHERE username = ? AND password_hash = ?"
    cursor.execute(query, (username, password_hash))
    row = cursor.fetchone()
    if row:
        return {"id": row[0], "username": row[1], "role": row[2], "email": row[3]}
    return None


# ==============================================================================
# 2. BUSCA DE PRODUTOS
# ==============================================================================

def search_products_vulnerable(conn: sqlite3.Connection, search_term: str) -> List[Dict[str, Any]]:
    """
    [VULNERÁVEL] Busca produtos interpolando termo de busca diretamente.
    Permite ataques de UNION Injection para extrair registros de outras tabelas.
    """
    cursor = conn.cursor()
    query = f"SELECT id, name, category, price FROM products WHERE name LIKE '%{search_term}%'"
    cursor.execute(query)
    rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1], "category": r[2], "price": r[3]} for r in rows]


def search_products_secure(
    conn: sqlite3.Connection,
    search_term: str,
    page: int = 1,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    [SEGURO] Busca produtos usando consulta parametrizada com binding correto do curinga '%'
    e paginação defensiva contra exaustão de recursos (mitigação de DoS / CWE-400).

    Validação defensiva de paginação:
    - Impede valores negativos ou nulos para página e limite.
    - Impõe um limite máximo rígido (ex: 50 registros) para evitar consumo excessivo de memória.
    - Calcula o offset de forma segura: offset = (page - 1) * limit.
    """
    # Sanitização e normalização defensiva de parâmetros de paginação
    safe_page = max(1, int(page))
    safe_limit = max(1, min(int(limit), 50))
    offset = (safe_page - 1) * safe_limit

    cursor = conn.cursor()
    query = "SELECT id, name, category, price FROM products WHERE name LIKE ? LIMIT ? OFFSET ?"
    cursor.execute(query, (f"%{search_term}%", safe_limit, offset))
    rows = cursor.fetchall()
    return [{"id": r[0], "name": r[1], "category": r[2], "price": r[3]} for r in rows]


# ==============================================================================
# 3. CRIAÇÃO DE USUÁRIO (TESTE DE CARACTERES ESPECIAIS LEGÍTIMOS)
# ==============================================================================

def register_user_vulnerable(conn: sqlite3.Connection, username: str, password_hash: str, role: str, email: str) -> bool:
    """
    [VULNERÁVEL] Insere usuário via concatenação direta.
    Quebra com sqlite3.OperationalError se o username contiver apóstrofos legítimos (ex: "D'Angelo").

    Nota de Precisão Técnica:
    A f-string é perfeitamente válida na sintaxe do Python e não lança SyntaxError.
    O erro ocorre no analisador gramatical do motor SQLite ao receber a query malformada,
    sendo capturado e repassado pelo conector como sqlite3.OperationalError.
    """
    cursor = conn.cursor()
    query = f"INSERT INTO users (username, password_hash, role, email) VALUES ('{username}', '{password_hash}', '{role}', '{email}')"
    cursor.execute(query)
    conn.commit()
    return True


def register_user_secure(conn: sqlite3.Connection, username: str, password_hash: str, role: str, email: str) -> bool:
    """
    [SEGURO] Insere usuário com consulta parametrizada.
    Lida perfeitamente com qualquer caractere especial válido (como apóstrofos em "D'Angelo"),
    sem falhas de sintaxe SQL no banco e sem risco de injeção de código.
    """
    cursor = conn.cursor()
    query = "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)"
    cursor.execute(query, (username, password_hash, role, email))
    conn.commit()
    return True


if __name__ == "__main__":
    print("=== Laboratório DIO Agent Security ===")
    conn = get_connection()
    print("Banco em memória inicializado com sucesso.")
    print("Execute os testes automatizados com:")
    print("    python3 -m unittest lab/test_lab.py -v")
