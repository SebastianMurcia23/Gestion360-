import pytest
from MySql import BaseDeDatos

@pytest.fixture(autouse=True)
def limpiar_singletons():
    # Limpiar instancias entre pruebas
    BaseDeDatos._instances = {}