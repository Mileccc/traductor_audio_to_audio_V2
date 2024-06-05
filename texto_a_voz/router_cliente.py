import multiprocessing
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import numpy as np
import queue
import logging
import requests
import sounddevice as sd
import time
import threading


class TranscriptorAAudio(threading.Thread):
    def __init__(self, evento_terminacion_procesos, cola_respuesta, cola_audio_respuesta, evento_detener_audio, evento_audio_activo):
        self.evento_terminacion_procesos = evento_terminacion_procesos
        self.evento_audio_activo = evento_audio_activo
        self.cola_respuesta = cola_respuesta
        self.cola_audio_respuesta = cola_audio_respuesta
        self.evento_detener_audio = evento_detener_audio
        self.hablante = [
            "f1_script1_clean_segment_0.wav_es_316.wav"]
        self.lenguaje = "es"
        self.SERVER_URL = "http://80.31.215.251:8020/tts_stream"
        self.stream = None

    def run(self):
        print("Iniciando en la clase TTS")
        try:
            self.iniciar_modelo()
        except Exception as e:
            logging.error(f"Fallo en la inicialización del modelo TTS: {e}")

    def iniciar_modelo(self):
        texto = None
        while not self.evento_terminacion_procesos.is_set():
            try:
                while not self.evento_detener_audio.is_set():
                    texto = None
                    try:
                        # if self.evento_terminacion_procesos.is_set():
                        #     return
                        texto = self.cola_respuesta.get(timeout=60)
                    except queue.Empty:
                        logging.debug("cola_respuesta vacía")
                        continue
                    except Exception as e:
                        print(
                            f"Error al obtener el texto de la cola_respuesta: {e}")
                    try:
                        print(
                            f"ESTE ES EL TEXTO QUE LLEGA A 'text_a_audio': {texto}")
                        if not texto is None and not texto == "":
                            self.evento_audio_activo.set()
                            if not self.evento_detener_audio.is_set():
                                self.stream_audio(
                                    self.SERVER_URL, texto, self.hablante[0], self.lenguaje)
                            time.sleep(0.1)
                            self.evento_audio_activo.clear()
                    except Exception as e:
                        print(f"Error al transcribir texto a audio: {e}")
            finally:
                self.limpiar_cola_audio()

    def stream_audio(self, server_url, text, speaker_wav, language):
        params = {
            "text": text,
            "speaker_wav": speaker_wav,
            "language": language
        }

        try:
            with requests.get(server_url, params=params, stream=True) as response:
                response.raise_for_status()

                # Configuración de stream de sounddevice
                self.stream = sd.OutputStream(
                    samplerate=24000, channels=1, dtype='int16')
                self.stream.start()

                audio_buffer = []

                for chunk in response.iter_content(chunk_size=512):
                    if chunk:
                        audio_data = np.frombuffer(chunk, dtype=np.int16)
                        audio_buffer.append(audio_data)

                        if len(audio_buffer) > 0 and not self.evento_detener_audio.is_set():
                            combined_audio = np.concatenate(audio_buffer)
                            self.stream.write(combined_audio)
                            audio_buffer = []

                # stream.stop()
                # stream.close()

        except requests.exceptions.ChunkedEncodingError:
            print("Error: La respuesta terminó prematuramente.")

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")

    def limpiar_cola_audio(self):
        while not self.cola_audio_respuesta.empty():
            try:
                buffer = self.cola_audio_respuesta.get_nowait()
            except queue.Empty:
                break
        while not self.cola_respuesta.empty():
            try:
                buffer = self.cola_respuesta.get_nowait()
            except queue.Empty:
                break
