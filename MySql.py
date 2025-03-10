import mysql.connector
import numpy as np
import cv2

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

        # Crear la base de datos si no existe
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
            rostro LONGBLOB
        )
        """
        self.cursor.execute(query)
        self.conexion.commit()

    def guardar_usuario(self, nombre, tipo_documento, numero_documento, rostro):
        try:
            query = "INSERT INTO usuarios (nombre, tipo_documento, numero_documento, rostro) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(query, (nombre, tipo_documento, numero_documento, rostro))
            self.conexion.commit()
        except mysql.connector.Error as err:
            print(f"Error al guardar usuario: {err}")

    def buscar_usuario(self, rostro):
        query = "SELECT nombre, numero_documento, rostro FROM usuarios"
        self.cursor.execute(query)
        usuarios = self.cursor.fetchall()

        for nombre, num_doc, rostro_guardado in usuarios:
            if self.comparar_rostros(rostro, rostro_guardado):
                return nombre, num_doc

        return None, None

    def comparar_rostros(self, rostro_nuevo, rostro_guardado):
        try:
            array_guardado = np.frombuffer(rostro_guardado, dtype=np.uint8)
            array_nuevo = np.frombuffer(rostro_nuevo, dtype=np.uint8)

            # Convertir los datos en imágenes
            img_guardada = cv2.imdecode(array_guardado, cv2.IMREAD_GRAYSCALE)
            img_nueva = cv2.imdecode(array_nuevo, cv2.IMREAD_GRAYSCALE)

            # Comparación por histograma
            hist_guardado = cv2.calcHist([img_guardada], [0], None, [256], [0, 256])
            hist_nuevo = cv2.calcHist([img_nueva], [0], None, [256], [0, 256])
            similitud = cv2.compareHist(hist_guardado, hist_nuevo, cv2.HISTCMP_CORREL)

            # Si la similitud es alta (cercana a 1), es el mismo rostro
            return similitud > 0.8
        except:
            return False

    def cerrar_conexion(self):
        self.cursor.close()
        self.conexion.close()
