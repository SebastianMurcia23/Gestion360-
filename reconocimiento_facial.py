import cv2
import face_recognition
import numpy as np
import streamlit as st

class ReconocimientoFacial:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
    
    def capturar_rostro(self, mensaje="", mostrar_video=True):
        encoding = None
        frame_placeholder = st.empty() if mostrar_video else None
        stop_button = st.button("Limpiar Captura") if mostrar_video else None
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Procesamiento de frame aunque no se muestre
            face_locations = face_recognition.face_locations(frame)
            
            if len(face_locations) > 0:
                top, right, bottom, left = face_locations[0]
                face_encoding = face_recognition.face_encodings(frame, [face_locations[0]])[0]
                encoding = face_encoding.tobytes()
                
                if mostrar_video:
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    frame = cv2.putText(frame, mensaje, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(frame_rgb, channels="RGB")

            # Condición de salida silenciosa cuando no se muestra video
            if encoding or (not mostrar_video and face_locations):
                self.cap.release()
                return encoding
            
            # Condición de salida con botón visible
            if mostrar_video and stop_button:
                self.cap.release()
                return None

        self.cap.release()
        return None

    def verificar_usuario(self, bd, mostrar_video=True):
        encoding = self.capturar_rostro("Verificando usuario..." if mostrar_video else "", mostrar_video)
        if encoding:
            nombre, num_doc, rol = bd.buscar_usuario(encoding)
            return nombre, num_doc, rol
        return None, None, None