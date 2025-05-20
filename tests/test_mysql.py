import pytest
import numpy as np
import mysql.connector
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime, timedelta
from MySql import BaseDeDatos


@pytest.fixture
def mock_mysql_connector():
    """Fixture para simular mysql.connector"""
    with patch('mysql.connector.connect') as mock_connect:
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        yield mock_connect, mock_connection, mock_cursor


@pytest.fixture
def db(mock_mysql_connector):
    """Fixture para crear una instancia de BaseDeDatos con mocks"""
    _, _, _ = mock_mysql_connector
    return BaseDeDatos()


class TestBaseDeDatos:
    def test_inicializacion(self, mock_mysql_connector):
        """Prueba la inicialización de la base de datos"""
        _, mock_connection, mock_cursor = mock_mysql_connector
        
        db = BaseDeDatos()
        
        # Verificar que se haya conectado correctamente
        assert mock_connection.cursor.called
        # Verificar que se hayan ejecutado los comandos para crear la base de datos
        assert mock_cursor.execute.call_count >= 3
        # Verificar que se llamó a "commit"
        assert mock_connection.commit.called
    
    def test_crear_tabla(self, db, mock_mysql_connector):
        """Prueba la creación de la tabla de usuarios"""
        _, _, mock_cursor = mock_mysql_connector
        
        db.crear_tabla()
        
        # Verificar que se haya ejecutado la consulta para crear la tabla
        mock_cursor.execute.assert_any_call(ANY)
    
    def test_crear_tabla_turnos(self, db, mock_mysql_connector):
        """Prueba la creación de la tabla de registro_turnos"""
        _, _, mock_cursor = mock_mysql_connector
        
        db.crear_tabla_turnos()
        
        # Verificar que se haya ejecutado la consulta para crear la tabla
        mock_cursor.execute.assert_any_call(ANY)
    
    def test_guardar_usuario(self, db, mock_mysql_connector):
        """Prueba guardar un nuevo usuario"""
        _, mock_connection, mock_cursor = mock_mysql_connector
        
        nombre = "Test User"
        tipo_documento = "Cédula"
        numero_documento = "123456789"
        encoding = np.ones(128).tobytes()
        rol = "usuario"
        
        db.guardar_usuario(nombre, tipo_documento, numero_documento, encoding, rol)
        
        # Verificar que se haya ejecutado la consulta
        mock_cursor.execute.assert_any_call(
            """INSERT INTO usuarios 
                    (nombre, tipo_documento, numero_documento, encoding, rol) 
                    VALUES (%s, %s, %s, %s, %s)""", 
            (nombre, tipo_documento, numero_documento, encoding, rol)
        )
        assert mock_connection.commit.called
    
    def test_buscar_usuario_encontrado(self, db, mock_mysql_connector):
        """Prueba buscar un usuario existente"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        nombre = "Test User"
        num_doc = "123456789"
        rol = "usuario"
        encoding_db = np.ones(128).tobytes()
        
        # Configurar el mock para devolver un usuario
        mock_cursor.fetchall.return_value = [(nombre, num_doc, encoding_db, rol)]
        
        # Simular un encoding casi idéntico (distancia < 0.6)
        encoding_nuevo = (np.ones(128) + np.random.normal(0, 0.1, 128)).tobytes()
        
        with patch('face_recognition.face_distance', return_value=np.array([0.3])):
            resultado_nombre, resultado_doc, resultado_rol = db.buscar_usuario(encoding_nuevo)
        
        assert resultado_nombre == nombre
        assert resultado_doc == num_doc
        assert resultado_rol == rol
    
    def test_buscar_usuario_no_encontrado(self, db, mock_mysql_connector):
        """Prueba buscar un usuario que no existe"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        nombre = "Test User"
        num_doc = "123456789"
        rol = "usuario"
        encoding_db = np.ones(128).tobytes()
        
        # Configurar el mock para devolver un usuario
        mock_cursor.fetchall.return_value = [(nombre, num_doc, encoding_db, rol)]
        
        # Crear un encoding muy diferente (distancia > 0.6)
        encoding_nuevo = np.zeros(128).tobytes()
        
        with patch('face_recognition.face_distance', return_value=np.array([0.7])):
            resultado_nombre, resultado_doc, resultado_rol = db.buscar_usuario(encoding_nuevo)
        
        assert resultado_nombre is None
        assert resultado_doc is None
        assert resultado_rol is None
    
    def test_registrar_entrada(self, db, mock_mysql_connector):
        """Prueba registrar entrada de un usuario"""
        _, mock_connection, mock_cursor = mock_mysql_connector
        
        # Mock de verificar_turno_activo
        with patch.object(db, 'verificar_turno_activo', return_value=False):
            nombre = "Test User"
            num_doc = "123456789"
            
            resultado = db.registrar_entrada(nombre, num_doc)
            
            assert resultado is True
            mock_cursor.execute.assert_any_call(
                """INSERT INTO registro_turnos 
                    (nombre_usuario, numero_documento, hora_entrada) 
                    VALUES (%s, %s, %s)""",
                (nombre, num_doc, ANY)
            )
            assert mock_connection.commit.called
    
    def test_registrar_entrada_turno_activo(self, db, mock_mysql_connector):
        """Prueba registrar entrada cuando ya hay un turno activo"""
        _, _, _ = mock_mysql_connector
        
        # Mock de verificar_turno_activo
        with patch.object(db, 'verificar_turno_activo', return_value=True):
            nombre = "Test User"
            num_doc = "123456789"
            
            resultado = db.registrar_entrada(nombre, num_doc)
            
            assert resultado is False
    
    def test_registrar_salida(self, db, mock_mysql_connector):
        """Prueba registrar salida de un usuario con turno activo"""
        _, mock_connection, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        num_doc = "123456789"
        id_registro = 1
        hora_entrada = datetime.now() - timedelta(hours=8)
        
        # Configurar el mock para devolver un turno activo
        mock_cursor.fetchone.return_value = (id_registro, hora_entrada)
        
        resultado = db.registrar_salida(num_doc)
        
        assert resultado is True
        mock_cursor.execute.assert_any_call(
            """UPDATE registro_turnos 
                    SET hora_salida = %s, duracion = %s 
                    WHERE id = %s""",
            (ANY, ANY, id_registro)
        )
        assert mock_connection.commit.called
    
    def test_registrar_salida_sin_turno_activo(self, db, mock_mysql_connector):
        """Prueba registrar salida sin turno activo"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Configurar el mock para indicar que no hay turno activo
        mock_cursor.fetchone.return_value = None
        
        resultado = db.registrar_salida("123456789")
        
        assert resultado is False
    
    def test_verificar_turno_activo(self, db, mock_mysql_connector):
        """Prueba verificar turno activo"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Caso 1: Con turno activo
        mock_cursor.fetchone.return_value = (1,)  # Hay un turno activo
        assert db.verificar_turno_activo("123456789") is True
        
        # Caso 2: Sin turno activo
        mock_cursor.fetchone.return_value = (0,)  # No hay turno activo
        assert db.verificar_turno_activo("123456789") is False
    
    def test_obtener_info_turno_activo(self, db, mock_mysql_connector):
        """Prueba obtener información de turno activo"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        id_registro = 1
        hora_entrada = datetime.now() - timedelta(hours=2)
        
        # Caso 1: Con turno activo
        mock_cursor.fetchone.return_value = (id_registro, hora_entrada)
        info = db.obtener_info_turno_activo("123456789")
        
        assert info is not None
        assert info['id'] == id_registro
        assert 'hora_inicio' in info
        
        # Caso 2: Sin turno activo
        mock_cursor.fetchone.return_value = None
        info = db.obtener_info_turno_activo("123456789")
        assert info is None
    
    def test_obtener_historial_turnos(self, db, mock_mysql_connector):
        """Prueba obtener historial de turnos"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        turnos = [
            (1, datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=1, hours=8), "8h 0m"),
            (2, datetime.now() - timedelta(days=2), datetime.now() - timedelta(days=2, hours=7), "7h 0m")
        ]
        
        mock_cursor.fetchall.return_value = turnos
        
        resultado = db.obtener_historial_turnos("123456789")
        
        assert resultado == turnos
        mock_cursor.execute.assert_any_call(
            """SELECT id, hora_entrada, hora_salida, duracion 
                    FROM registro_turnos 
                    WHERE numero_documento = %s AND hora_salida IS NOT NULL 
                    ORDER BY hora_entrada DESC""",
            ("123456789",)
        )
    
    def test_obtener_registros_turnos(self, db, mock_mysql_connector):
        """Prueba obtener todos los registros de turnos"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        turnos = [
            (1, "Usuario 1", "123456789", datetime.now(), datetime.now(), "8h"),
            (2, "Usuario 2", "987654321", datetime.now(), datetime.now(), "7h")
        ]
        
        mock_cursor.fetchall.return_value = turnos
        
        resultado = db.obtener_registros_turnos()
        
        assert resultado == turnos
        mock_cursor.execute.assert_any_call(
            """SELECT t.id, t.nombre_usuario, t.numero_documento, 
                    t.hora_entrada, t.hora_salida, t.duracion 
                    FROM registro_turnos t 
                    ORDER BY t.hora_entrada DESC"""
        )
    
    def test_obtener_todos_usuarios(self, db, mock_mysql_connector):
        """Prueba obtener todos los usuarios"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        usuarios = [
            (1, "Usuario 1", "Cédula", "123456789", "usuario"),
            (2, "Usuario 2", "Cédula", "987654321", "administrador")
        ]
        
        mock_cursor.fetchall.return_value = usuarios
        
        resultado = db.obtener_todos_usuarios()
        
        assert resultado == usuarios
        mock_cursor.execute.assert_any_call(
            """SELECT id, nombre, tipo_documento, numero_documento, rol 
                    FROM usuarios ORDER BY nombre"""
        )
    
    def test_obtener_usuario_por_id(self, db, mock_mysql_connector):
        """Prueba obtener usuario por id"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        usuario = (1, "Usuario 1", "Cédula", "123456789", "usuario")
        
        mock_cursor.fetchone.return_value = usuario
        
        resultado = db.obtener_usuario_por_id(1)
        
        assert resultado == usuario
        mock_cursor.execute.assert_any_call(
            """SELECT id, nombre, tipo_documento, numero_documento, rol 
                    FROM usuarios WHERE id = %s""",
            (1,)
        )
    
    def test_actualizar_usuario(self, db, mock_mysql_connector):
        """Prueba actualizar usuario"""
        _, mock_connection, mock_cursor = mock_mysql_connector
        
        # Datos de prueba
        id_usuario = 1
        nombre = "Usuario Actualizado"
        tipo_documento = "Cédula"
        numero_documento = "123456789"
        rol = "administrador"
        
        resultado = db.actualizar_usuario(id_usuario, nombre, tipo_documento, numero_documento, rol)
        
        assert resultado is True
        mock_cursor.execute.assert_any_call(
            """UPDATE usuarios SET nombre = %s, tipo_documento = %s, 
                    numero_documento = %s, rol = %s WHERE id = %s""",
            (nombre, tipo_documento, numero_documento, rol, id_usuario)
        )
        assert mock_connection.commit.called
    
    def test_eliminar_usuario_sin_turnos(self, db, mock_mysql_connector):
        """Prueba eliminar usuario sin turnos asociados"""
        _, mock_connection, mock_cursor = mock_mysql_connector
        
        # Configurar que no tenga turnos asociados
        mock_cursor.fetchone.return_value = (0,)
        
        resultado = db.eliminar_usuario(1)
        
        assert resultado is True
        mock_cursor.execute.assert_any_call("DELETE FROM usuarios WHERE id = %s", (1,))
        assert mock_connection.commit.called
    
    def test_eliminar_usuario_con_turnos(self, db, mock_mysql_connector):
        """Prueba eliminar usuario con turnos asociados"""
        _, _, mock_cursor = mock_mysql_connector
        
        # Configurar que tenga turnos asociados
        mock_cursor.fetchone.return_value = (1,)
        
        resultado = db.eliminar_usuario(1)
        
        # Debe devolver mensaje de error
        assert isinstance(resultado, str)
        assert "No se puede eliminar" in resultado