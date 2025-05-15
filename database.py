import sqlite3

def init_db():
    conn = sqlite3.connect('spa.db')
    c = conn.cursor()
    
    # Crear tabla para las reservas
    c.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            servicio TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    
def crear_tabla_admin():
    conn = sqlite3.connect('spa.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insertar_admin_por_defecto():
    conn = sqlite3.connect('spa.db')
    c = conn.cursor()
    # Usuario: admin / Contraseña: 1234
    c.execute('INSERT OR IGNORE INTO admin (usuario, contrasena) VALUES (?, ?)', ('admin', '1234'))
    conn.commit()
    conn.close()
    
def crear_tabla_usuarios():
    conn = sqlite3.connect('spa.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

