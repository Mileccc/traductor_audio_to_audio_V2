import threading
from queue import Empty
import numpy as np
import requests
import sounddevice as sd
import time


class TranscriptorAAudio(threading.Thread):
    def __init__(self, evento_terminacion_procesos, cola_traduccion_a_audio, evento_activacion_audio):
        super().__init__()
        self.evento_activacion_audio = evento_activacion_audio
        self.evento_terminacion_procesos = evento_terminacion_procesos
        self.cola_traduccion_a_audio = cola_traduccion_a_audio
        self.audio_hablante = ["es_es_m4.wav"]
        self.lenguaje = "es"
        self.audio_activo = True
        self.SERVER_URL = "http://80.31.215.251:8080/tts_stream"
        self.stream = None

    def run(self):
        while not self.evento_terminacion_procesos.is_set():
            try:
                while not self.evento_activacion_audio.is_set():
                    try:
                        datos = self.cola_traduccion_a_audio.get(timeout=60)
                        print(
                            f"ESTE ES EL TEXTO QUE LLEGA A 'text_a_audio': {datos}")
                        if self.lenguaje != datos["idioma"]:
                            self.lenguaje = datos["idioma"]
                            self.audio_hablante = datos['path_hablante']

                        texto = datos["texto_traducido"]
                        if texto and not texto == "":
                            print(
                                f"Aqui llegamos bien?\nTexto:{type(texto)}\nHablante:{type(self.audio_hablante)}\nLenguaje:{type(self.lenguaje)}")

                            self.texto_a_audio(texto)
                    except Empty:
                        pass
            finally:
                self.limpiar_cola_audio()

    def texto_a_audio(self, texto):
        self.stream_audio(self.SERVER_URL, texto,
                          self.audio_hablante[0], self.lenguaje)
        time.sleep(0.1)

    def stream_audio(self, server_url, text, speaker_wav, language):
        params = {
            "text": text,
            "speaker_wav": speaker_wav,
            "language": language
        }

        try:
            with requests.get(server_url, params=params, stream=True) as response:
                print(f"Que tiene response: {response}")
                response.raise_for_status()

                self.iniciar_stream()

                audio_buffer = []

                for chunk in response.iter_content(chunk_size=512):
                    if chunk:
                        audio_data = np.frombuffer(chunk, dtype=np.int16)
                        audio_buffer.append(audio_data)

                        if len(audio_buffer) > 0 and not self.evento_activacion_audio.is_set():
                            combined_audio = np.concatenate(audio_buffer)
                            self.stream.write(combined_audio)
                            audio_buffer = []
        except requests.exceptions.ChunkedEncodingError:
            print("Error: La respuesta terminó prematuramente.")

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
        finally:
            self.cerrar_stream()

    def iniciar_stream(self):
        if self.stream is not None:
            self.cerrar_stream()
        self.stream = sd.OutputStream(
            samplerate=24000, channels=1, dtype='int16')
        self.stream.start()

    def cerrar_stream(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    def limpiar_cola_audio(self):
        while not self.cola_traduccion_a_audio.empty():
            try:
                buffer = self.cola_traduccion_a_audio.get_nowait()
            except Empty:
                break
