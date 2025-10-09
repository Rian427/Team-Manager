import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict

DB_CONFIG = {
  "host": "localhost",
  "user": "root",
  "password": "admin",
  "database": "teammanager",
  "port": 3000
}

def get_connection():
  """Abre e retorna uma nova conexão com o banco MySQL."""
  return mysql.connector.connect(**DB_CONFIG)

def fetchone(query: str, params: tuple = ()):
  conn = get_connection()
  try:
    cur = conn.cursor(dictionary=True)  # 'dictionary=True' faz cada linha ser retornada como dict
    cur.execute(query, params)
    return cur.fetchone()
  finally:
    cur.close()
    conn.close()

def fetchall(query: str, params: tuple = ()):
  conn = get_connection()
  try:
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params)
    return cur.fetchall()  # retorna uma lista de dicionários
  finally:
    cur.close()
    conn.close()

def execute(query: str, params: tuple = ()):
  conn = get_connection()
  try:
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()  # grava as alterações no banco
    return cur.lastrowid
  finally:
    cur.close()
    conn.close()

def get_user_by_username(username: str) -> Optional[Dict]:
  """Busca um usuário pelo username e retorna dados completos + cargo."""
  return fetchone("""
    SELECT u.*, p.name AS position_name, p.level AS position_level
    FROM users u
    JOIN positions p ON u.position_id = p.id
    WHERE u.username = %s
  """, (username,))

def create_user(name: str, username: str, date_birth: Optional[str], position_id: int, password: str) -> int:
  """Insere um novo usuário no banco."""
  return execute("""
    INSERT INTO users (name, username, date_birth, position_id, password)
    VALUES (%s, %s, %s, %s, %s)
  """, (name, username, date_birth, position_id, password))

def get_all_positions() -> List[Dict]:
  """Retorna todos os cargos existentes."""
  return fetchall("SELECT * FROM positions ORDER BY level ASC")

def create_position(name: str, level: int) -> int:
  """Cria um novo cargo."""
  return execute("INSERT INTO positions (name, level) VALUES (%s, %s)", (name, level))

def get_positions_with_higher_level_than(level: int) -> List[Dict]:
  """
  Retorna cargos com nível MAIOR (ou seja, menos poder) do que o informado.
  Exemplo: se level=1 (CEO), retorna todos os níveis 2,3,4...
  """
  return fetchall("SELECT * FROM positions WHERE level > %s ORDER BY level ASC", (level,))

def get_positions_with_lower_level_than(level: int) -> List[Dict]:
  """Retorna cargos com nível MENOR (ou seja, mais poder) que o informado."""
  return fetchall("SELECT * FROM positions WHERE level < %s ORDER BY level ASC", (level,))

def get_manageable_users_by_user(user_id: int) -> List[Dict]:
  """
  Retorna usuários que o usuário com 'user_id' pode gerenciar
  (ou seja, cargos com level > seu próprio level).
  """
  user = fetchone("""
    SELECT u.*, p.level AS position_level
    FROM users u JOIN positions p ON u.position_id = p.id
    WHERE u.id = %s
  """, (user_id,))
  if not user:
    return []
  my_level = user['position_level']
  return fetchall("""
    SELECT u.id, u.name, u.username, u.date_birth, u.position_id,
            p.name AS position_name, p.level AS position_level
    FROM users u JOIN positions p ON u.position_id = p.id
    WHERE p.level > %s
    ORDER BY p.level ASC, u.name ASC
  """, (my_level,))

def update_user_position(user_id: int, new_position_id: int):
  """Atualiza o cargo (posição) de um usuário."""
  return execute("UPDATE users SET position_id = %s WHERE id = %s", (new_position_id, user_id))

def delete_user(user_id: int):
  """Remove um usuário do banco."""
  conn = get_connection()
  try:
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
  finally:
    cur.close()
    conn.close()