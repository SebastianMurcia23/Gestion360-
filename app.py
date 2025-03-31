import streamlit as st
from reconocimiento_facial import ReconocimientoFacial
from MySql import BaseDeDatos

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
        if st.button("Iniciar Sesión"):
            if usuario == "admin" and contraseña == "1234":  
                st.session_state.autenticado = True
                st.success("Acceso concedido")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        st.markdown("</div>", unsafe_allow_html=True)

# --- Menú Principal ---
else:
    # Sidebar accesible desde cualquier pestaña
    st.sidebar.title("Menú Principal")
    pestaña = st.sidebar.radio("Seleccione un módulo", ["Reconocimiento Facial", "Módulo 2", "Módulo 3"])

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

            if st.button("📸 Capturar Rostro"):
                reconocimiento = ReconocimientoFacial()
                encoding = reconocimiento.capturar_rostro("Registrando...")
                if encoding:
                    bd.guardar_usuario(nombre, tipo_doc, num_doc, encoding)
                    st.success(f"Usuario {nombre} registrado correctamente.")
                else:
                    st.error("No se detectó un rostro válido.")

        elif menu == "Ingresar a turno":
            st.subheader("Verificación de Usuario")
            if st.button("🔍 Verificar Rostro"):
                reconocimiento = ReconocimientoFacial()
                nombre, num_doc = reconocimiento.verificar_usuario(bd)
                if nombre:
                    st.success(f"Bienvenido {nombre}, documento: {num_doc}")
                else:
                    st.error("Usuario no válido.")

    elif pestaña == "Módulo 2":
        st.subheader("Módulo 2")
        st.info("Próximamente...")

    elif pestaña == "Módulo 3":
        st.subheader("Módulo 3")
        st.info("Próximamente...")
