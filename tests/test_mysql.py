import pytest
from unittest.mock import Mock, patch
import numpy as np
from MySql import BaseDeDatos

@pytest.fixture
def mock_db():
    with patch('mysql.connector.connect') as mock_connect:
        mock_conexion = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conexion
        mock_conexion.cursor.return_value = mock_cursor
        yield mock_conexion, mock_cursor

def test_crear_tabla(mock_db):
    mock_conexion, mock_cursor = mock_db
    bd = BaseDeDatos()
    
    # Verificar que se ejecuta la query de creación
    mock_cursor.execute.assert_called()
    assert "CREATE TABLE IF NOT EXISTS usuarios" in mock_cursor.execute.call_args[0][0]
    mock_conexion.commit.assert_called_once()

def test_guardar_usuario(mock_db):  # Asegúrate de que el nombre sea exacto
    mock_conexion, mock_cursor = mock_db
    bd = BaseDeDatos()
    encoding = np.random.rand(128).tobytes()
    
    bd.guardar_usuario("Juan", "Cédula", "12345", encoding, "administrador")
    
    # Verificar parámetros
    args, _ = mock_cursor.execute.call_args
    assert args[1] == ("Juan", "Cédula", "12345", encoding, "administrador")

def test_buscar_usuario(mock_db):
    _, mock_cursor = mock_db
    bd = BaseDeDatos()
    encoding_prueba = np.random.rand(128)
    
    # Configurar mock para resultado de base de datos
    mock_cursor.fetchall.return_value = [
        ("Ana", "67890", encoding_prueba.tobytes(), "usuario")
    ]
    
    nombre, doc, _ = bd.buscar_usuario(encoding_prueba.tobytes())
    assert nombre == "Ana"
    assert doc == "67890"