import streamlit as st
from reconocimiento_facial import ReconocimientoFacial
from MySql import BaseDeDatos
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
from datetime import datetime
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
        pestaña = st.sidebar.radio("Módulos", ["Reconocimiento Facial", "ChatBot", "Módulo 3", "Registro de Turnos"])

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