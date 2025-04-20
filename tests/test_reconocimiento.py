import pytest
import face_recognition
from unittest.mock import Mock, patch
import cv2
import numpy as np
from reconocimiento_facial import ReconocimientoFacial

@pytest.fixture
def mock_video_capture():
    # Mock de VideoCapture que simula una cámara con una imagen
    mock_cap = Mock()
    mock_cap.isOpened.return_value = True
    mock_cap.read.return_value = (True, np.zeros((50, 50, 3), dtype=np.uint8))  # Imagen negra de 50x50
    return mock_cap

def test_capturar_rostro_exitoso(mock_video_capture):
    # Crear una imagen con un rostro
    test_image = face_recognition.load_image_file("tests/test_imagenes/persona.jfif")  # Usa una imagen real o genera una
    mock_video_capture.read.return_value = (True, test_image)
    
    with patch("cv2.VideoCapture", return_value=mock_video_capture):
        rf = ReconocimientoFacial()
        encoding = rf.capturar_rostro(mostrar_video=False)
        assert encoding is not None

@patch.object(ReconocimientoFacial, 'capturar_rostro')
def test_verificar_usuario_exitoso(mock_capturar, mock_video_capture):
    mock_capturar.return_value = b"dummy_encoding"  # Simula un encoding válido
    mock_bd = Mock()
    mock_bd.buscar_usuario.return_value = ("Ana", "123", "usuario")
    
    rf = ReconocimientoFacial()
    nombre, doc, rol = rf.verificar_usuario(mock_bd)
    assert nombre == "Ana"  

@patch.object(ReconocimientoFacial, 'capturar_rostro')
def test_verificar_usuario_no_encontrado(mock_capturar):
    mock_capturar.return_value = b"dummy_encoding"  # Encoding "válido"
    mock_bd = Mock()
    mock_bd.buscar_usuario.return_value = (None, None, None)  # BD no encuentra usuario
    
    rf = ReconocimientoFacial()
    nombre, doc, rol = rf.verificar_usuario(mock_bd)
    assert nombre is None
