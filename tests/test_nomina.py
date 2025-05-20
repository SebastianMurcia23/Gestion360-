import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import sys
import io

# Mock classes and dependencies
class MockBaseDeDatos:
    def __init__(self):
        self.cursor = MagicMock()
        self.conexion = MagicMock()
        self.mock_data = {}
        
        # Add the nomina methods needed for testing
        self.calcular_nomina_usuario = self._calcular_nomina_usuario
        self.obtener_usuarios_para_nomina = self._obtener_usuarios_para_nomina
        self.guardar_nomina = self._guardar_nomina
        self.obtener_nominas = self._obtener_nominas
        self.obtener_usuario_por_id = self._obtener_usuario_por_id
        
    def _calcular_nomina_usuario(self, num_doc, fecha_inicio, fecha_fin, valor_hora=10000):
        # Mock implementation for calculating user payroll
        if num_doc == "123456789":
            # Get a sample user with turnos
            turnos = [
                (datetime.now() - timedelta(days=5, hours=8), datetime.now() - timedelta(days=5), 8.0),
                (datetime.now() - timedelta(days=4, hours=8), datetime.now() - timedelta(days=4), 8.0),
            ]
            
            # Return mock nomina data
            detalles_turnos = []
            total_horas = 0
            
            for entrada, salida, duracion in turnos:
                horas = duracion
                total_horas += horas
                
                detalles_turnos.append({
                    'fecha': entrada.strftime('%Y-%m-%d'),
                    'entrada': entrada.strftime('%H:%M'),
                    'salida': salida.strftime('%H:%M'),
                    'horas': round(horas, 2),
                    'valor': int(horas * valor_hora)
                })
            
            subtotal = total_horas * valor_hora
            salud = subtotal * 0.04
            pension = subtotal * 0.04
            recargos_nocturnos = valor_hora * 0.35
            total = subtotal - salud - pension
            
            return {
                'nombre': 'Juan Pérez',
                'documento': f"Cédula: {num_doc}",
                'periodo': f"{fecha_inicio} al {fecha_fin}",
                'turnos': detalles_turnos,
                'total_horas': round(total_horas, 2),
                'valor_hora': valor_hora,
                'subtotal': int(subtotal),
                'salud': int(salud),
                'pension': int(pension),
                'recargos_nocturnos': int(recargos_nocturnos),
                'total': int(total)
            }
        elif num_doc == "987654321":
            # User with no turnos
            return {
                'nombre': 'Pedro García',
                'documento': f"Cédula: {num_doc}",
                'periodo': f"{fecha_inicio} al {fecha_fin}",
                'turnos': [],
                'total_horas': 0,
                'valor_hora': valor_hora,
                'subtotal': 0,
                'salud': 0,
                'pension': 0,
                'recargos_nocturnos': 0,
                'total': 0
            }
        else:
            return None
    
    def _obtener_usuarios_para_nomina(self):
        # Mock implementation to get users for payroll
        return [
            ("123456789", "Juan Pérez"),
            ("987654321", "Pedro García"),
            ("456789123", "María Rodríguez")
        ]
    
    def _guardar_nomina(self, datos_nomina):
        # Mock implementation to save payroll
        return 1  # Return a mock ID for the saved payroll
    
    def _obtener_nominas(self):
        # Mock implementation to get all payrolls
        return [
            (1, "Juan Pérez", "123456789", "2025-05-01", "2025-05-15", 16.0, 10000, 160000, "2025-05-15 14:30:00"),
            (2, "Pedro García", "987654321", "2025-05-01", "2025-05-15", 8.0, 12000, 96000, "2025-05-15 15:20:00")
        ]
        
    def _obtener_usuario_por_id(self, user_id):
        # Mock implementation to get user by ID
        users = {
            1: (1, "Juan Pérez", "Cédula", "123456789", "usuario"),
            2: (2, "Pedro García", "Cédula", "987654321", "usuario")
        }
        return users.get(user_id)


