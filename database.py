import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Ajusta si tienes contraseña en MySQL
        database="sistema_spa"
    )
