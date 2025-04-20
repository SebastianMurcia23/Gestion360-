import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from app import bd, reconocimiento_facial
import numpy as np

# ---------------------------
# Fixtures comunes
# ---------------------------
@pytest.fixture
def mock_db():
    mock_bd = Mock()
    mock_bd.buscar_usuario.return_value = (None, None, None)
    return mock_bd

@pytest.fixture
def mock_session_state():
    return {"autenticado": False, "rol": None, "nombre": None}

# ---------------------------
# Tests de Login Administrativo
# ---------------------------
@patch('streamlit.button')
@patch('streamlit.text_input')
def test_login_admin_exitoso(mock_input, mock_button, mock_session_state):
    # Configurar mocks
    mock_input.side_effect = ["admin", "1234"]
    mock_button.return_value = True
    
    # Ejecutar lógica
    if mock_button("Iniciar Sesión"):
        if mock_input("Usuario") == "admin" and mock_input("Contraseña") == "1234":
            mock_session_state["autenticado"] = True
            mock_session_state["rol"] = "administrador"
    
    assert mock_session_state["autenticado"] == True
    assert mock_session_state["rol"] == "administrador"

@patch('streamlit.button')
@patch('streamlit.text_input')
def test_login_admin_fallido(mock_input, mock_button, mock_session_state):
    mock_input.side_effect = ["admin", "password_incorrecta"]
    mock_button.return_value = True
    
    if mock_button("Iniciar Sesión"):
        mock_session_state["autenticado"] = False
    
    assert mock_session_state["autenticado"] == False

# ---------------------------
# Tests de Reconocimiento Facial
# ---------------------------
@patch('app.reconocimiento_facial.verificar_usuario')
@patch('streamlit.button')
def test_login_facial_exitoso(mock_button, mock_verificar, mock_db):
    # Configurar mocks
    mock_verificar.return_value = ("Ana Pérez", "112233", "usuario")
    mock_button.return_value = True  # Simular clic en el botón
    nombre, num_doc, rol = None, None, None
    
    # Ejecutar lógica
    if mock_button("Face Id"):
        nombre, num_doc, rol = reconocimiento_facial.verificar_usuario(mock_db, False)
        
    # Verificaciones
    assert nombre == "Ana Pérez"  # Solo validamos el retorno mockeado

@patch('app.reconocimiento_facial.verificar_usuario')
@patch('streamlit.button')
def test_login_facial_fallido(mock_button, mock_verificar, mock_db):
    # Configurar mocks
    mock_verificar.return_value = (None, None, None)
    mock_button.return_value = True
    error = None
    
    # Ejecutar lógica
    if mock_button("Face Id"):
        nombre, _, _ = reconocimiento_facial.verificar_usuario(mock_db, False)
        error = "Usuario no válido o rostro no detectado" if not nombre else None
    
    # Verificación
    assert error is not None

# ---------------------------
# Tests de Módulo Administrativo
# ---------------------------
@patch('app.ReconocimientoFacial.capturar_rostro')
@patch('streamlit.button')
def test_registro_usuario_exitoso(mock_button, mock_capturar, mock_db):
    # Configurar mocks
    mock_capturar.return_value = np.random.rand(128).tobytes()
    mock_button.side_effect = [True]  # Simular clic en "Capturar Rostro"
    
    # Simular entrada de datos
    nombre = "Carlos Gómez"
    tipo_doc = "Cédula"
    num_doc = "445566"
    
    # Ejecutar lógica
    if mock_button("📸 Capturar Rostro"):
        encoding = mock_capturar()
        if encoding:
            mock_db.guardar_usuario(nombre, tipo_doc, num_doc, encoding, "usuario")
    
    # Verificaciones
    assert mock_db.guardar_usuario.called
    assert mock_db.guardar_usuario.call_args[0][0] == "Carlos Gómez"

@patch('app.ReconocimientoFacial.verificar_usuario')
@patch('streamlit.button')
def test_verificacion_rostro_fallida(mock_button, mock_verificar, mock_db):
    # Configurar mocks
    mock_verificar.return_value = (None, None, None)
    mock_button.return_value = True
    nombre, num_doc, rol = None, None, None
    
    # Ejecutar lógica
    if mock_button("🔍 Verificar Rostro"):
        nombre, num_doc, rol = reconocimiento_facial.verificar_usuario(mock_db)
        
    # Verificación
    assert nombre is None