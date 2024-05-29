import threading
import pyaudio


class Reproductor(threading.Thread):
    def __init__(self, cola_audios_final, evento_terminacion_procesos):
        super().__init__()
        self.cola_audios_final = cola_audios_final
        self.evento_terminacion_procesos = evento_terminacion_procesos
        self.audio_activo = True

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1,
                        rate=22050, output=True)
        while not self.evento_terminacion_procesos.is_set():
            data_audio = self.cola_audios_final.get(timeout=60)
            if data_audio is not None and self.audio_activo:
                self.reproducir_audio(data_audio, stream)

    def reproducir_audio(self, data_audio, stream):
        audio_bytes = data_audio.tobytes()
        stream.write(audio_bytes)
