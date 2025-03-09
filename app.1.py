import streamlit as st
from reconocimiento_facial import ReconocimientoFacial
from MySql import BaseDeDatos
import cv2
import numpy as np

# Configurar página
st.set_page_config(page_title="Sistema de Reconocimiento Facial", page_icon="😎", layout="centered")

# Agregar CSS personalizado
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

# Inicializar base de datos y reconocimiento facial
bd = BaseDeDatos()
reconocimiento_facial = ReconocimientoFacial()

# Manejo de sesión
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
            if usuario == "admin" and contraseña == "1234":  # ⚠ Validación temporal
                st.session_state.autenticado = True
                st.success("Acceso concedido")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        st.markdown("</div>", unsafe_allow_html=True)

# --- Módulos del sistema ---
else:
    st.sidebar.title("Menú")
    pestañas = st.tabs(["Reconocimiento Facial", "Módulo 2", "Módulo 3"])

    # Módulo de reconocimiento facial
    with pestañas[0]:
        st.subheader("Módulo de Reconocimiento Facial")
        if st.button("🔍 Verificar Rostro"):
            nombre, num_doc = reconocimiento_facial.verificar_usuario(bd)
            if nombre:
                st.success(f"Bienvenido {nombre}, documento: {num_doc}")
            else:
                st.error("Usuario no válido.")
    
    # Módulo 2 (sin funcionalidad aún)
    with pestañas[1]:
        st.subheader("Módulo 2")
        st.info("Próximamente...")
    
    # Módulo 3 (sin funcionalidad aún)
    with pestañas[2]:
        st.subheader("Módulo 3")
        st.info("Próximamente...")
    
    # Opción para cerrar sesión
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
