import cv2
import face_recognition
import numpy as np
import streamlit as st

class ReconocimientoFacial:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
    
    def capturar_rostro(self, mensaje=""):
        encoding = None
        frame_placeholder = st.empty()
        stop_button = st.button("Limpiar Captura")
        
        while self.cap.isOpened() and not stop_button:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Detectar rostros
            face_locations = face_recognition.face_locations(frame)
            
            if len(face_locations) > 0:
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Generar encoding
                face_encoding = face_recognition.face_encodings(frame, [face_locations[0]])[0]
                encoding = face_encoding.tobytes()
                frame = cv2.putText(frame, mensaje, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Convertir BGR a RGB y mostrar en Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB")
            
            if encoding:
                self.cap.release()
                return encoding
        
        self.cap.release()
        return None

    def verificar_usuario(self, bd):
        encoding = self.capturar_rostro("Verificando usuario...")
        return bd.buscar_usuario(encoding) if encoding else (None, None)