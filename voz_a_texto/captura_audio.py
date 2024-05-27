import threading
import queue
import io
import pyaudio
import speech_recognition as sr


class AudioManager():
    def __init__(self, cola_audios, loop):
        print("AudioManager inicializado")
        self.grabacion = sr.Recognizer()
        self.cola_audios = cola_audios
        self.micro_predeterminado = self.conf_micro()
        # self.listo_para_nuevo_audio = threading.Event()
        # self.listo_para_nuevo_audio.set()
        self.pause_threshold_base = 0.5
        self.loop = loop

    @staticmethod
    def conf_micro():
        p = pyaudio.PyAudio()
        indice_predeterminado_mic = None
        try:
            indice_predeterminado = p.get_default_input_device_info()
            indice_predeterminado_mic = indice_predeterminado["index"]
        except (IOError, OSError):
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0 and indice_predeterminado_mic is None:
                    indice_predeterminado_mic = i
        if indice_predeterminado_mic is None:
            raise Exception("No se han encontrado dispositivos de entrada.")
        return indice_predeterminado_mic

    def escucha(self):
        try:
            with sr.Microphone(device_index=self.micro_predeterminado) as fuente:
                self.grabacion.adjust_for_ambient_noise(fuente, duration=0.7)
                self.grabacion.pause_threshold = self.pause_threshold_base

            self.grabacion.listen_in_background(
                fuente, callback=self.grabacion_de_fondo, phrase_time_limit=8)
        except Exception as e:
            print(f"Error al iniciar la escucha: {e}")

    def grabacion_de_fondo(self, _, datos_audio):
        audio = io.BytesIO(datos_audio.get_wav_data())
        self.loop.call_soon_threadsafe(self.cola_audios.put_nowait, audio)
