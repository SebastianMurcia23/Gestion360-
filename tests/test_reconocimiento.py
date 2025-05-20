import pytest
import cv2
import numpy as np
from unittest.mock import patch, MagicMock, ANY
from reconocimiento_facial import ReconocimientoFacial


@pytest.fixture
def mock_cv2():
    """Fixture para simular cv2"""
    with patch('cv2.VideoCapture') as mock_video_capture:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        # También simulamos cv2.rectangle y cv2.putText
        with patch('cv2.rectangle'), patch('cv2.putText'), patch('cv2.cvtColor'):
            yield mock_video_capture, mock_cap


@pytest.fixture
def mock_face_recognition():
    """Fixture para simular face_recognition"""
    with patch('face_recognition.face_locations') as mock_locations, \
         patch('face_recognition.face_encodings') as mock_encodings:
        
        # Simular que se detecta un rostro
        mock_locations.return_value = [(50, 200, 250, 100)]  # (top, right, bottom, left)
        mock_encodings.return_value = [np.ones(128)]
        
        yield mock_locations, mock_encodings


@pytest.fixture
def mock_streamlit():
    """Fixture para simular streamlit"""
    with patch('streamlit.empty') as mock_empty, \
         patch('streamlit.button') as mock_button:
        
        mock_empty.return_value = MagicMock()
        mock_button.return_value = False  # Botón no presionado
        
        yield


@pytest.fixture
def reconocimiento_facial(mock_cv2, mock_streamlit):
    """Fixture para crear instancia de ReconocimientoFacial con mocks"""
    _, _ = mock_cv2
    return ReconocimientoFacial(camara_source=0)


class TestReconocimientoFacial:
    def test_inicializar_camara(self, reconocimiento_facial, mock_cv2):
        """Prueba la inicialización de la cámara"""
        mock_video_capture, _ = mock_cv2
        
        # Forzar la inicialización de la cámara
        reconocimiento_facial._inicializar_camara()
        
        # Verificar que se llamó a VideoCapture
        mock_video_capture.assert_called_once_with(0)
    
    def test_inicializar_camara_error(self, mock_cv2):
        """Prueba inicialización de cámara con error"""
        mock_video_capture, mock_cap = mock_cv2
        mock_cap.isOpened.return_value = False
        
        reconocimiento = ReconocimientoFacial(camara_source=0)
        
        with patch('streamlit.error') as mock_error:
            with pytest.raises(RuntimeError):
                reconocimiento._inicializar_camara()
            mock_error.assert_called_once()
    
    def test_capturar_rostro_con_rostro_detectado(self, reconocimiento_facial, mock_cv2, mock_face_recognition, mock_streamlit):
        """Prueba capturar rostro con detección exitosa"""
        _, mock_cap = mock_cv2
        mock_locations, _ = mock_face_recognition
        
        # Configurar la detección de un rostro
        mock_locations.return_value = [(50, 200, 250, 100)]  # (top, right, bottom, left)
        
        encoding = reconocimiento_facial.capturar_rostro("Test", mostrar_video=True)
        
        # Verificar que se cerró la cámara después de detectar un rostro
        mock_cap.release.assert_called_once()
        # Verificar que hay un encoding no nulo
        assert encoding is not None
    
    def test_capturar_rostro_con_boton_stop(self, reconocimiento_facial, mock_cv2, mock_face_recognition):
        """Prueba capturar rostro con botón de parar presionado"""
        _, mock_cap = mock_cv2
        
        # Simular botón presionado
        with patch('streamlit.button', return_value=True):
            encoding = reconocimiento_facial.capturar_rostro(mostrar_video=True)
        
        # Verificar que se cerró la cámara
        mock_cap.release.assert_called_once()
    
    def test_capturar_rostro_error_camara(self, reconocimiento_facial, mock_cv2):
        """Prueba capturar rostro con error en la cámara"""
        _, mock_cap = mock_cv2
        
        # Simular error en la lectura de frame
        mock_cap.read.return_value = (False, None)
        
        with patch('streamlit.warning') as mock_warning:
            encoding = reconocimiento_facial.capturar_rostro(mostrar_video=True)
            mock_warning.assert_called_once()
        
        # Verificar que se cerró la cámara
        mock_cap.release.assert_called_once()
        # No debería haber encoding
        assert encoding is None
    
    def test_verificar_usuario_encontrado(self, reconocimiento_facial):
        """Prueba verificar usuario encontrado"""
        # Datos de prueba
        nombre = "Test User"
        num_doc = "123456789"
        rol = "usuario"
        
        # Mock de la base de datos
        mock_bd = MagicMock()
        mock_bd.buscar_usuario.return_value = (nombre, num_doc, rol)
        
        # Mock de capturar_rostro
        with patch.object(reconocimiento_facial, 'capturar_rostro') as mock_capturar:
            mock_capturar.return_value = np.ones(128).tobytes()
            
            resultado_nombre, resultado_doc, resultado_rol = reconocimiento_facial.verificar_usuario(mock_bd)
            
            assert resultado_nombre == nombre
            assert resultado_doc == num_doc
            assert resultado_rol == rol
            mock_bd.buscar_usuario.assert_called_once_with(mock_capturar.return_value)
    
    def test_verificar_usuario_no_encontrado(self, reconocimiento_facial):
        """Prueba verificar usuario no encontrado"""
        # Mock de la base de datos
        mock_bd = MagicMock()
        mock_bd.buscar_usuario.return_value = (None, None, None)
        
        # Mock de capturar_rostro
        with patch.object(reconocimiento_facial, 'capturar_rostro') as mock_capturar:
            mock_capturar.return_value = np.ones(128).tobytes()
            
            resultado_nombre, resultado_doc, resultado_rol = reconocimiento_facial.verificar_usuario(mock_bd)
            
            assert resultado_nombre is None
            assert resultado_doc is None
            assert resultado_rol is None
    
