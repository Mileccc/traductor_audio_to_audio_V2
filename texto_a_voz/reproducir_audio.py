import threading
import pyaudio
from queue import Empty


class Reproductor(threading.Thread):
    def __init__(self, cola_audios_final, evento_terminacion_procesos, evento_activacion_audio):
        super().__init__()
        self.cola_audios_final = cola_audios_final
        self.evento_activacion_audio = evento_activacion_audio
        self.evento_terminacion_procesos = evento_terminacion_procesos
        self.audio_activo = True

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1,
                        rate=22050, output=True)

        try:
            while not self.evento_terminacion_procesos.is_set():
                if not self.evento_activacion_audio.is_set():
                    try:
                        data_audio = self.cola_audios_final.get(timeout=60)
                        if not self.evento_activacion_audio.is_set():
                            self.reproducir_audio(data_audio, stream)
                    except Empty:
                        pass

        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def reproducir_audio(self, data_audio, stream):
        audio_bytes = data_audio.tobytes()
        stream.write(audio_bytes)
