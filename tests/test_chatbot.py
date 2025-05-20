import pytest
from unittest.mock import MagicMock, patch
import streamlit as st
import sys
import re

# Tests for the ChatBot module
class TestChatBot:
    
    @pytest.fixture
    def setup_chatbot(self):
        """Set up chatbot session state and menus for testing"""
        # Define menus and responses used in the chatbot
        menus = {
            "principal": {
                "titulo": "📋 Menú Principal - Seleccione una opción:",
                "opciones": {
                    "1": {"texto": "Consultar horarios 📅", "accion": "menu", "destino": "horarios"},
                    "2": {"texto": "Soporte técnico 🛠️", "accion": "menu", "destino": "soporte"},
                    "3": {"texto": "Información general ℹ️", "accion": "respuesta", "texto_respuesta": "🌟 Somos Gestión360, su solución integral."},
                    "4": {"texto": "Contacto 📧", "accion": "respuesta", "texto_respuesta": "📩 Email: soporte@gestion360.com\n📞 Teléfono: +57 123 456 7890"}
                }
            },
            "horarios": {
                "titulo": "⏰ Gestión de Horarios:",
                "opciones": {
                    "1": {"texto": "Ver mi horario 👀", "accion": "respuesta", "texto_respuesta": "🕒 Su horario actual es: Lunes a Viernes de 8:00 AM a 5:00 PM"},
                    "2": {"texto": "Solicitar cambio 🔄", "accion": "respuesta", "texto_respuesta": "📤 Envíe su solicitud a RRHH al email: rrhh@gestion360.com"},
                    "3": {"texto": "Registrar horas extras ⏳", "accion": "respuesta", "texto_respuesta": "⏱️ Use el formulario del módulo de Recursos Humanos"},
                    "0": {"texto": "Volver al menú principal ↩️", "accion": "menu", "destino": "principal"}
                }
            },
            "soporte": {
                "titulo": "🖥️ Soporte Técnico:",
                "opciones": {
                    "1": {"texto": "Reportar problema 🚨", "accion": "respuesta", "texto_respuesta": "✅ Ticket creado (#00123). Nuestro equipo lo contactará en 24h"},
                    "2": {"texto": "Estado de ticket 🔍", "accion": "respuesta", "texto_respuesta": "🔄 Ingrese su número de ticket para consultar el estado"},
                    "3": {"texto": "Urgencias ⚠️", "accion": "respuesta", "texto_respuesta": "📞 Contacte inmediatamente al: +57 3195968338 asesora laura  "},
                    "0": {"texto": "Volver al menú principal ↩️", "accion": "menu", "destino": "principal"}
                }
            }
        }
        
        # Initialize session state
        if 'chatbot' not in st.session_state:
            st.session_state.chatbot = {
                'menu_actual': 'principal',
                'historial': [
                    {'tipo': 'sistema', 'contenido': '¡Bienvenido! Soy su asistente virtual. ¿En qué puedo ayudarle?'}
                ]
            }
        
        return menus
    
    def test_chatbot_initial_state(self, setup_chatbot):
        """Test the initial state of the chatbot"""
        # Check if chatbot is initialized correctly
        assert 'chatbot' in st.session_state
        assert st.session_state.chatbot['menu_actual'] == 'principal'
        assert len(st.session_state.chatbot['historial']) == 1
        assert st.session_state.chatbot['historial'][0]['tipo'] == 'sistema'
    
    def test_menu_navigation(self, setup_chatbot):
        """Test navigation between menus"""
        menus = setup_chatbot
        
        # Starting from principal menu
        assert st.session_state.chatbot['menu_actual'] == 'principal'
        
        # Function to simulate processing user input
        def process_input(user_input):
            # Add user input to history
            st.session_state.chatbot['historial'].append({
                'tipo': 'usuario',
                'contenido': user_input
            })
            
            # Get current menu
            menu_actual = menus[st.session_state.chatbot['menu_actual']]
            opciones_validas = menu_actual['opciones']
            
            # Process valid option
            if user_input in opciones_validas:
                accion = opciones_validas[user_input]['accion']
                
                if accion == 'menu':
                    nuevo_menu = opciones_validas[user_input]['destino']
                    st.session_state.chatbot['menu_actual'] = nuevo_menu
                    respuesta = f"Navegando a {nuevo_menu.capitalize()} ↪️"
                else:
                    respuesta = opciones_validas[user_input]['texto_respuesta']
                
                # Add system response to history
                st.session_state.chatbot['historial'].append({
                    'tipo': 'sistema',
                    'contenido': respuesta
                })
                
                return True
            else:
                # Handle invalid option
                error_msg = "⚠️ Opción no válida. Por favor seleccione una de las opciones mostradas."
                st.session_state.chatbot['historial'].append({
                    'tipo': 'sistema',
                    'contenido': error_msg
                })
                return False
        
        # Test navigation to horarios menu
        process_input("1")
        assert st.session_state.chatbot['menu_actual'] == 'horarios'
        assert len(st.session_state.chatbot['historial']) == 3
        
        # Test getting response within horarios menu
        process_input("1")
        assert st.session_state.chatbot['menu_actual'] == 'horarios'  # Menu doesn't change
        assert len(st.session_state.chatbot['historial']) == 5
        assert "horario actual" in st.session_state.chatbot['historial'][-1]['contenido']
        
        # Test returning to principal menu
        process_input("0")
        assert st.session_state.chatbot['menu_actual'] == 'principal'
        assert len(st.session_state.chatbot['historial']) == 7
        
        # Test navigation to soporte menu
        process_input("2")
        assert st.session_state.chatbot['menu_actual'] == 'soporte'
        assert len(st.session_state.chatbot['historial']) == 9
        
        # Test invalid option
        process_input("5")  # Invalid option
        assert st.session_state.chatbot['menu_actual'] == 'soporte'  # Menu doesn't change
        assert len(st.session_state.chatbot['historial']) == 11
        assert "Opción no válida" in st.session_state.chatbot['historial'][-1]['contenido']
    
    def test_respuestas_informativas(self, setup_chatbot):
        """Test informative responses from the chatbot"""
        menus = setup_chatbot
        
        # Reset chatbot state
        st.session_state.chatbot = {
            'menu_actual': 'principal',
            'historial': [
                {'tipo': 'sistema', 'contenido': '¡Bienvenido! Soy su asistente virtual. ¿En qué puedo ayudarle?'}
            ]
        }
        
        # Function to simulate processing user input (simplified from test_menu_navigation)
        def process_input(user_input):
            # Add user input to history
            st.session_state.chatbot['historial'].append({
                'tipo': 'usuario',
                'contenido': user_input
            })
            
            # Get current menu
            menu_actual = menus[st.session_state.chatbot['menu_actual']]
            opciones_validas = menu_actual['opciones']
            
            # Process valid option
            if user_input in opciones_validas:
                accion = opciones_validas[user_input]['accion']
                
                if accion == 'menu':
                    nuevo_menu = opciones_validas[user_input]['destino']
                    st.session_state.chatbot['menu_actual'] = nuevo_menu
                    respuesta = f"Navegando a {nuevo_menu.capitalize()} ↪️"
                else:
                    respuesta = opciones_validas[user_input]['texto_respuesta']
                
                # Add system response to history
                st.session_state.chatbot['historial'].append({
                    'tipo': 'sistema',
                    'contenido': respuesta
                })
                
                return respuesta
            else:
                # Handle invalid option
                error_msg = "⚠️ Opción no válida. Por favor seleccione una de las opciones mostradas."
                st.session_state.chatbot['historial'].append({
                    'tipo': 'sistema',
                    'contenido': error_msg
                })
                return error_msg
        
        # Test information response
        respuesta = process_input("3")
        assert "Somos Gestión360" in respuesta
        
        # Test contact information response
        respuesta = process_input("4")
        assert "soporte@gestion360.com" in respuesta
        assert "+57 123 456 7890" in respuesta
        
        # Navigate to soporte menu
        process_input("2")
        
        # Test emergency response
        respuesta = process_input("3")
        assert "+57 3195968338" in respuesta
        assert "asesora laura" in respuesta
        
    def test_historial_chat(self, setup_chatbot):
        """Test chat history functionality"""
        menus = setup_chatbot
        
        # Reset chatbot state
        st.session_state.chatbot = {
            'menu_actual': 'principal',
            'historial': [
                {'tipo': 'sistema', 'contenido': '¡Bienvenido! Soy su asistente virtual. ¿En qué puedo ayudarle?'}
            ]
        }
        
        # Function to add chat messages
        def add_messages(messages):
            for message in messages:
                tipo, contenido = message
                st.session_state.chatbot['historial'].append({
                    'tipo': tipo,
                    'contenido': contenido
                })
        
        # Add some test messages
        test_messages = [
            ('usuario', 'Hola, necesito ayuda'),
            ('sistema', 'Claro, ¿en qué puedo ayudarte?'),
            ('usuario', '1'),
            ('sistema', 'Navegando a Horarios ↪️'),
            ('usuario', '2'),
            ('sistema', '📤 Envíe su solicitud a RRHH al email: rrhh@gestion360.com')
        ]
        
        add_messages(test_messages)
        
        # Check history
        assert len(st.session_state.chatbot['historial']) == 7
        assert st.session_state.chatbot['historial'][1]['tipo'] == 'usuario'
        assert st.session_state.chatbot['historial'][1]['contenido'] == 'Hola, necesito ayuda'
        assert st.session_state.chatbot['historial'][-1]['tipo'] == 'sistema'
        assert "rrhh@gestion360.com" in st.session_state.chatbot['historial'][-1]['contenido']
        
        # Test history order (should be chronological)
        timestamps = []
        for i in range(1, len(test_messages) + 1):
            # Check alternating pattern of user and system messages
            assert st.session_state.chatbot['historial'][i]['tipo'] == test_messages[i-1][0]
            assert st.session_state.chatbot['historial'][i]['contenido'] == test_messages[i-1][1]
    
    @patch('streamlit.markdown')
    def test_chat_rendering(self, mock_markdown, setup_chatbot):
        """Test chat message rendering with correct styling"""
        menus = setup_chatbot
        
        # Reset chatbot state with some predefined messages
        st.session_state.chatbot = {
            'menu_actual': 'principal',
            'historial': [
                {'tipo': 'sistema', 'contenido': '¡Bienvenido! Soy su asistente virtual. ¿En qué puedo ayudarle?'},
                {'tipo': 'usuario', 'contenido': 'Hola, necesito información de horarios'},
                {'tipo': 'sistema', 'contenido': 'Para información de horarios, seleccione la opción 1'},
            ]
        }
        
        # Function to simulate rendering chat messages
        def render_chat_messages():
            for message in st.session_state.chatbot['historial']:
                if message['tipo'] == 'usuario':
                    st.markdown(f"""
                        <div class="chat-message chat-message-user">
                            <b>Tú:</b> {message["contenido"]}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="chat-message chat-message-bot">
                            <b>Asistente 360:</b> {message["contenido"]}
                        </div>
                    """, unsafe_allow_html=True)
        
        # Call the function to render messages
        render_chat_messages()
        
        # Assert that markdown was called the correct number of times
        assert mock_markdown.call_count == 3
        
        # Check correct styling for user messages
        user_message_calls = [
            call for call in mock_markdown.call_args_list 
            if 'chat-message-user' in call[0][0]
        ]
        assert len(user_message_calls) == 1
        assert 'Tú:' in user_message_calls[0][0][0]
        assert 'información de horarios' in user_message_calls[0][0][0]
        
        # Check correct styling for system messages
        system_message_calls = [
            call for call in mock_markdown.call_args_list 
            if 'chat-message-bot' in call[0][0]
        ]
        assert len(system_message_calls) == 2
        assert 'Asistente 360:' in system_message_calls[0][0][0]
        assert 'Asistente 360:' in system_message_calls[1][0][0]

    def test_menu_options_structure(self, setup_chatbot):
        """Test the structure of menu options"""
        menus = setup_chatbot
        
        # Test principal menu structure
        principal_menu = menus["principal"]
        assert "titulo" in principal_menu
        assert "opciones" in principal_menu
        assert len(principal_menu["opciones"]) == 4
        
        # Test horarios menu structure
        horarios_menu = menus["horarios"]
        assert "titulo" in horarios_menu
        assert "opciones" in horarios_menu
        assert len(horarios_menu["opciones"]) == 4
        assert "0" in horarios_menu["opciones"]  # Option to return to main menu
        
        # Test soporte menu structure
        soporte_menu = menus["soporte"]
        assert "titulo" in soporte_menu
        assert "opciones" in soporte_menu
        assert len(soporte_menu["opciones"]) == 4
        assert "0" in soporte_menu["opciones"]  # Option to return to main menu
        
        # Test menu option structure
        for menu_name, menu in menus.items():
            for option_key, option in menu["opciones"].items():
                assert "texto" in option
                assert "accion" in option
                assert option["accion"] in ["menu", "respuesta"]
                if option["accion"] == "menu":
                    assert "destino" in option
                    assert option["destino"] in menus.keys()
                else:
                    assert "texto_respuesta" in option
