import asyncio
from faster_whisper import WhisperModel
import logging
import queue
import queue
import io
import multiprocessing


class TranscriptorATexto():
    def __init__(self, cola_audios_micro, cola_verificacion, evento_terminacion_procesos):
        self.cola_audios_micro: queue.Queue = cola_audios_micro
        self.cola_verificacion: queue.Queue = cola_verificacion
        self.evento_terminacion_procesos: multiprocessing.Event = evento_terminacion_procesos
        self.whisper_modelo: WhisperModel = None

    async def run(self):
        print("Iniciando en la clase TranscriptorSTT")
        try:
            self.whisper_modelo = WhisperModel(
                "medium", device="cuda", compute_type="float16")
        except Exception as e:
            logging.error(
                f"Fallo en la inicialización del modelo Whisper: {e}")
        print("Whisper iniciado correctamente.")
        await self.loop_transcripcion()

    async def loop_transcripcion(self,):
        while not self.evento_terminacion_procesos.is_set():
            try:
                try:
                    await asyncio.sleep(0.01)
                    datos_audio: io.BytesIO = self.cola_audios_micro.get(
                        timeout=60)
                except queue.Empty:
                    logging.debug("Cola_audios_micro vacía")
                    continue
                if datos_audio:
                    segments, info = self.whisper_modelo.transcribe(
                        datos_audio, beam_size=5, language="es")
                    texto: str = " ".join(segment.text for segment in segments)
                    logging.debug(
                        f"Transcripción inicial en TranscriptorSTT: {texto}")
                    try:
                        await asyncio.sleep(0.01)
                        # print(
                        #     f"Transcripción inicial en TranscriptorSTT: {texto}")
                        self.cola_verificacion.put_nowait(texto)
                    except queue.Full:
                        logging.warning(
                            "La cola_verificacion está llena; el dato no fue añadido.")
            except Exception as e:
                logging.error(f"Error al transcribir audio: {e}")
