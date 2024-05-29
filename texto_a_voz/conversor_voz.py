import pyaudio
import os
import time
import numpy as np
import asyncio
import torch
from TTS.api import TTS
import threading
from queue import Empty


class TranscriptorAAudio(threading.Thread):
    def __init__(self, evento_terminacion_procesos, cola_traduccion_a_audio, cola_audios_final):
        super().__init__()
        self.cola_audios_final = cola_audios_final
        self.evento_terminacion_procesos = evento_terminacion_procesos
        self.cola_traduccion_a_audio = cola_traduccion_a_audio
        self.nombre_modelo = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.audio_hablante = "D:\ProyectoTraductor\Traductor_en_tiempo_real\speakers\es_es\mi_voz.wav"
        self.lenguaje = "es"
        self.tts = None
        self.dispositivo = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.audio_activo = True

    def run(self):
        print(f"Inicializando modelo en {self.dispositivo}...")
        self.tts = TTS(model_name=self.nombre_modelo)
        self.tts.to(self.dispositivo)
        while not self.evento_terminacion_procesos.is_set():
            try:
                datos = self.cola_traduccion_a_audio.get(timeout=60)
                if self.lenguaje != datos["idioma"]:
                    self.lenguaje = datos["idioma"]
                    self.audio_hablante = f"speakers/{datos['path_hablante']}"

                self.texto_a_audio(datos["texto_traducido"])
            except Empty:
                pass

    def texto_a_audio(self, texto):
        audio_data = self.tts.tts(
            text=texto, speaker_wav=self.audio_hablante, language=self.lenguaje)

        audio_array = np.array(audio_data, dtype=np.float32)
        audio_array_int16 = np.int16(audio_array * 32767)
        self.cola_audios_final.put(audio_array_int16)
        print(f"Audio transcrito guardado correctamente")
