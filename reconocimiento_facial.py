import cv2
import face_recognition
import numpy as np

class ReconocimientoFacial:
    def __init__(self):
        pass

    def capturar_rostro(self, mensaje=""):
        cap = cv2.VideoCapture(0)
        encoding = None

        while True:
            ret, frame = cap.read()
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

            cv2.putText(frame, mensaje, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow('Reconocimiento Facial', frame)

            if cv2.waitKey(1) & 0xFF == ord('q') and encoding is not None:
                break

        cap.release()
        cv2.destroyAllWindows()
        return encoding if encoding else None

    def verificar_usuario(self, bd):
        encoding = self.capturar_rostro("Verificando usuario...")
        return bd.buscar_usuario(encoding) if encoding else (None, None)