import asyncio
from faster_whisper import WhisperModel

class TranscriptorATexto:
    def __init__(self, tamanio_modelo="medium", dispositivo="cuda", tipo_calculo="float16", lenguaje="es"):
        print("Transcriptor inicializado con modelo Whisper.")
        self.tamanio_modelo = tamanio_modelo
        self.dispositivo = dispositivo
        self.tipo_calculo = tipo_calculo
        self.lenguaje = lenguaje
        self.modelo = WhisperModel(self.tamanio_modelo, device=self.dispositivo, compute_type=self.tipo_calculo)

    async def transcribe_audio(self, datos_audio, loop):
        transcripcion = await loop.run_in_executor(None, self.transcribe, datos_audio)
        return transcripcion

    def transcribe(self, datos_audio):
        segmentos_generador, info = self.modelo.transcribe(datos_audio, beam_size=5, language=self.lenguaje, vad_filter=True)
        transcripcion_completa = ' '.join([segmento.text.strip() for segmento in segmentos_generador])
        return transcripcion_completa
