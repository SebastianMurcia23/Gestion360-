import mysql.connector
import numpy as np
import face_recognition
from datetime import datetime

class BaseDeDatos:
    def __init__(self):
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Sebastian0423.",
            port=3306
        )
        self.cursor = self.conexion.cursor()
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS reconocimiento_facial")
        self.cursor.execute("USE reconocimiento_facial")
        self.crear_tabla()
        self.crear_tabla_turnos()

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
        
    def crear_tabla_turnos(self):
        query = """
        CREATE TABLE IF NOT EXISTS registro_turnos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_usuario VARCHAR(100),
            numero_documento VARCHAR(50),
            hora_entrada DATETIME,
            hora_salida DATETIME NULL,
            duracion VARCHAR(50) NULL,
            FOREIGN KEY (numero_documento) REFERENCES usuarios(numero_documento)
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
            
    def registrar_entrada(self, nombre_usuario, numero_documento):
        """Registra la hora de entrada de un usuario"""
        try:
            # Verificar que no haya un turno activo para ese usuario
            if self.verificar_turno_activo(numero_documento):
                return False
                
            hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = """INSERT INTO registro_turnos 
                    (nombre_usuario, numero_documento, hora_entrada) 
                    VALUES (%s, %s, %s)"""
            self.cursor.execute(query, (nombre_usuario, numero_documento, hora_actual))
            self.conexion.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al registrar entrada: {err}")
            return False
            
    def registrar_salida(self, numero_documento):
        """Registra la hora de salida y calcula la duración del turno"""
        try:
            # Buscar el registro de entrada sin salida
            query = """SELECT id, hora_entrada FROM registro_turnos 
                    WHERE numero_documento = %s AND hora_salida IS NULL 
                    ORDER BY hora_entrada DESC LIMIT 1"""
            self.cursor.execute(query, (numero_documento,))
            resultado = self.cursor.fetchone()
            
            if not resultado:
                return False
                
            id_registro, hora_entrada = resultado
            hora_salida = datetime.now()
            
            # Asegurarnos de trabajar con objetos datetime
            if isinstance(hora_entrada, str):
                hora_entrada_dt = datetime.strptime(hora_entrada, '%Y-%m-%d %H:%M:%S')
            elif isinstance(hora_entrada, datetime):
                hora_entrada_dt = hora_entrada
            else:
                # Para cualquier otro formato, convertir a string y luego a datetime
                hora_entrada_dt = datetime.strptime(str(hora_entrada), '%Y-%m-%d %H:%M:%S')
            
            # Calcular duración (incluye días si es necesario)
            duracion = hora_salida - hora_entrada_dt
            total_segundos = duracion.total_seconds()
            dias = duracion.days
            horas = int(total_segundos // 3600) % 24
            minutos = int((total_segundos % 3600) // 60)
            
            
            # Formato apropiado según la duración
            if dias > 0:
                duracion_formato = f"{dias}d {horas}h {minutos}m {int(total_segundos)}sg"
            elif horas > 0:
                duracion_formato = f"{horas}h {minutos}m {int(total_segundos)}sg"
            elif minutos > 0:
                duracion_formato = f"{minutos}h {int(total_segundos)}sg"
            else:
                duracion_formato = f"{int(total_segundos)}sg" 
            
            # Actualizar registro
            query = """UPDATE registro_turnos 
                    SET hora_salida = %s, duracion = %s 
                    WHERE id = %s"""
            self.cursor.execute(query, (hora_salida.strftime('%Y-%m-%d %H:%M:%S'), duracion_formato, id_registro))
            self.conexion.commit()
            return True
        except Exception as err:
            print(f"Error al registrar salida: {err}")
            return False
            
    def verificar_turno_activo(self, numero_documento):
        """Verifica si un usuario tiene un turno activo (sin hora de salida)"""
        try:
            query = """SELECT COUNT(*) FROM registro_turnos 
                    WHERE numero_documento = %s AND hora_salida IS NULL"""
            self.cursor.execute(query, (numero_documento,))
            cantidad = self.cursor.fetchone()[0]
            return cantidad > 0
        except mysql.connector.Error as err:
            print(f"Error al verificar turno activo: {err}")
            return False
            
    def obtener_info_turno_activo(self, numero_documento):
        """Obtiene información del turno activo de un usuario"""
        try:
            query = """SELECT id, hora_entrada FROM registro_turnos 
                    WHERE numero_documento = %s AND hora_salida IS NULL 
                    ORDER BY hora_entrada DESC LIMIT 1"""
            self.cursor.execute(query, (numero_documento,))
            resultado = self.cursor.fetchone()
            
            if resultado:
                id_registro, hora_entrada = resultado
                return {
                    'id': id_registro,
                    'hora_inicio': hora_entrada.strftime('%Y-%m-%d %H:%M:%S') if isinstance(hora_entrada, datetime) else str(hora_entrada)
                }
            return None
        except mysql.connector.Error as err:
            print(f"Error al obtener información del turno: {err}")
            return None
            
    def obtener_historial_turnos(self, numero_documento):
        """Obtiene el historial de turnos de un usuario específico"""
        try:
            query = """SELECT id, hora_entrada, hora_salida, duracion 
                    FROM registro_turnos 
                    WHERE numero_documento = %s AND hora_salida IS NOT NULL 
                    ORDER BY hora_entrada DESC"""
            self.cursor.execute(query, (numero_documento,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener historial: {err}")
            return []
            
    def obtener_registros_turnos(self):
        """Obtiene todos los registros de turnos para los administradores"""
        try:
            query = """SELECT t.id, t.nombre_usuario, t.numero_documento, 
                    t.hora_entrada, t.hora_salida, t.duracion 
                    FROM registro_turnos t 
                    ORDER BY t.hora_entrada DESC"""
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener registros: {err}")
            return []
        
    def obtener_todos_usuarios(self):
        """Obtiene la lista de todos los usuarios registrados"""
        try:
            query = """SELECT id, nombre, tipo_documento, numero_documento, rol 
                    FROM usuarios ORDER BY nombre"""
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener usuarios: {err}")
            return []

    def obtener_usuario_por_id(self, id_usuario):
        """Obtiene los datos de un usuario específico por su ID"""
        try:
            query = """SELECT id, nombre, tipo_documento, numero_documento, rol 
                    FROM usuarios WHERE id = %s"""
            self.cursor.execute(query, (id_usuario,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error al obtener usuario: {err}")
            return None

    def actualizar_usuario(self, id_usuario, nombre, tipo_documento, numero_documento, rol):
        """Actualiza los datos de un usuario existente"""
        try:
            query = """UPDATE usuarios SET nombre = %s, tipo_documento = %s, 
                    numero_documento = %s, rol = %s WHERE id = %s"""
            self.cursor.execute(query, (nombre, tipo_documento, numero_documento, rol, id_usuario))
            self.conexion.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al actualizar usuario: {err}")
            return False

    def eliminar_usuario(self, id_usuario):
        """Elimina un usuario de la base de datos"""
        try:
            # Primero verificamos si el usuario tiene registros en la tabla de turnos
            query_check = """SELECT COUNT(*) FROM registro_turnos 
                        WHERE numero_documento = (SELECT numero_documento FROM usuarios WHERE id = %s)"""
            self.cursor.execute(query_check, (id_usuario,))
            count = self.cursor.fetchone()[0]
            
            if count > 0:
                # Si tiene registros, no podemos eliminar por la restricción de clave foránea
                return "No se puede eliminar el usuario porque tiene registros de turnos asociados"
            
            # Si no tiene registros, procedemos a eliminar
            query = "DELETE FROM usuarios WHERE id = %s"
            self.cursor.execute(query, (id_usuario,))
            self.conexion.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al eliminar usuario: {err}")
            return str(err)
        
def calcular_nomina_usuario(self, num_doc, fecha_inicio, fecha_fin, valor_hora=10000):
    """Calcula la nómina para un usuario en un período específico"""
    try:
        # Obtenemos los turnos del usuario en el período seleccionado
        query = """
        SELECT hora_entrada, hora_salida, duracion 
        FROM registro_turnos 
        WHERE numero_documento = %s 
        AND hora_entrada BETWEEN %s AND %s
        AND hora_salida IS NOT NULL
        ORDER BY hora_entrada DESC
        """
        self.cursor.execute(query, (num_doc, fecha_inicio, fecha_fin))
        turnos = self.cursor.fetchall()
        
        # Información del usuario
        query_usuario = "SELECT nombre, tipo_documento FROM usuarios WHERE numero_documento = %s"
        self.cursor.execute(query_usuario, (num_doc,))
        info_usuario = self.cursor.fetchone()
        
        if not info_usuario:
            return None
        
        nombre_usuario, tipo_doc = info_usuario
        
        # Datos para la nómina
        total_horas = 0
        detalles_turnos = []
        
        for entrada, salida, duracion in turnos:
            # Convertir a datetime si no lo son ya
            if isinstance(entrada, str):
                entrada_dt = datetime.strptime(entrada, '%Y-%m-%d %H:%M:%S')
            else:
                entrada_dt = entrada
                
            if isinstance(salida, str):
                salida_dt = datetime.strptime(salida, '%Y-%m-%d %H:%M:%S')
            else:
                salida_dt = salida
            
            # Calcular horas trabajadas
            diff = salida_dt - entrada_dt
            horas = diff.total_seconds() / 3600  # Convertir segundos a horas
            total_horas += horas
            
            detalles_turnos.append({
                'fecha': entrada_dt.strftime('%Y-%m-%d'),
                'entrada': entrada_dt.strftime('%H:%M'),
                'salida': salida_dt.strftime('%H:%M'),
                'horas': round(horas, 2),
                'valor': int(horas * valor_hora)
            })
        
        # Calcular totales
        subtotal = total_horas * valor_hora
        salud = subtotal * 0.04  # 4% para salud
        pension = subtotal * 0.04  # 4% para pensión
        total = subtotal - salud - pension
        
        return {
            'nombre': nombre_usuario,
            'documento': f"{tipo_doc}: {num_doc}",
            'periodo': f"{fecha_inicio} al {fecha_fin}",
            'turnos': detalles_turnos,
            'total_horas': round(total_horas, 2),
            'valor_hora': valor_hora,
            'subtotal': int(subtotal),
            'salud': int(salud),
            'pension': int(pension),
            'total': int(total)
        }
    except Exception as e:
        print(f"Error al calcular nómina: {e}")
        return None

def obtener_usuarios_para_nomina(self):
    """Obtiene la lista de usuarios que tienen registros de turnos"""
    try:
        query = """
        SELECT DISTINCT u.numero_documento, u.nombre 
        FROM usuarios u
        INNER JOIN registro_turnos t ON u.numero_documento = t.numero_documento
        WHERE t.hora_salida IS NOT NULL
        ORDER BY u.nombre
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener usuarios para nómina: {e}")
        return []
        
