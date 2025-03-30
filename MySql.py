import mysql.connector
import numpy as np
import face_recognition

class BaseDeDatos:
    def __init__(self):
        self.conexion = mysql.connector.connect(
            host="interchange.proxy.rlwy.net",  # Servidor de Railway
            user="root",  # Usuario de la BD
            password="EtyyxisOoQYnxGYdHxulHnJFvHSOFBOe",  # Contraseña de la BD
            database="railway",  # Nombre de la BD en Railway
            port=26224  # Puerto asignado por Railway
        )
        self.cursor = self.conexion.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS reconocimiento_facial")
        self.cursor.execute("USE reconocimiento_facial")
        self.crear_tabla()

    def crear_tabla(self):
        query = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100),
            tipo_documento VARCHAR(50),
            numero_documento VARCHAR(50) UNIQUE,
            encoding LONGBLOB
        )
        """
        self.cursor.execute(query)
        self.conexion.commit()

    def guardar_usuario(self, nombre, tipo_documento, numero_documento, encoding):
        try:
            query = "INSERT INTO usuarios (nombre, tipo_documento, numero_documento, encoding) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (nombre, tipo_documento, numero_documento, encoding))
            self.conexion.commit()
        except mysql.connector.Error as err:
            print(f"Error al guardar usuario: {err}")

    def buscar_usuario(self, encoding_nuevo):
        try:
            query = "SELECT nombre, numero_documento, encoding FROM usuarios"
            self.cursor.execute(query)
            usuarios = self.cursor.fetchall()
            
            encoding_nuevo = np.frombuffer(encoding_nuevo, dtype=np.float64)
            
            for nombre, num_doc, encoding_guardado in usuarios:
                encoding_db = np.frombuffer(encoding_guardado, dtype=np.float64)
                
                # Comparar embeddings
                distancia = face_recognition.face_distance([encoding_db], encoding_nuevo)[0]
                if distancia < 0.6:  # Umbral ajustable
                    return nombre, num_doc
                    
            return None, None
        except Exception as e:
            print(f"Error en búsqueda: {e}")
            return None, None