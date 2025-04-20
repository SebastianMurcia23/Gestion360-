import streamlit as st
from reconocimiento_facial import ReconocimientoFacial
from MySql import BaseDeDatos
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
st.set_page_config(page_title="Gestión360 ", page_icon="😎", layout="centered")

st.markdown("""
    <style>
        .title {
            color: #ffffff;
            background-color: #ff6347;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-size: 30px;
        }
        .login-box {
            background-color: #f5f5f5;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
            width: 400px;
            margin: auto;
            text-align: center;
        }
        .stButton > button {
            background-color: #ff6347;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

bd = BaseDeDatos()
reconocimiento_facial = ReconocimientoFacial()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# --- Pantalla de Login ---
if not st.session_state.autenticado:
    st.markdown('<h1 class="title">Inicio de Sesión</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        usuario = st.text_input("Usuario", key="user_input")
        contraseña = st.text_input("Contraseña", type="password", key="password_input")
        
        # Botones en columnas
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("Iniciar Sesión"):
                if usuario == "admin" and contraseña == "1234":
                    st.session_state.autenticado = True
                    st.session_state.rol = "administrador"
                    st.session_state.nombre = "administrador"
                    st.success("Acceso concedido")
                    st.rerun()
                    
            if st.button("Face Id"):
                with st.spinner('Detectando rostro...'):
                    nombre, num_doc, rol = reconocimiento_facial.verificar_usuario(bd, mostrar_video=False)
                    if nombre:
                        st.session_state.autenticado = True
                        st.session_state.rol = rol
                        st.session_state.nombre = nombre
                        st.success(f"Bienvenido {nombre}, documento: {num_doc}")
                        st.rerun()
                    else:
                        st.error("Usuario no válido o rostro no detectado")

        st.markdown("</div>", unsafe_allow_html=True)

# --- Menú Principal ---
else:
    # Sidebar accesible desde cualquier pestaña
    if st.session_state.rol == 'administrador':
        # Sidebar y módulos 
        st.sidebar.title(f"Bienvenid@ {st.session_state.nombre}")
        pestaña = st.sidebar.radio("Módulos", ["Reconocimiento Facial", "ChatBot", "Módulo 3"])

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

        # --- Módulos ---
        if pestaña == "Reconocimiento Facial":
            menu = st.sidebar.radio("Seleccione una opción", ["Ingresar a turno", "Registrar usuario"])

            if menu == "Registrar usuario":
                st.subheader("Registrar Usuario")
                nombre = st.text_input("Nombre")
                tipo_doc = st.selectbox("Tipo de Documento", ["Cédula", "Tarjeta de Identidad"])
                num_doc = st.text_input("Número de Documento")
                rol = st.selectbox("Rol", ["usuario", "administrador"])

                if st.button("📸 Capturar Rostro"):
                    reconocimiento = ReconocimientoFacial()
                    encoding = reconocimiento.capturar_rostro("Registrando...")
                    if encoding:
                        bd.guardar_usuario(nombre, tipo_doc, num_doc, encoding, rol)
                        st.success(f"Usuario {nombre} registrado correctamente.")
                    else:
                        st.error("No se detectó un rostro válido.")

            elif menu == "Ingresar a turno":
                st.subheader("Verificación de Usuario")
                if st.button("🔍 Verificar Rostro"):
                    reconocimiento = ReconocimientoFacial()
                    nombre, num_doc, rol = reconocimiento.verificar_usuario(bd)
                    if nombre:
                        st.success(f"Bienvenido {nombre}, documento: {num_doc}")
                    else:
                        st.error("Usuario no válido.")

        elif pestaña == "ChatBot":
            st.subheader("Asistente Virtual 360")
            
            # Definición de menús y respuestas
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
                        "3": {"texto": "Urgencias ⚠️", "accion": "respuesta", "texto_respuesta": "📞 Contacte inmediatamente al: +57 987 654 3210"},
                        "0": {"texto": "Volver al menú principal ↩️", "accion": "menu", "destino": "principal"}
                    }
                }
            }

            # Inicializar estado del chatbot
            if 'chatbot' not in st.session_state:
                st.session_state.chatbot = {
                    'menu_actual': 'principal',
                    'historial': [
                        {'tipo': 'sistema', 'contenido': '¡Bienvenido! Soy su asistente virtual. ¿En qué puedo ayudarle?'}
                    ]
                }

            # Estilos CSS para el chat
            st.markdown("""
                <style>
                    .chat-container {
                        background-color: #f9f9f9;
                        border-radius: 10px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .user-message {
                        background-color: #e3f2fd;
                        padding: 10px;
                        border-radius: 10px;
                        margin: 5px 0;
                        max-width: 80%;
                        float: right;
                        clear: both;
                    }
                    .bot-message {
                        background-color: #ffffff;
                        padding: 10px;
                        border-radius: 10px;
                        margin: 5px 0;
                        max-width: 80%;
                        float: left;
                        clear: both;
                        border: 1px solid #eee;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Contenedor del chat con auto-scroll
            with st.container(height=400):
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                
                for interaccion in st.session_state.chatbot['historial']:
                    if interaccion['tipo'] == 'usuario':
                        st.markdown(f'<div class="user-message">Tú: {interaccion["contenido"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="bot-message">Asistente 360: {interaccion["contenido"]}</div>', unsafe_allow_html=True)
                
                st.markdown("""
                    <script>
                        window.parent.document.querySelector('section[data-testid="stVerticalBlock"]').scrollTo(0, 999999);
                    </script>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Mostrar menú actual
            menu_actual = menus[st.session_state.chatbot['menu_actual']]
            st.markdown(f'**{menu_actual["titulo"]}**')
            
            cols = st.columns(2)
            current_col = 0
            for opcion, detalle in menu_actual['opciones'].items():
                with cols[current_col]:
                    st.markdown(f"**{opcion}.** {detalle['texto']}")
                    current_col = (current_col + 1) % 2

            # Manejar entrada de usuario
            with st.form("chat_form", clear_on_submit=True):
                user_input = st.text_input("Escriba el número de la opción:", key="chat_input")
                enviado = st.form_submit_button("Enviar ➤")
                
                if enviado and user_input:
                    # Registrar pregunta del usuario
                    st.session_state.chatbot['historial'].append({
                        'tipo': 'usuario',
                        'contenido': user_input
                    })
                    
                    # Procesar opción seleccionada
                    opciones_validas = menu_actual['opciones']
                    
                    if user_input in opciones_validas:
                        accion = opciones_validas[user_input]['accion']
                        
                        if accion == 'menu':
                            nuevo_menu = opciones_validas[user_input]['destino']
                            st.session_state.chatbot['menu_actual'] = nuevo_menu
                            respuesta = f" >> Navegando a {nuevo_menu.capitalize()}"
                        else:
                            respuesta = opciones_validas[user_input]['texto_respuesta']
                        
                        # Registrar respuesta del sistema
                        st.session_state.chatbot['historial'].append({
                            'tipo': 'sistema',
                            'contenido': respuesta
                        })
                        
                    else:
                        error_msg = "⚠️ Opción no válida. Por favor seleccione una de las opciones mostradas."
                        st.session_state.chatbot['historial'].append({
                            'tipo': 'sistema',
                            'contenido': error_msg
                        })
                    
                    # Limpiar input correctamente
                    if "chat_input" in st.session_state:
                        del st.session_state.chat_input
                    st.rerun()

        elif pestaña == "Módulo 3":
            st.subheader("Módulo 3")
            st.info("Próximamente...")

    if st.session_state.rol == 'usuario':
        st.sidebar.title(f"Bienvenid@ {st.session_state.nombre}")