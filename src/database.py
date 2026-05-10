import sqlite3
import hashlib

def conectar():
    return sqlite3.connect('usuarios.db', check_same_thread=False)

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            username TEXT PRIMARY KEY,
            password TEXT,
            equipo_favorito TEXT
        )
    ''')
    conn.commit()
    conn.close()

def registrar_usuario(user, password, equipo):
    conn = conectar()
    cursor = conn.cursor()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        cursor.execute("INSERT INTO usuarios VALUES (?, ?, ?)", (user, pw_hash, equipo))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def verificar_usuario(user, password):
    conn = conectar()
    cursor = conn.cursor()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT equipo_favorito FROM usuarios WHERE username = ? AND password = ?", (user, pw_hash))
    resultado = cursor.fetchone()
    conn.close()
    return resultado