import mysql.connector

def get_connection():
  return mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="teammanager"
  )

def autenticar(username, password):
  conn = get_connection()
  cursor = conn.cursor(dictionary=True)

  query = """
    SELECT id, name FROM users
    WHERE username = %s AND password = %s
  """
  cursor.execute(query, (username, password))
  user = cursor.fetchone()

  cursor.close()
  conn.close()

  return user

def listar_cargos():
  conn = get_connection()
  cursor = conn.cursor(dictionary=True)

  cursor.execute("SELECT id, name, level FROM positions ORDER BY level ASC")
  cargos = cursor.fetchall()

  cursor.close()
  conn.close()

  return cargos


def criar_cargo(nome):
  conn = get_connection()
  cursor = conn.cursor()

  try:
    cursor.execute("SELECT MAX(level) FROM positions")
    max_level = cursor.fetchone()[0] or 0

    cursor.execute(
        "INSERT INTO positions (name, level) VALUES (%s, %s)",
        (nome, max_level + 1)
    )
    conn.commit()
    ok = True
  except:
    ok = False

  cursor.close()
  conn.close()
  return ok

def cadastrar_funcionario(nome, username, nascimento, cargo_id, senha):
  conn = get_connection()
  cursor = conn.cursor()

  query = """
  INSERT INTO users (name, username, date_birth, position_id, password)
    VALUES (%s, %s, %s, %s, %s)
  """

  try:
    cursor.execute(query, (nome, username, nascimento, cargo_id, senha))
    conn.commit()
    ok = True
  except Exception as e:
    print("Erro:", e)
    ok = False

  cursor.close()
  conn.close()
  return ok


def listar_funcionarios():
  conn = get_connection()
  cursor = conn.cursor(dictionary=True)

  query = """
    SELECT u.name, u.username, u.date_birth, p.name AS cargo
    FROM users u
    JOIN positions p ON p.id = u.position_id
    ORDER BY p.level ASC
  """

  cursor.execute(query)
  funcionarios = cursor.fetchall()

  cursor.close()
  conn.close()
  return funcionarios