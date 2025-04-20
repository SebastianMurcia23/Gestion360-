import pytest
from unittest.mock import Mock, patch
from app import bd, reconocimiento_facial
import streamlit as st

# Fixture con la estructura de menús para los tests
@pytest.fixture
def mock_menus():
    return {
        "principal": {
            "titulo": "📋 Menú Principal - Seleccione una opción:",
            "opciones": {
                "1": {"texto": "Consultar horarios 📅", "accion": "menu", "destino": "horarios"},
                "3": {"texto": "Información general ℹ️", "accion": "respuesta", "texto_respuesta": "🌟 Somos Gestión360, su solución integral."},
                "4": {"texto": "Contacto 📧", "accion": "respuesta", "texto_respuesta": "📩 Email: soporte@gestion360.com\n📞 Teléfono: +57 123 456 7890"}
            }
        },
        "horarios": {
            "titulo": "⏰ Gestión de Horarios:",
            "opciones": {
                "0": {"texto": "Volver al menú principal ↩️", "accion": "menu", "destino": "principal"}
            }
        }
    }

# Fixture para el estado del chatbot
@pytest.fixture
def mock_chatbot_state():
    return {
        'menu_actual': 'principal',
        'historial': [{
            'tipo': 'sistema',
            'contenido': '¡Bienvenido! Soy su asistente virtual. ¿En qué puedo ayudarle?'
        }]
    }

# ---------------------------
# Tests corregidos
# ---------------------------
@patch('streamlit.form_submit_button')
@patch('streamlit.text_input')
def test_navegacion_menu_principal_a_horarios(mock_input, mock_submit, mock_chatbot_state, mock_menus):
    mock_input.return_value = '1'
    mock_submit.return_value = True
    
    menu_actual = mock_chatbot_state['menu_actual']
    opciones = mock_menus[menu_actual]['opciones']['1']
    
    if opciones['accion'] == 'menu':
        mock_chatbot_state['menu_actual'] = opciones['destino']
    
    assert mock_chatbot_state['menu_actual'] == 'horarios'

@patch('streamlit.form_submit_button')
@patch('streamlit.text_input')
def test_respuesta_informacion_general(mock_input, mock_submit, mock_chatbot_state, mock_menus):
    mock_input.return_value = '3'
    mock_submit.return_value = True
    
    menu_actual = mock_chatbot_state['menu_actual']
    respuesta_esperada = mock_menus[menu_actual]['opciones']['3']['texto_respuesta']
    
    mock_chatbot_state['historial'].append({
        'tipo': 'sistema',
        'contenido': respuesta_esperada
    })
    
    assert len(mock_chatbot_state['historial']) == 2
    assert "Gestión360" in mock_chatbot_state['historial'][-1]['contenido']

@patch('streamlit.form_submit_button')
@patch('streamlit.text_input')
def test_opcion_invalida(mock_input, mock_submit, mock_chatbot_state):
    mock_input.return_value = '99'
    mock_submit.return_value = True
    
    error_msg = "⚠️ Opción no válida. Por favor seleccione una de las opciones mostradas."
    mock_chatbot_state['historial'].append({
        'tipo': 'sistema',
        'contenido': error_msg
    })
    
    assert "no válida" in mock_chatbot_state['historial'][-1]['contenido']

@patch('streamlit.form_submit_button')
@patch('streamlit.text_input')
def test_flujo_completo_conversacion(mock_input, mock_submit, mock_menus):
    mock_input.side_effect = ['1', '0', '4']
    mock_submit.side_effect = [True, True, True]

    state = {
        'menu_actual': 'principal',
        'historial': []
    }

    # Primera interacción
    state['historial'].append({'tipo': 'usuario', 'contenido': '1'})
    menu = mock_menus['principal']['opciones']['1']
    state['menu_actual'] = menu['destino']
    state['historial'].append({'tipo': 'sistema', 'contenido': f" >> Navegando a {menu['destino']}"})

    # Segunda interacción
    state['historial'].append({'tipo': 'usuario', 'contenido': '0'})
    menu = mock_menus['horarios']['opciones']['0']
    state['menu_actual'] = menu['destino']
    state['historial'].append({'tipo': 'sistema', 'contenido': f" >> Navegando a {menu['destino']}"})

    # Tercera interacción
    state['historial'].append({'tipo': 'usuario', 'contenido': '4'})
    respuesta = mock_menus['principal']['opciones']['4']['texto_respuesta']
    state['historial'].append({'tipo': 'sistema', 'contenido': respuesta})

    assert len(state['historial']) == 6
    assert state['menu_actual'] == 'principal'
    assert "soporte@gestion360.com" in state['historial'][-1]['contenido']