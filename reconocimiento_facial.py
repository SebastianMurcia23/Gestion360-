import cv2
import face_recognition
import numpy as np
import streamlit as st

class ReconocimientoFacial:
    def __init__(self, camara_source=0):
        self.camara_source = camara_source
        self.cap = None  # Inicializar como None

    def _inicializar_camara(self):
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camara_source)
            if not self.cap.isOpened():
                st.error("Error: Cámara no disponible. Verifica conexión.")
                raise RuntimeError("Cámara no detectada")

    def capturar_rostro(self, mensaje="", mostrar_video=True):
        self._inicializar_camara()
        encoding = None
        frame_placeholder = st.empty() if mostrar_video else None
        stop_button = st.button("Limpiar Captura") if mostrar_video else None
        
        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    st.warning("Problema con la señal de la cámara")
                    break
                
                # Procesamiento del frame
                face_locations = face_recognition.face_locations(frame)
                
                if face_locations:
                    top, right, bottom, left = face_locations[0]
                    face_encoding = face_recognition.face_encodings(frame, [face_locations[0]])[0]
                    encoding = face_encoding.tobytes()
                    
                    if mostrar_video:
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        frame = cv2.putText(frame, mensaje, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        frame_placeholder.image(frame_rgb, channels="RGB")

                # Condiciones de salida
                if encoding or (not mostrar_video and face_locations):
                    break
                
                if mostrar_video and stop_button:
                    break

        finally:
            if self.cap.isOpened():
                self.cap.release()
        
        return encoding

    def verificar_usuario(self, bd, mostrar_video=True):
        encoding = self.capturar_rostro("Verificando usuario..." if mostrar_video else "", mostrar_video)
        if encoding:
            return bd.buscar_usuario(encoding)
        return None, None, None
    
    