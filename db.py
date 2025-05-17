import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",          # Tu usuario de MySQL
        password="",          # Déjalo vacío si no tienes contraseña
        database="sistema_spa"
    )
