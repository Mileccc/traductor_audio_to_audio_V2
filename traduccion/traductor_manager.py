from transformers import MarianMTModel, MarianTokenizer
import threading
from queue import Empty


class Traductor(threading.Thread):
    def __init__(self, cola_traduccion, cola_traduccion_a_audio, evento_terminacion_procesos):
        """
        Inicializa el modelo y el tokenizador para la traducción es-en.
        """
        super().__init__()
        self.cola_traduccion = cola_traduccion
        self.cola_traduccion_a_audio = cola_traduccion_a_audio
        self.evento_terminacion_procesos = evento_terminacion_procesos
        self.modelo = "Helsinki-NLP/opus-mt-es-en"
        self.tokenizer = MarianTokenizer.from_pretrained(self.modelo)
        self.model = MarianMTModel.from_pretrained(self.modelo)
        self.idioma = "en"
        self.path_hablante = "es_en/2.wav"

    def run(self):
        while not self.evento_terminacion_procesos.is_set():
            try:
                dic_traduccion = self.cola_traduccion.get(timeout=60)
                if dic_traduccion["modelo"] != self.modelo and dic_traduccion["modelo"] != "":
                    self.modelo = dic_traduccion["modelo"]
                    self.cargar_modelo(self.modelo)
                if dic_traduccion["idioma"] != "":
                    self.idioma = dic_traduccion["idioma"]
                    self.path_hablante = dic_traduccion["path_hablante"]
                self.traducir(dic_traduccion["texto"],
                              self.idioma, self.path_hablante)
            except Empty:
                pass

    def traducir(self, texto, idioma, path_hablante):
        """
        Traduce un texto del español al inglés.
        """
        # Tokenización del texto
        texto_tokenizado = self.tokenizer(
            texto, return_tensors="pt", padding=True, truncation=True)

        # Generación de la traducción
        traduccion_ids = self.model.generate(**texto_tokenizado)

        # Decodificación del texto traducido
        texto_traducido = self.tokenizer.decode(
            traduccion_ids[0], skip_special_tokens=True)
        print(texto_traducido)
        self.cola_traduccion_a_audio.put(
            {"texto_traducido": texto_traducido, "idioma": idioma, "path_hablante": path_hablante})

    def cargar_modelo(self, modelo):
        self.model = modelo
        self.tokenizer = MarianTokenizer.from_pretrained(modelo)
        self.model = MarianMTModel.from_pretrained(modelo)