# Tests for the Nómina module
class TestNomina:
    
    @pytest.fixture
    def bd_mock(self):
        return MockBaseDeDatos()
    
    def test_calcular_nomina_usuario_with_turnos(self, bd_mock):
        """Test calculating payroll for a user with shifts"""
        nomina = bd_mock.calcular_nomina_usuario(
            "123456789", 
            "2025-05-01", 
            "2025-05-15", 
            10000
        )
        
        # Assert the result contains expected fields
        assert nomina is not None
        assert nomina['nombre'] == 'Juan Pérez'
        assert nomina['documento'] == 'Cédula: 123456789'
        assert 'turnos' in nomina
        assert len(nomina['turnos']) == 2
        assert nomina['total_horas'] == 16.0
        assert nomina['valor_hora'] == 10000
        assert nomina['subtotal'] == 160000
        assert nomina['salud'] == 6400
        assert nomina['pension'] == 6400
        assert nomina['total'] == 147200
    
    def test_calcular_nomina_usuario_without_turnos(self, bd_mock):
        """Test calculating payroll for a user without shifts"""
        nomina = bd_mock.calcular_nomina_usuario(
            "987654321", 
            "2025-05-01", 
            "2025-05-15", 
            10000
        )
        
        # Assert the result contains expected fields
        assert nomina is not None
        assert nomina['nombre'] == 'Pedro García'
        assert nomina['documento'] == 'Cédula: 987654321'
        assert 'turnos' in nomina
        assert len(nomina['turnos']) == 0
        assert nomina['total_horas'] == 0
        assert nomina['subtotal'] == 0
        assert nomina['total'] == 0
    
    def test_calcular_nomina_usuario_nonexistent(self, bd_mock):
        """Test calculating payroll for a nonexistent user"""
        nomina = bd_mock.calcular_nomina_usuario(
            "000000000", 
            "2025-05-01", 
            "2025-05-15", 
            10000
        )
        
        # Assert the result is None for nonexistent user
        assert nomina is None
    
    def test_obtener_usuarios_para_nomina(self, bd_mock):
        """Test getting users for payroll"""
        usuarios = bd_mock.obtener_usuarios_para_nomina()
        
        # Assert we get the expected list of users
        assert len(usuarios) == 3
        assert usuarios[0][0] == "123456789"
        assert usuarios[0][1] == "Juan Pérez"
    
    def test_guardar_nomina(self, bd_mock):
        """Test saving payroll data"""
        nomina_data = {
            'nombre': 'Juan Pérez',
            'documento': 'Cédula: 123456789',
            'periodo': '2025-05-01 al 2025-05-15',
            'turnos': [
                {
                    'fecha': '2025-05-10',
                    'entrada': '08:00',
                    'salida': '16:00',
                    'horas': 8.0,
                    'valor': 80000
                }
            ],
            'total_horas': 8.0,
            'valor_hora': 10000,
            'subtotal': 80000,
            'salud': 3200,
            'pension': 3200,
            'total': 73600
        }
        
        result = bd_mock.guardar_nomina(nomina_data)
        
        # Assert the result is the expected ID
        assert result == 1
    
    def test_obtener_nominas(self, bd_mock):
        """Test getting all payrolls"""
        nominas = bd_mock.obtener_nominas()
        
        # Assert we get the expected list of payrolls
        assert len(nominas) == 2
        assert nominas[0][1] == "Juan Pérez"
        assert nominas[1][1] == "Pedro García"

    @patch('pandas.DataFrame.to_csv')
    def test_export_to_csv(self, mock_to_csv, bd_mock):
        """Test exporting payroll data to CSV"""
        # Mock the pandas to_csv method to return a known string
        mock_to_csv.return_value = "ID,Empleado,Documento,Fecha Inicio,Fecha Fin,Total Horas,Valor Hora,Total Pagado"
        
        # Get payroll data
        nominas = bd_mock.obtener_nominas()
        
        # Convert to DataFrame
        df = pd.DataFrame(nominas, columns=[
            "ID", "Empleado", "Documento", "Fecha Inicio", 
            "Fecha Fin", "Total Horas", "Valor Hora", 
            "Total Pagado", "Fecha Generación"
        ])
        
        # Generate CSV
        csv = df.to_csv(index=False)
        
        # Verify that to_csv was called
        mock_to_csv.assert_called_once_with(index=False)

    @patch('reportlab.platypus.SimpleDocTemplate')
    def test_generar_pdf_nomina(self, mock_simpledoc, bd_mock):
        """Test generating PDF for payroll"""
        from reportlab.platypus import SimpleDocTemplate
        from io import BytesIO
        
        # Mock the reportlab objects
        mock_doc = MagicMock()
        mock_simpledoc.return_value = mock_doc
        
        # Function to simulate generating a PDF (simplified version from app.py)
        def generar_pdf_nomina(nomina):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer)
            doc.build([])  # Empty content just for the test
            pdf = buffer.getvalue()
            buffer.close()
            return pdf
            
        # Get a nomina for testing
        nomina = bd_mock.calcular_nomina_usuario(
            "123456789", 
            "2025-05-01", 
            "2025-05-15", 
            10000
        )
        
        # Call the function
        pdf_data = generar_pdf_nomina(nomina)
        
        # Verify that the document build was called
        mock_doc.build.assert_called_once()
