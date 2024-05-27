import pyaudio
import os
import time
import numpy as np
import asyncio
import torch
from TTS.api import TTS
import sys
sys.path.append('D:\\ProyectoTraductor\\Traductor_en_tiempo_real\\TTS')


class TranscriptorAAudio:
    def __init__(self):
        self.nombre_modelo = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.audio_hablante = "D:\ProyectoTraductor\Traductor_en_tiempo_real\speakers\es_es\mi_voz.wav"
        self.lenguaje = "es"
        self.tts = None
        self.dispositivo = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.cola_audios_final = asyncio.Queue()
        # Modificado para usar asyncio.Queue
        self.MAX_CONCURRENT_TTS = 2
        self.semaforo = asyncio.Semaphore(self.MAX_CONCURRENT_TTS)
        self.audio_activo = True

    def iniciar_modelo(self):
        print(f"Inicializando modelo en {self.dispositivo}...")
        self.tts = TTS(model_name=self.nombre_modelo)
        self.tts.to(self.dispositivo)

    async def texto_a_audio(self, texto):
        inicio = time.time()
        ruta_absoluta = os.path.abspath(self.audio_hablante)

        if not os.path.exists(ruta_absoluta):
            print(f"El archivo de audio {ruta_absoluta} no existe.")
            return

        try:
            async with self.semaforo:
                print(f"Convirtiendo texto a voz: {texto}")
                # Ejecutar la conversión de TTS en un executor para no bloquear el event loop
                audio_data = await asyncio.get_running_loop().run_in_executor(
                    None, lambda: self.tts.tts(text=texto, speaker_wav=self.audio_hablante, language=self.lenguaje))

                fin = time.time()
                print(f"Conversión completada en {fin - inicio:.2f} segundos.")

                audio_array = np.array(audio_data, dtype=np.float32)
                audio_array_int16 = np.int16(audio_array * 32767)
                await self.cola_audios_final.put(audio_array_int16)
        except Exception as e:
            print(f"Error al convertir texto a voz: {e}")

    async def reproducir_audios(self):
        print("Iniciando la reproducción de audios...")
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1,
                        rate=22050, output=True)

        try:
            while True:
                audio_data = await self.cola_audios_final.get()
                if audio_data is not None and self.audio_activo:
                    print("Reproduciendo audio...")
                    await self.play_audio(stream, audio_data)
                elif not self.audio_activo:
                    print("Audio pausado, saltando reproducción.")
        except asyncio.CancelledError:
            print("Tarea de reproducción de audios cancelada.")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    async def play_audio(self, stream, audio_data):
        await asyncio.get_running_loop().run_in_executor(None, self._blocking_play_audio, stream, audio_data)

    def _blocking_play_audio(self, stream, audio_data):
        audio_bytes = audio_data.tobytes()
        stream.write(audio_bytes)

    def set_hablante(self, audio_hablante, lenguaje):
        self.audio_hablante = audio_hablante
        self.lenguaje = lenguaje

    def pausar_audio(self):
        self.audio_activo = False

    def reanudar_audio(self):
        self.audio_activo = True
