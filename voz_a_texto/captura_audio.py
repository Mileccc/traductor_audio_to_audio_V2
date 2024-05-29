import threading
import queue
import io
import pyaudio
import speech_recognition as sr
import logging
import multiprocessing


class AudioManager(threading.Thread):
    def __init__(self, evento_terminacion_procesos, cola_audios_micro) -> None:
        super().__init__(daemon=True)
        self.grabacion: sr.Recognizer = sr.Recognizer()
        self.p: pyaudio.PyAudio = pyaudio.PyAudio()
        self.micro_predeterminado: int = self.localizar_micro()
        self.evento_terminacion_procesos: multiprocessing.Event = evento_terminacion_procesos
        self.cola_audios_micro: queue.Queue = cola_audios_micro

    def run(self):
        try:
            self.iniciar_escucha_continua()
        except Exception as e:
            logging.error("Error al reproducir stream: %s", e)
        finally:
            self.p.terminate()
            logging.info("AudioManager limpio y terminado correctamente.")

    def iniciar_escucha_continua(self) -> None:
        try:
            with sr.Microphone(device_index=self.micro_predeterminado) as source:
                self.grabacion.adjust_for_ambient_noise(source, duration=1)
                self.grabacion.dynamic_energy_threshold = False
                self.grabacion.pause_threshold = 0.5
                self.grabacion.energy_threshold = 300
                while not self.evento_terminacion_procesos.is_set():
                    print("Escuchando...")
                    audio: object = self.grabacion.listen(source)
                    logging.debug("Terminada la grabacion")
                    audio_data: io.BytesIO = io.BytesIO(audio.get_wav_data())
                    logging.debug("Datos tranformados")
                    try:
                        self.cola_audios_micro.put_nowait(audio_data)
                        logging.debug("Dato anadido a la cola")
                    except queue.Full:
                        logging.warning(
                            "La cola_audios_micro está llena; el dato no fue añadido.")
        except Exception as e:
            logging.error("Error al iniciar escucha continua: %s", e)

    def localizar_micro(self) -> int:
        try:
            indice_predeterminado: dict = self.p.get_default_input_device_info()
            logging.debug("Índice predeterminado del micrófono: %s",
                          indice_predeterminado["index"])
            return int(indice_predeterminado["index"])
        except Exception as e:
            logging.error(
                "Error al obtener el dispositivo predeterminado: %s", e)
            return self.buscar_alternativa()

    def buscar_alternativa(self) -> int:
        dispositivos_revisados: int = 0
        try:
            for i in range(self.p.get_device_count()):
                info: dict = self.p.get_device_info_by_index(i)
                dispositivos_revisados += 1
                if info['maxInputChannels'] > 0:
                    logging.info("Usando micrófono alternativo: %s", i)
                    return i
            logging.warning("Se revisaron %d dispositivos y no se encontró un micrófono válido.",
                            dispositivos_revisados)
        except Exception as e:
            logging.error("Error al buscar un micrófono alternativo: %s", e)
