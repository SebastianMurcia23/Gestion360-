import pyttsx3  # Para la voz
import time      # Para manejar tiempos 
import random    # Para selección aleatoria de respuestas
import json      # Para manejar el archivo de conocimiento
import os        # Para operaciones del sistema de archivos
from pyfiglet import Figlet  # Para mostrar texto en ASCII
from termcolor import colored  # Para pintar la salida en terminal

class AsistenteVirtual:
    
    def __init__(self):

        self.motor_voz = pyttsx3.init()  # Inicializa la voz
        self.base_conocimiento = {}      # Diccionario para almacenar preguntas y respuestas
        self.cargar_conocimiento()       # Carga el conocimiento desde archivo
        
        voces = self.motor_voz.getProperty('voices')  # Obtiene las voces disponibles
        self.motor_voz.setProperty('voice', voces[0 ].id)  # Selecciona la primera voz
        self.motor_voz.setProperty('rate', 170)  # Ajusta la velocidad de habla (palabras por minuto)
        
    def cargar_conocimiento(self):
        """
        Carga la base de conocimiento desde un archivo JSON.
        Si el archivo no existe, inicia con una base vacía.
        """
        if os.path.exists('conocimiento.json'):
            with open('conocimiento.json', 'r', encoding='utf-8') as f:
                self.base_conocimiento = json.load(f)
    
    def guardar_conocimiento(self):
        """
        Guarda la base de conocimiento en un archivo JSON.
        """
        with open('conocimiento.json', 'w', encoding='utf-8') as f:
            json.dump(self.base_conocimiento, f, indent=4, ensure_ascii=False)
    
    def hablar(self, texto):

        print(colored(f"360: {texto}", 'cyan'))  # Muestra texto en cyan
        self.motor_voz.say(texto)  # Añade texto a la cola de habla
        self.motor_voz.runAndWait()  # Ejecuta la síntesis de voz
    
    def obtener_entrada(self):
    
        print(colored("\nEscribe tu pregunta: ", 'yellow'))  # Mensaje en amarillo
        return input().lower()  
    
    def procesar_pensamiento(self, consulta):
    
        # Comando para salir
        if "salir" in consulta or "terminar" in consulta:
            self.hablar("Hasta luego. Cerrando sistemas.")
            return False
        
        # Comando para aprender nuevas respuestas
        if "aprende que" in consulta:
            try:
                # Extrae pregunta y respuesta del comando
                partes = consulta.split("aprende que")
                pregunta = partes[1].split("responde")[0].strip()
                respuesta = partes[1].split("responde")[1].strip()
                
                # Guarda en la base de conocimiento
                self.base_conocimiento[pregunta] = respuesta
                self.guardar_conocimiento()
                
                # Confirma el aprendizaje
                self.hablar(f"Entendido. He aprendido que cuando preguntan '{pregunta}' debo responder '{respuesta}'")
            except Exception as e:
                # Manejo de errores en el formato
                self.hablar("No entendí el formato. Escribe: aprende que [pregunta] responde [respuesta]")
            return True
        
        # Busca coincidencias en la base de conocimiento
        for pregunta, respuesta in self.base_conocimiento.items():
            if pregunta in consulta:
                self.hablar(respuesta)
                return True
        
        # Respuestas por defecto si no encuentra coincidencias
        respuestas_predeterminadas = [
            "No estoy seguro de entender completamente su pregunta.",
            "Podría necesitar más información para responder eso adecuadamente.",
            "Mis sistemas no tienen una respuesta programada para esa consulta.",
            "¿Podría reformular la pregunta?"
        ]
        
        # Selecciona y da una respuesta aleatoria
        self.hablar(random.choice(respuestas_predeterminadas))
        return True
    
    def animacion_inicio(self):

        # Crea texto ASCII con el nombre 360
        f = Figlet(font='slant')
        print(colored(f.renderText('360'), 'cyan'))
        
        # Mensajes de inicio secuenciales
        mensajes_inicio = [
            "Inicializando sistemas...",
            "Conectando con servidores principales...",
            "Analizando entorno...",
            "Sistemas de voz activados...",
            "Listo para interactuar."
        ]
        
        # Muestra cada mensaje con un pequeño retraso
        for msg in mensajes_inicio:
            print(colored(f"> {msg}", 'blue'))
            time.sleep(1.5)
        
        # Mensaje de voz inicial
        self.hablar("Sistemas activados. ¿En qué puedo ayudar?")

        # chatbot.py (modificación)
    def procesar_pensamiento_streamlit(self, consulta):
        if "salir" in consulta or "terminar" in consulta:
            return "Hasta luego. Cerrando sistemas."
        
        if "aprende que" in consulta:
            try:
                partes = consulta.split("aprende que")
                pregunta = partes[1].split("responde")[0].strip()
                respuesta = partes[1].split("responde")[1].strip()
                
                self.base_conocimiento[pregunta] = respuesta
                self.guardar_conocimiento()
                
                return f"Entendido. He aprendido que cuando preguntan '{pregunta}' debo responder '{respuesta}'"
            except:
                return "No entendí el formato. Escribe: aprende que [pregunta] responde [respuesta]"
        
        for pregunta, respuesta in self.base_conocimiento.items():
            if pregunta in consulta:
                return respuesta
        
        respuestas_predeterminadas = [
            "No estoy seguro de entender completamente su pregunta.",
            "Podría necesitar más información para responder eso adecuadamente.",
            "Mis sistemas no tienen una respuesta programada para esa consulta.",
            "¿Podría reformular la pregunta?"
        ]
        
        return random.choice(respuestas_predeterminadas)

def main():

    asistente = AsistenteVirtual()  # Crea instancia del asistente
    asistente.animacion_inicio()  # Ejecuta animación de inicio
    
    en_ejecucion = True
    while en_ejecucion:
        consulta = asistente.obtener_entrada()  # Obtiene entrada del usuario
        if consulta:
            en_ejecucion = asistente.procesar_pensamiento_streamlit(consulta)  # Procesa la entrada


if __name__ == "__main__":
    main()
