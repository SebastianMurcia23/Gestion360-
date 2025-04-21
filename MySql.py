import mysql.connector
import numpy as np
import face_recognition

class BaseDeDatos:
    def __init__(self):
        self.conexion = mysql.connector.connect(
        host="gestion360.ctc0io2scw9l.us-east-2.rds.amazonaws.com",
        user="admin",
        password="Gestion3601234",
        database="gestion360",
        port=3306,
        ssl_ca='rds-combined-ca-bundle.pem'  # Opcional, pero recomendado
    )
        


        
        self.cursor = self.conexion.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS gestion360")
        self.cursor.execute("USE gestion360")
        self.crear_tabla()

    def crear_tabla(self):
        query = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100),
            tipo_documento VARCHAR(50),
            numero_documento VARCHAR(50) UNIQUE,
            encoding LONGBLOB,
            rol ENUM('usuario', 'administrador') DEFAULT 'usuario'
        )
        """
        self.cursor.execute(query)
        self.conexion.commit()

    def guardar_usuario(self, nombre, tipo_documento, numero_documento, encoding, rol='usuario'):
        try:
            query = """INSERT INTO usuarios 
                    (nombre, tipo_documento, numero_documento, encoding, rol) 
                    VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (nombre, tipo_documento, numero_documento, encoding, rol))
            self.conexion.commit()
        except mysql.connector.Error as err:
            print(f"Error al guardar usuario: {err}")

    def buscar_usuario(self, encoding_nuevo):
        try:
            query = "SELECT nombre, numero_documento, encoding, rol FROM usuarios"
            self.cursor.execute(query)
            usuarios = self.cursor.fetchall()
            
            encoding_nuevo = np.frombuffer(encoding_nuevo, dtype=np.float64)
            
            for nombre, num_doc, encoding_guardado, rol in usuarios:
                encoding_db = np.frombuffer(encoding_guardado, dtype=np.float64)
                
                distancia = face_recognition.face_distance([encoding_db], encoding_nuevo)[0]
                if distancia < 0.6:
                    return nombre, num_doc, rol 
                    
            return None, None, None
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            return None, None, None