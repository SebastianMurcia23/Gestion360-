import cv2
import mediapipe as mp
import numpy as np

class ReconocimientoFacial:
    def __init__(self):
        self.deteccion_rostros = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.7)
        self.malla_facial = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False, max_num_faces=1, refine_landmarks=True, 
            min_detection_confidence=0.6, min_tracking_confidence=0.6
        )
        self.utilidades_dibujo = mp.solutions.drawing_utils
        self.especificaciones_dibujo = self.utilidades_dibujo.DrawingSpec(
            color=(64, 64, 64), thickness=1, circle_radius=0
        )

    def capturar_rostro(self, mensaje=""):
        cap = cv2.VideoCapture(0)
        rostro_extraido = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultados_rostros = self.deteccion_rostros.process(frame_rgb)
            resultados_malla = self.malla_facial.process(frame_rgb)

            # Dibujar detección de rostro y malla
            if resultados_rostros.detections:
                for deteccion in resultados_rostros.detections:
                    bboxC = deteccion.location_data.relative_bounding_box
                    h, w, _ = frame.shape
                    x, y, ancho, alto = int(bboxC.xmin * w), int(bboxC.ymin * h), int(bboxC.width * w), int(bboxC.height * h)

                    rostro_extraido = frame[y:y+alto, x:x+ancho]  # Extraer rostro detectado

            if resultados_malla.multi_face_landmarks:
                for landmarks in resultados_malla.multi_face_landmarks:
                    self.utilidades_dibujo.draw_landmarks(
                        frame, landmarks, mp.solutions.face_mesh.FACEMESH_TESSELATION, 
                        self.especificaciones_dibujo, self.especificaciones_dibujo
                    )

            cv2.putText(frame, mensaje, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow('Reconocimiento Facial', frame)

            if cv2.waitKey(1) & 0xFF == ord('q') and rostro_extraido is not None:
                break

        cap.release()
        cv2.destroyAllWindows()

        if rostro_extraido is not None:
            rostro_extraido = cv2.resize(rostro_extraido, (100, 100))  # Normalizar tamaño
            return np.array(rostro_extraido).tobytes()  
        else:
            print("No se detectó ningún rostro.")
            return None

    def registrar_usuario(self):
        print("Por favor, mire hacia la cámara para registrar su rostro y presione 'q' cuando esté listo.")
        rostro = self.capturar_rostro("Registrando rostro...")

        if rostro is not None:
            nombre = input("Ingrese su nombre: ")
            tipo_doc = input("Ingrese el tipo de documento: ")
            num_doc = input("Ingrese el número de documento: ")
            return nombre, tipo_doc, num_doc, rostro
        else:
            return None, None, None, None

    def verificar_usuario(self, bd):
        print("Mire hacia la cámara para verificar su identidad y presione 'q' cuando esté listo.")
        rostro = self.capturar_rostro("Verificando usuario...")

        if rostro is None:
            return None, None

        return bd.buscar_usuario(rostro)
