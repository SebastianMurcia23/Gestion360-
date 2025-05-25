import streamlit as st
import pandas as pd
from reconocimiento_facial import ReconocimientoFacial
from MySql import BaseDeDatos
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import base64
import sentry_sdk

# Configura Sentry (¡primero que todo!)
sentry_sdk.init(
    dsn="https://c2bc2f3344df5e541b137b53b6a834f0@o4509385850093568.ingest.us.sentry.io/4509385880829952",
    send_default_pii=True,
    traces_sample_rate=1.0
)
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
        .card {
            background-color: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card-title {
            color: #ff6347;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .status-active {
            background-color: #d4edda;
            color: #155724;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
        }
        .status-inactive {
            background-color: #f8d7da;
            color: #721c24;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
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
                        st.session_state.num_doc = num_doc
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
        pestaña = st.sidebar.radio("Módulos", ["Reconocimiento Facial", "ChatBot", "Nómina", "Registro de Turnos"])

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

        # --- Módulos ---
        if pestaña == "Reconocimiento Facial":
            menu = st.sidebar.radio("Seleccione una opción", ["Registrar usuario", "Verificar Registro", "Mostrar todos los usuarios"])

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

            elif menu == "Verificar Registro":
                st.subheader("Verificación de Usuario")
                if st.button("🔍 Verificar Rostro"):
                    reconocimiento = ReconocimientoFacial()
                    nombre, num_doc, rol = reconocimiento.verificar_usuario(bd)
                    if nombre:
                        st.success(f"Bienvenido {nombre}, documento: {num_doc}")
                    else:
                        st.error("Usuario no válido.")
                        
            elif menu == "Mostrar todos los usuarios":
                st.subheader("Gestión de Usuarios")
                
                # Estilos adicionales para la gestión de usuarios
                st.markdown("""
                    <style>
                        .user-action-btn {
                            background-color: #ff6347;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 5px;
                            cursor: pointer;
                            margin-right: 5px;
                        }
                        .delete-btn {
                            background-color: #dc3545;
                        }
                        .edit-form {
                            background-color: #f8f9fa;
                            padding: 15px;
                            border-radius: 10px;
                            margin-top: 20px;
                            border: 1px solid #dee2e6;
                        }
                        .confirmation-box {
                            background-color: #fff3cd;
                            padding: 10px;
                            border-radius: 5px;
                            border: 1px solid #ffeeba;
                            margin: 10px 0;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                # Obtener todos los usuarios
                usuarios = bd.obtener_todos_usuarios()
                
                if not usuarios:
                    st.info("No hay usuarios registrados en el sistema.")
                else:
                    # Convertir a DataFrame y mostrar tabla
                    import pandas as pd
                    
                    # Crear DataFrame
                    df = pd.DataFrame(usuarios, columns=["ID", "Nombre", "Tipo Documento", "Número Documento", "Rol"])
                    
                    # Mostrar tabla con usuarios
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-title">Usuarios Registrados</div>', unsafe_allow_html=True)
                    st.dataframe(df, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Sección para editar/eliminar usuario
                    st.markdown('### Editar o Eliminar Usuario')
                    
                    # Seleccionar usuario
                    usuario_ids = {f"{usuario[1]} ({usuario[3]})": usuario[0] for usuario in usuarios}
                    selected_user = st.selectbox("Seleccione un usuario:", list(usuario_ids.keys()))
                    
                    if selected_user:
                        user_id = usuario_ids[selected_user]
                        usuario = bd.obtener_usuario_por_id(user_id)
                        
                        if usuario:
                            st.markdown('<div class="edit-form">', unsafe_allow_html=True)
                            tabs = st.tabs(["Editar Usuario", "Eliminar Usuario"])
                            
                            # Pestaña de edición
                            with tabs[0]:
                                with st.form(key="edit_user_form"):
                                    st.markdown("#### Datos del Usuario")
                                    nombre = st.text_input("Nombre", value=usuario[1])
                                    tipo_doc = st.selectbox("Tipo de Documento", 
                                                        ["Cédula", "Tarjeta de Identidad"], 
                                                        index=0 if usuario[2] == "Cédula" else 1)
                                    num_doc = st.text_input("Número de Documento", value=usuario[3])
                                    rol = st.selectbox("Rol", ["usuario", "administrador"], 
                                                    index=0 if usuario[4] == "usuario" else 1)
                                    
                                    submit_button = st.form_submit_button("Actualizar Usuario")
                                        
                                    if submit_button:
                                        if bd.actualizar_usuario(user_id, nombre, tipo_doc, num_doc, rol):
                                            st.success(f"Usuario {nombre} actualizado correctamente")
                                            st.rerun()
                                        else:
                                            st.error("Error al actualizar el usuario")
                            
                            # Pestaña de eliminación
                            with tabs[1]:
                                st.markdown("#### Eliminar Usuario")
                                st.warning(f"¿Está seguro que desea eliminar al usuario **{usuario[1]}**?")
                                st.markdown('<div class="confirmation-box">', unsafe_allow_html=True)
                                st.markdown("""
                                **IMPORTANTE**: 
                                - Esta acción no se puede deshacer.
                                - Si el usuario tiene registros de turnos asociados, no podrá ser eliminado.
                                """)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                confirmar = st.checkbox("Confirmar eliminación")
                                
                                if st.button("🗑️ Eliminar Usuario", type="primary", disabled=not confirmar):
                                    if confirmar:
                                        resultado = bd.eliminar_usuario(user_id)
                                        if resultado is True:
                                            st.success(f"Usuario {usuario[1]} eliminado correctamente")
                                            st.rerun()
                                        else:
                                            st.error(f"No se pudo eliminar el usuario: {resultado}")
                                    else:
                                        st.warning("Por favor confirme la eliminación marcando la casilla")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                    # Opción para actualizar reconocimiento facial
                    with st.expander("Actualizar reconocimiento facial"):
                        st.write("""
                        Si desea actualizar la imagen facial de un usuario existente,
                        seleccione el usuario y capture un nuevo rostro:
                        """)
                        
                        selected_user_update = st.selectbox(
                            "Seleccione un usuario para actualizar:", 
                            list(usuario_ids.keys()),
                            key="update_facial_recognition"
                        )
                        
                        if selected_user_update:
                            user_id_update = usuario_ids[selected_user_update]
                            usuario_update = bd.obtener_usuario_por_id(user_id_update)
                            
                            if st.button("📸 Capturar Nuevo Rostro"):
                                reconocimiento = ReconocimientoFacial()
                                encoding = reconocimiento.capturar_rostro("Actualizando reconocimiento facial...")
                                if encoding:
                                    try:
                                        # Actualizar solo el encoding facial manteniendo los demás datos
                                        query = "UPDATE usuarios SET encoding = %s WHERE id = %s"
                                        bd.cursor.execute(query, (encoding, user_id_update))
                                        bd.conexion.commit()
                                        st.success(f"Reconocimiento facial de {usuario_update[1]} actualizado correctamente.")
                                    except Exception as e:
                                        st.error(f"Error al actualizar el reconocimiento facial: {e}")
                                else:
                                    st.error("No se detectó un rostro válido.")

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
                        "3": {"texto": "Urgencias ⚠️", "accion": "respuesta", "texto_respuesta": "📞 Contacte inmediatamente al: +57 3195968338 asesora laura  "},
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

            # Estilos CSS para el chat - Simplificados para mayor compatibilidad
            st.markdown("""
                <style>
                    .chat-message {
                        padding: 10px;
                        border-radius: 10px;
                        margin-bottom: 10px;
                        display: flex;
                        flex-direction: column;
                        width: 100%;
                    }
                    .chat-message-user {
                        background-color: #e3f2fd;
                        border: 1px solid #c5e1f5;
                        align-self: flex-end;
                        text-align: right;
                    }
                    .chat-message-bot {
                        background-color: #f5f5f5;
                        border: 1px solid #e0e0e0;
                        align-self: flex-start;
                    }
                    .chat-container {
                        margin-bottom: 15px;
                        padding: 10px;
                        border-radius: 5px;
                        border: 1px solid #ddd;
                        background-color: white;
                        overflow-y: auto;
                    }
                    .chat-options {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 10px;
                        margin-top: 15px;
                    }
                    .chat-option {
                        background-color: #ff6347;
                        color: white;
                        padding: 5px 10px;
                        border-radius: 5px;
                        cursor: pointer;
                        display: inline-block;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Contenedor del chat
            chat_container = st.container()
            
            with chat_container:
                # Mostrar historial de chat
                for interaccion in st.session_state.chatbot['historial']:
                    if interaccion['tipo'] == 'usuario':
                        st.markdown(f"""
                            <div class="chat-message chat-message-user">
                                <b>Tú:</b> {interaccion["contenido"]}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="chat-message chat-message-bot">
                                <b>Asistente 360:</b> {interaccion["contenido"]}
                            </div>
                        """, unsafe_allow_html=True)
            
            # Mostrar menú actual
            menu_actual = menus[st.session_state.chatbot['menu_actual']]
            st.markdown(f"<h4>{menu_actual['titulo']}</h4>", unsafe_allow_html=True)
            
            # Mostrar opciones como botones clickeables
            st.markdown('<div class="chat-options">', unsafe_allow_html=True)
            for opcion, detalle in menu_actual['opciones'].items():
                st.markdown(f"""
                    <div class="chat-option" onclick="document.getElementById('chat-input').value='{opcion}'; document.getElementById('chat-form-submit').click();">
                        {opcion}. {detalle['texto']}
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Formulario de entrada
            with st.form("chat_form", clear_on_submit=True):
                st.markdown('<div style="display: flex; gap: 10px;">', unsafe_allow_html=True)
                user_input = st.text_input("Seleccione una opción:", key="chat_input", 
                                            placeholder="Escriba el número o use los botones...",
                                            label_visibility="collapsed")
                enviado = st.form_submit_button("Enviar", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Script para permitir que los botones de opciones funcionen
                st.markdown("""
                    <script>
                        // Agregar atributos id para hacer el formulario interactivo
                        const inputs = window.parent.document.querySelectorAll('input[aria-label="Escriba el número o use los botones..."]');
                        if (inputs.length > 0) {
                            inputs[0].id = 'chat-input';
                        }
                        const buttons = window.parent.document.querySelectorAll('button[kind="primaryFormSubmit"]');
                        if (buttons.length > 0) {
                            buttons[0].id = 'chat-form-submit';
                        }
                    </script>
                """, unsafe_allow_html=True)
                
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
                            respuesta = f"Navegando a {nuevo_menu.capitalize()} ↪️"
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
                    
                    # Recargar para mostrar la nueva interacción
                    st.rerun()

        elif pestaña == "Nómina":
            st.subheader("Nómina")
            
            # Estilos CSS adicionales para la nómina
            st.markdown("""
                <style>
                    .nomina-card {
                        background-color: #f9f9f9;
                        border-radius: 10px;
                        padding: 20px;
                        margin-bottom: 20px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }
                    .nomina-header {
                        background-color: #ff6347;
                        color: white;
                        padding: 10px 15px;
                        border-radius: 5px 5px 0 0;
                        font-weight: bold;
                        margin-bottom: 15px;
                    }
                    .nomina-footer {
                        background-color: #f5f5f5;
                        padding: 10px 15px;
                        border-radius: 0 0 5px 5px;
                        font-weight: bold;
                        border-top: 1px solid #ddd;
                        margin-top: 15px;
                    }
                    .nomina-row {
                        display: flex;
                        justify-content: space-between;
                        padding: 8px 0;
                        border-bottom: 1px solid #eee;
                    }
                    .nomina-section-title {
                        background-color: #f0f0f0;
                        padding: 5px 10px;
                        margin: 10px 0;
                        border-left: 4px solid #ff6347;
                    }
                    .badge-primary {
                        background-color: #007bff;
                        color: white;
                        padding: 3px 10px;
                        border-radius: 10px;
                        font-size: 0.8em;
                    }
                    .badge-success {
                        background-color: #28a745;
                        color: white;
                        padding: 3px 10px;
                        border-radius: 10px;
                        font-size: 0.8em;
                    }
                    .badge-danger {
                        background-color: #dc3545;
                        color: white;
                        padding: 3px 10px;
                        border-radius: 10px;
                        font-size: 0.8em;
                    }
                    .badge-info {
                        background-color: #17a2b8;
                        color: white;
                        padding: 3px 10px;
                        border-radius: 10px;
                        font-size: 0.8em;
                    }
                    .nomina-total {
                        font-weight: bold;
                        font-size: 1.2em;
                        color: #28a745;
                    }
                    .nomina-filter {
                        background-color: white;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                        border: 1px solid #eee;
                    }
                    .btn-generate {
                        background-color: #ff6347;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 5px;
                        border: none;
                        cursor: pointer;
                        font-weight: bold;
                        transition: all 0.3s;
                    }
                    .btn-generate:hover {
                        background-color: #ff4500;
                        transform: translateY(-2px);
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Añadir función a la clase BaseDeDatos para calcular turnos y nómina
            if not hasattr(bd, 'calcular_nomina_usuario'):
                # Funciones auxiliares para la nómina
                def calcular_nomina_usuario(self, num_doc, fecha_inicio, fecha_fin, valor_hora=10000):
                    """Calcula la nómina para un usuario en un período específico"""
                    try:
                        # Obtenemos los turnos del usuario en el período seleccionado
                        query = """
                        SELECT hora_entrada, hora_salida, duracion 
                        FROM registro_turnos 
                        WHERE numero_documento = %s 
                        AND hora_entrada BETWEEN %s AND %s
                        AND hora_salida IS NOT NULL
                        ORDER BY hora_entrada DESC
                        """
                        self.cursor.execute(query, (num_doc, fecha_inicio, fecha_fin))
                        turnos = self.cursor.fetchall()
                        
                        # Información del usuario
                        query_usuario = "SELECT nombre, tipo_documento FROM usuarios WHERE numero_documento = %s"
                        self.cursor.execute(query_usuario, (num_doc,))
                        info_usuario = self.cursor.fetchone()
                        
                        if not info_usuario:
                            return None
                        
                        nombre_usuario, tipo_doc = info_usuario
                        
                        # Datos para la nómina
                        total_horas = 0
                        detalles_turnos = []
                        
                        for entrada, salida, duracion in turnos:
                            # Convertir a datetime si no lo son ya
                            if isinstance(entrada, str):
                                entrada_dt = datetime.strptime(entrada, '%Y-%m-%d %H:%M:%S')
                            else:
                                entrada_dt = entrada
                                
                            if isinstance(salida, str):
                                salida_dt = datetime.strptime(salida, '%Y-%m-%d %H:%M:%S')
                            else:
                                salida_dt = salida
                            
                            # Calcular horas trabajadas
                            diff = salida_dt - entrada_dt
                            horas = diff.total_seconds() / 3600  # Convertir segundos a horas
                            total_horas += horas
                            
                            detalles_turnos.append({
                                'fecha': entrada_dt.strftime('%Y-%m-%d'),
                                'entrada': entrada_dt.strftime('%H:%M'),
                                'salida': salida_dt.strftime('%H:%M'),
                                'horas': round(horas, 2),
                                'valor': int(horas * valor_hora)
                            })
                        
                        # Calcular totales
                        subtotal = total_horas * valor_hora
                        salud = subtotal * 0.04  # 4% para salud
                        pension = subtotal * 0.04  # 4% para pensión
                        recargos_nocturnos = valor_hora / 0.35 # 35% para los recargos nocturnos despues de las 9pm
                        total = subtotal - salud - pension
                        
                        return {
                            'nombre': nombre_usuario,
                            'documento': f"{tipo_doc}: {num_doc}",
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
                    except Exception as e:
                        print(f"Error al calcular nómina: {e}")
                        return None
                
                def obtener_usuarios_para_nomina(self):
                    """Obtiene la lista de usuarios que tienen registros de turnos"""
                    try:
                        query = """
                        SELECT DISTINCT u.numero_documento, u.nombre 
                        FROM usuarios u
                        INNER JOIN registro_turnos t ON u.numero_documento = t.numero_documento
                        WHERE t.hora_salida IS NOT NULL
                        ORDER BY u.nombre
                        """
                        self.cursor.execute(query)
                        return self.cursor.fetchall()
                    except Exception as e:
                        print(f"Error al obtener usuarios para nómina: {e}")
                        return []
                        
                def guardar_nomina(self, datos_nomina):
                    """Guarda un registro de nómina en la base de datos"""
                    try:
                        # Crear tabla si no existe
                        self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS nominas (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            numero_documento VARCHAR(50),
                            nombre_usuario VARCHAR(100),
                            fecha_inicio DATE,
                            fecha_fin DATE,
                            total_horas FLOAT,
                            valor_hora INT,
                            subtotal INT,
                            descuento_salud INT,
                            descuento_pension INT,
                            total INT,
                            fecha_generacion DATETIME,
                            FOREIGN KEY (numero_documento) REFERENCES usuarios(numero_documento)
                        )
                        """)
                        self.conexion.commit()
                        
                        # Insertar registro
                        query = """
                        INSERT INTO nominas (
                            numero_documento, nombre_usuario, fecha_inicio, fecha_fin,
                            total_horas, valor_hora, subtotal, descuento_salud,
                            descuento_pension, total, fecha_generacion
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        values = (
                            datos_nomina['documento'].split(': ')[1],
                            datos_nomina['nombre'],
                            datos_nomina['periodo'].split(' al ')[0],
                            datos_nomina['periodo'].split(' al ')[1],
                            datos_nomina['total_horas'],
                            datos_nomina['valor_hora'],
                            datos_nomina['subtotal'],
                            datos_nomina['salud'],
                            datos_nomina['pension'],
                            datos_nomina['total'],
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        )
                        
                        self.cursor.execute(query, values)
                        self.conexion.commit()
                        return self.cursor.lastrowid
                    except Exception as e:
                        print(f"Error al guardar nómina: {e}")
                        return None
                        
                def obtener_nominas(self):
                    """Obtiene todas las nóminas generadas"""
                    try:
                        query = """
                        SELECT id, nombre_usuario, numero_documento, 
                            fecha_inicio, fecha_fin, total_horas, 
                            valor_hora, total, fecha_generacion
                        FROM nominas
                        ORDER BY fecha_generacion DESC
                        """
                        self.cursor.execute(query)
                        return self.cursor.fetchall()
                    except Exception as e:
                        print(f"Error al obtener nóminas: {e}")
                        return []
                
                # Añadir los métodos a la clase
                setattr(BaseDeDatos, 'calcular_nomina_usuario', calcular_nomina_usuario)
                setattr(BaseDeDatos, 'obtener_usuarios_para_nomina', obtener_usuarios_para_nomina)
                setattr(BaseDeDatos, 'guardar_nomina', guardar_nomina)
                setattr(BaseDeDatos, 'obtener_nominas', obtener_nominas)
            
            # Interfaz de usuario para la nómina
            tabs = st.tabs(["Generar Nómina", "Historial"])
            
            with tabs[0]:
                st.markdown('<div class="nomina-filter">', unsafe_allow_html=True)
                st.subheader("Generar Desprendible de Nómina")
                
                # Obtener usuarios que tienen registros de turnos
                usuarios_nomina = bd.obtener_usuarios_para_nomina()
                
                if not usuarios_nomina:
                    st.info("No hay usuarios con turnos registrados para generar nómina.")
                else:
                    # Formulario para generar nómina
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Crear opciones para el selectbox
                        opciones_usuario = {f"{nombre} ({num_doc})": num_doc for num_doc, nombre in usuarios_nomina}
                        usuario_seleccionado = st.selectbox(
                            "Seleccione un empleado:",
                            options=list(opciones_usuario.keys())
                        )
                        
                        valor_hora = st.number_input(
                            "Valor por hora (COP):",
                            min_value=5000,
                            value=10000,
                            step=1000,
                            help="Valor a pagar por cada hora trabajada"
                        )
                    
                    with col2:
                        # Fechas para filtrar los turnos
                        fecha_inicio = st.date_input(
                            "Fecha de inicio:",
                            value=datetime.now().replace(day=1),  # Primer día del mes actual
                            help="Fecha de inicio del período de liquidación"
                        )
                        
                        fecha_fin = st.date_input(
                            "Fecha de fin:",
                            value=datetime.now(),  # Día actual
                            help="Fecha final del período de liquidación"
                        )
                    
                    # Botón para generar nómina
                    if st.button("Generar Nómina", type="primary"):
                        if usuario_seleccionado:
                            num_doc = opciones_usuario[usuario_seleccionado]
                            
                            # Convertir fechas a formato string para la consulta SQL
                            fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
                            fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
                            
                            with st.spinner("Calculando nómina..."):
                                # Calcular nómina
                                nomina = bd.calcular_nomina_usuario(
                                    num_doc, 
                                    fecha_inicio_str, 
                                    fecha_fin_str, 
                                    valor_hora
                                )
                                
                                if nomina and nomina['turnos']:
                                    # Guardar la nómina en la base de datos
                                    id_nomina = bd.guardar_nomina(nomina)
                                    
                                    # Mostrar desprendible
                                    st.success(f"Nómina generada correctamente. ID: {id_nomina}")
                                    
                                    # Desprendible de nómina detallado
                                    st.markdown('<div class="nomina-card">', unsafe_allow_html=True)
                                    
                                    # Cabecera
                                    st.markdown(f"""
                                    <div class="nomina-header">
                                        <h3>DESPRENDIBLE DE PAGO</h3>
                                        <p>Periodo: {nomina['periodo']}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Datos del empleado
                                    st.markdown("<div class='nomina-section-title'>Información del Empleado</div>", unsafe_allow_html=True)
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"**Nombre:** {nomina['nombre']}")
                                    with col2:
                                        st.markdown(f"**Documento:** {nomina['documento']}")
                                    
                                    # Detalles de turnos
                                    st.markdown("<div class='nomina-section-title'>Detalle de Turnos</div>", unsafe_allow_html=True)
                                    
                                    # Crear DataFrame para la tabla de turnos
                                    df_turnos = pd.DataFrame(nomina['turnos'])
                                    df_turnos.columns = ['Fecha', 'Entrada', 'Salida', 'Horas', 'Valor (COP)']
                                    
                                    # Formatear valores monetarios
                                    df_turnos['Valor (COP)'] = df_turnos['Valor (COP)'].apply(lambda x: f"${x:,.0f}")
                                    
                                    st.dataframe(df_turnos, use_container_width=True)
                                    
                                    # Resumen de pago
                                    st.markdown("<div class='nomina-section-title'>Resumen de Pago</div>", unsafe_allow_html=True)
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown(f"""
                                        <div class="nomina-row">
                                            <span>Total Horas:</span>
                                            <span><span class="badge-primary">{nomina['total_horas']}</span></span>
                                        </div>
                                        <div class="nomina-row">
                                            <span>Valor por Hora:</span>
                                            <span>${nomina['valor_hora']:,.0f}</span>
                                        </div>
                                        <div class="nomina-row">
                                            <span>Subtotal:</span>
                                            <span>${nomina['subtotal']:,.0f}</span>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                    with col2:
                                        st.markdown(f"""
                                        <div class="nomina-row">
                                            <span>Descuento Salud (4%):</span>
                                            <span><span class="badge-danger">-${nomina['salud']:,.0f}</span></span>
                                        </div>
                                        <div class="nomina-row">
                                            <span>Descuento Pensión (4%):</span>
                                            <span><span class="badge-danger">-${nomina['pension']:,.0f}</span></span>
                                        </div>
                                        <div class="nomina-row">
                                            <span>Total a Pagar:</span>
                                            <span class="nomina-total">${nomina['total']:,.0f}</span>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    # Pie de página
                                    st.markdown(f"""
                                    <div class="nomina-footer">
                                        <p>Generado por: Sistema Gestión360 - Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # Opción para descargar como PDF (simulado)
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        def generar_pdf_nomina(nomina):
                                            """Genera un PDF real con los datos de la nómina"""
                                            # Crear un buffer en memoria para el PDF
                                            buffer = BytesIO()
                                            
                                            # Crear el documento PDF
                                            doc = SimpleDocTemplate(buffer, pagesize=letter, 
                                                                rightMargin=72, leftMargin=72,
                                                                topMargin=72, bottomMargin=18)
                                            
                                            # Estilos para el documento
                                            styles = getSampleStyleSheet()
                                            styles.add(ParagraphStyle(name='Centered', alignment=TA_CENTER, fontSize=14, fontName='Helvetica-Bold'))
                                            styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
                                            
                                            # Contenido del documento
                                            contenido = []
                                            
                                            # Título
                                            titulo = Paragraph("<font size=16>DESPRENDIBLE DE PAGO</font>", styles["Centered"])
                                            contenido.append(titulo)
                                            contenido.append(Spacer(1, 12))
                                            
                                            # Período
                                            periodo = Paragraph(f"<b>Período:</b> {nomina['periodo']}", styles["Centered"])
                                            contenido.append(periodo)
                                            contenido.append(Spacer(1, 20))
                                            
                                            # Información del empleado
                                            contenido.append(Paragraph("<b>Información del Empleado</b>", styles["Heading2"]))
                                            contenido.append(Spacer(1, 6))
                                            
                                            info_empleado = [
                                                [Paragraph("<b>Nombre:</b>", styles["Normal"]), nomina['nombre']],
                                                [Paragraph("<b>Documento:</b>", styles["Normal"]), nomina['documento']]
                                            ]
                                            
                                            tabla_info = Table(info_empleado, colWidths=[120, 350])
                                            tabla_info.setStyle(TableStyle([
                                                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                                                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                                                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('PADDING', (0, 0), (-1, -1), 6),
                                            ]))
                                            
                                            contenido.append(tabla_info)
                                            contenido.append(Spacer(1, 20))
                                            
                                            # Detalle de turnos
                                            contenido.append(Paragraph("<b>Detalle de Turnos</b>", styles["Heading2"]))
                                            contenido.append(Spacer(1, 6))
                                            
                                            # Cabecera de la tabla
                                            datos_turnos = [["Fecha", "Entrada", "Salida", "Horas", "Valor (COP)"]]
                                            
                                            # Agregar datos de turnos
                                            for turno in nomina['turnos']:
                                                datos_turnos.append([
                                                    turno['fecha'],
                                                    turno['entrada'],
                                                    turno['salida'],
                                                    str(turno['horas']),
                                                    f"${turno['valor']:,.0f}"
                                                ])
                                            
                                            # Crear tabla de turnos
                                            tabla_turnos = Table(datos_turnos, colWidths=[80, 80, 80, 80, 120])
                                            tabla_turnos.setStyle(TableStyle([
                                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                                                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('PADDING', (0, 0), (-1, -1), 6),
                                            ]))
                                            
                                            contenido.append(tabla_turnos)
                                            contenido.append(Spacer(1, 20))
                                            
                                            # Resumen de pago
                                            contenido.append(Paragraph("<b>Resumen de Pago</b>", styles["Heading2"]))
                                            contenido.append(Spacer(1, 6))
                                            
                                            resumen_pago = [
                                                ["Total Horas:", f"{nomina['total_horas']}"],
                                                ["Valor por Hora:", f"${nomina['valor_hora']:,.0f}"],
                                                ["Subtotal:", f"${nomina['subtotal']:,.0f}"],
                                                ["Descuento Salud (4%):", f"-${nomina['salud']:,.0f}"],
                                                ["Descuento Pensión (4%):", f"-${nomina['pension']:,.0f}"],
                                                ["Total a Pagar:", f"${nomina['total']:,.0f}"]
                                            ]
                                            
                                            tabla_resumen = Table(resumen_pago, colWidths=[200, 200])
                                            tabla_resumen.setStyle(TableStyle([
                                                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                                                ('BACKGROUND', (1, -1), (1, -1), colors.lightgreen),
                                                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                                                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                                ('PADDING', (0, 0), (-1, -1), 6),
                                                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                                            ]))
                                            
                                            contenido.append(tabla_resumen)
                                            contenido.append(Spacer(1, 30))
                                            
                                            # Pie de página
                                            fecha_generacion = datetime.now().strftime('%Y-%m-%d %H:%M')
                                            pie = Paragraph(f"Generado por: Sistema Gestión360 - Fecha: {fecha_generacion}", styles["Normal"])
                                            contenido.append(pie)
                                            
                                            # Construir el PDF
                                            doc.build(contenido)
                                            
                                            # Obtener el valor del PDF generado y codificarlo en base64
                                            pdf = buffer.getvalue()
                                            buffer.close()
                                            
                                            return pdf
                                        pdf_data = generar_pdf_nomina(nomina)
                                        st.download_button(
                                            label="⬇️ Descargar PDF",
                                            data=pdf_data,
                                            file_name=f"nomina_{nomina['nombre']}_{fecha_inicio_str}_{fecha_fin_str}.pdf",
                                            mime="application/pdf"
                                        )
                                    with col2:
                                        st.button("📧 Enviar por correo", disabled=True, 
                                                help="Función de envío por correo no implementada. Requiere configuración adicional.")
                                
                                elif nomina and not nomina['turnos']:
                                    st.warning(f"No se encontraron turnos para {nomina['nombre']} en el período seleccionado.")
                                else:
                                    st.error("No se pudo calcular la nómina. Verifique los datos e intente nuevamente.")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tabs[1]:
                st.subheader("Historial de Nóminas")
                
                # Obtener historial de nóminas
                nominas = bd.obtener_nominas()
                
                if not nominas:
                    st.info("No hay registros de nóminas generadas.")
                else:
                    # Convertir a DataFrame
                    import pandas as pd
                    
                    df_nominas = pd.DataFrame(nominas, columns=[
                        "ID", "Empleado", "Documento", "Fecha Inicio", 
                        "Fecha Fin", "Total Horas", "Valor Hora", 
                        "Total Pagado", "Fecha Generación"
                    ])
                    
                    # Formatear valores monetarios
                    df_nominas["Valor Hora"] = df_nominas["Valor Hora"].apply(lambda x: f"${x:,.0f}")
                    df_nominas["Total Pagado"] = df_nominas["Total Pagado"].apply(lambda x: f"${x:,.0f}")
                    
                    # Mostrar tabla
                    st.dataframe(df_nominas, use_container_width=True)
                    
                    # Añadir botón para exportar a CSV
                    csv = df_nominas.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="📊 Exportar a CSV",
                        data=csv,
                        file_name="historial_nominas.csv",
                        mime="text/csv",
                    )
            
        elif pestaña == "Registro de Turnos":
            st.subheader("Gestión de Turnos")
            
            # Tabla con registros de turnos
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Registros de Turnos</div>', unsafe_allow_html=True)
            
            registros = bd.obtener_registros_turnos()
            if registros:
                # Convertir a DataFrame para mejor visualización
                import pandas as pd
                df = pd.DataFrame(registros, columns=["ID", "Usuario", "Documento", "Entrada", "Salida", "Duración"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay registros de turnos disponibles.")
            
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.rol == 'usuario':
        st.sidebar.title(f"Bienvenid@ {st.session_state.nombre}")
        
        # Verificar si hay un turno activo para el usuario
        tiene_turno_activo = bd.verificar_turno_activo(st.session_state.num_doc)
        
        if tiene_turno_activo:
            # Mostrar información del turno activo
            info_turno = bd.obtener_info_turno_activo(st.session_state.num_doc)
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Turno Activo</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="status-active">✅ En turno</div>', unsafe_allow_html=True)
            
            # Mostrar información
            st.write(f"**Hora de inicio:** {info_turno['hora_inicio']}")
            
            # Calcular tiempo transcurrido
            tiempo_actual = datetime.now()
            tiempo_inicio = datetime.strptime(info_turno['hora_inicio'], "%Y-%m-%d %H:%M:%S")
            tiempo_transcurrido = tiempo_actual - tiempo_inicio
            
            dias = tiempo_transcurrido.days
            horas = tiempo_transcurrido.seconds // 3600
            minutos = (tiempo_transcurrido.seconds % 3600) // 60
            
            if dias > 0:
                st.write(f"**Tiempo transcurrido:** {dias} días, {horas} horas y {minutos} minutos")
            else:
                st.write(f"**Tiempo transcurrido:** {horas} horas y {minutos} minutos")
            
            if st.button("🔚 Cerrar Turno"):
                with st.spinner("Registrando salida..."):
                    bd.registrar_salida(st.session_state.num_doc)
                    st.success("¡Has finalizado tu turno correctamente!")
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Estado de Turno</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="status-inactive">❌ Sin turno activo</div>', unsafe_allow_html=True)
            
            if st.button("🏁 Iniciar Turno"):
                with st.spinner("Registrando entrada..."):
                    bd.registrar_entrada(st.session_state.nombre, st.session_state.num_doc)
                    st.success("¡Turno iniciado correctamente!")
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Historial de turnos del usuario
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Mi Historial de Turnos</div>', unsafe_allow_html=True)
        
        historial = bd.obtener_historial_turnos(st.session_state.num_doc)
        if historial:
            import pandas as pd
            df = pd.DataFrame(historial, columns=["ID", "Entrada", "Salida", "Duración"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No tienes registros de turnos anteriores.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()