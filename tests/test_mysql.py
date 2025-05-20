# tests/test_mysql.py
import pytest
from MySql import BaseDeDatos
import numpy as np
from datetime import datetime, timedelta

@pytest.fixture
def db():
    # Configurar con base de datos de prueba
    test_db = BaseDeDatos()
    test_db.cursor.execute("DROP DATABASE IF EXISTS reconocimiento_facial_test")
    test_db.cursor.execute("CREATE DATABASE reconocimiento_facial_test")
    test_db.cursor.execute("USE reconocimiento_facial_test")
    test_db.crear_tabla()
    test_db.crear_tabla_turnos()
    yield test_db
    
    # Limpieza final
    test_db.cursor.execute("DROP DATABASE reconocimiento_facial_test")
    test_db.conexion.close()

def test_guardar_usuario(db):
    encoding = np.random.randn(128).tobytes()
    db.guardar_usuario("Test User", "CC", "123", encoding)
    
    usuarios = db.obtener_todos_usuarios()
    assert len(usuarios) == 1
    assert usuarios[0][1] == "Test User"

def test_registro_turno_completo(db):
    encoding = np.random.randn(128).tobytes()
    db.guardar_usuario("Work User", "TI", "456", encoding)
    
    # Registro completo
    assert db.registrar_entrada("Work User", "456") is True
    assert db.verificar_turno_activo("456") is True
    assert db.registrar_salida("456") is True
    
    historial = db.obtener_historial_turnos("456")
    assert len(historial) == 1
    assert historial[0][3] is not None  # Hora salida

def test_calculo_nomina_simple(db):
    # Configurar datos
    doc = "789"
    db.guardar_usuario("Nomina User", "CE", doc, np.random.randn(128).tobytes())
    
    # Registrar turno de 8 horas
    entrada = datetime.now() - timedelta(hours=8)
    db.registrar_entrada("Nomina User", doc)
    db.registrar_salida(doc)
    
    # Calcular
    nomina = db.calcular_nomina_usuario(
        doc, 
        entrada.strftime('%Y-%m-%d'), 
        datetime.now().strftime('%Y-%m-%d')
    )
    
    assert nomina['total_horas'] == pytest.approx(8.0, 0.1)
    assert nomina['total'] == 8 * 10000 * 0.92

def test_eliminacion_usuario(db):
    encoding = np.random.randn(128).tobytes()
    db.guardar_usuario("Delete User", "CC", "999", encoding)
    
    usuarios = db.obtener_todos_usuarios()
    user_id = usuarios[0][0]
    
    result = db.eliminar_usuario(user_id)
    assert result is True
    assert len(db.obtener_todos_usuarios()) == 0