def guardar_nomina(self, datos_nomina):
    """Guarda un registro de nómina en la base de datos"""
    try:
        # Crear tabla si no existe
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS nominas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            numero_documento VARCHAR(50),
            nombre_usuario VARCHAR(100),
            fecha_inicio DATE,
            fecha_fin DATE,
            total_horas FLOAT,
            valor_hora INT,
            subtotal INT,
            descuento_salud INT,
            descuento_pension INT,
            total INT,
            fecha_generacion DATETIME,
            FOREIGN KEY (numero_documento) REFERENCES usuarios(numero_documento)
        )
        """)
        self.conexion.commit()
        
        # Insertar registro
        query = """
        INSERT INTO nominas (
            numero_documento, nombre_usuario, fecha_inicio, fecha_fin,
            total_horas, valor_hora, subtotal, descuento_salud,
            descuento_pension, total, fecha_generacion
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            datos_nomina['documento'].split(': ')[1],
            datos_nomina['nombre'],
            datos_nomina['periodo'].split(' al ')[0],
            datos_nomina['periodo'].split(' al ')[1],
            datos_nomina['total_horas'],
            datos_nomina['valor_hora'],
            datos_nomina['subtotal'],
            datos_nomina['salud'],
            datos_nomina['pension'],
            datos_nomina['total'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        self.cursor.execute(query, values)
        self.conexion.commit()
        return self.cursor.lastrowid
    except Exception as e:
        print(f"Error al guardar nómina: {e}")
        return None
        
def obtener_nominas(self):
    """Obtiene todas las nóminas generadas"""
    try:
        query = """
        SELECT id, nombre_usuario, numero_documento, 
               fecha_inicio, fecha_fin, total_horas, 
               valor_hora, total, fecha_generacion
        FROM nominas
        ORDER BY fecha_generacion DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener nóminas: {e}")
        return []

def obtener_detalle_nomina(self, id_nomina):
    """Obtiene el detalle completo de una nómina específica"""
    try:
        query = """
        SELECT * FROM nominas WHERE id = %s
        """
        self.cursor.execute(query, (id_nomina,))
        return self.cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener detalle de nómina: {e}")
        return None